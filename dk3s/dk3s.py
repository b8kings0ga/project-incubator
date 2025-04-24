#!/usr/bin/env python3
"""
dk3s - CLI tool for managing k3s on SUSE Micro OS with OrbStack
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="CLI tool for managing k3s on SUSE Micro OS with OrbStack")
console = Console()

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.absolute()


def run_command(command: str, cwd: Optional[Path] = None) -> int:
    """Run a shell command and return the exit code."""
    try:
        return subprocess.run(command, shell=True, check=True, cwd=cwd).returncode
    except subprocess.CalledProcessError as e:
        return e.returncode


def get_vm_ip() -> Optional[str]:
    """Get the VM IP address from the resources/vm_ip.txt file."""
    ip_file = SCRIPT_DIR / "resources" / "vm_ip.txt"
    if ip_file.exists():
        return ip_file.read_text().strip()
    return None


@app.command()
def deploy():
    """Deploy k3s on SUSE Micro OS with OrbStack."""
    console.print(Panel.fit("Deploying k3s on SUSE Micro OS with OrbStack", title="dk3s"))
    
    deploy_script = SCRIPT_DIR / "deploy.sh"
    if not deploy_script.exists():
        console.print(f"[bold red]Error:[/] Deploy script not found at {deploy_script}")
        return 1
    
    # Make the script executable
    os.chmod(deploy_script, 0o755)
    
    # Run the deploy script
    return run_command(str(deploy_script), cwd=SCRIPT_DIR)


@app.command()
def status():
    """Check the status of the k3s cluster."""
    console.print(Panel.fit("k3s Cluster Status", title="dk3s"))
    
    # Check if VM is running
    vm_ip = get_vm_ip()
    if not vm_ip:
        console.print("[bold red]Error:[/] VM IP not found. Has the cluster been deployed?")
        return 1
    
    # Check if VM is reachable
    ping_result = run_command(f"ping -c 1 {vm_ip} > /dev/null 2>&1")
    if ping_result != 0:
        console.print(f"[bold red]Error:[/] VM at {vm_ip} is not reachable.")
        return 1
    
    # Check k3s status on VM
    console.print("\n[bold]k3s Service Status:[/]")
    run_command(f"ssh -o StrictHostKeyChecking=no root@{vm_ip} 'systemctl status k3s | head -n 20'")
    
    # Check node status
    console.print("\n[bold]Node Status:[/]")
    run_command("kubectl get nodes -o wide")
    
    # Check pod status
    console.print("\n[bold]Pod Status:[/]")
    run_command("kubectl get pods --all-namespaces")
    
    return 0


@app.command()
def clean():
    """Clean up resources (VM, downloaded files, etc.)."""
    console.print(Panel.fit("Cleaning up resources", title="dk3s"))
    
    # Ask for confirmation
    confirm = inquirer.confirm(
        message="This will delete the VM and all downloaded resources. Are you sure?",
        default=False,
    ).execute()
    
    if not confirm:
        console.print("Cleanup cancelled.")
        return 0
    
    # Get VM IP
    vm_ip = get_vm_ip()
    if vm_ip:
        # Stop and remove VM
        console.print("Stopping and removing VM...")
        run_command("orb vm stop k3s-master || true")
        run_command("orb vm rm k3s-master || true")
    
    # Remove resources directory
    resources_dir = SCRIPT_DIR / "resources"
    if resources_dir.exists():
        console.print("Removing downloaded resources...")
        run_command(f"rm -rf {resources_dir}")
    
    console.print("[bold green]Cleanup completed successfully![/]")
    return 0


@app.command()
def ssh():
    """SSH into the k3s VM."""
    vm_ip = get_vm_ip()
    if not vm_ip:
        console.print("[bold red]Error:[/] VM IP not found. Has the cluster been deployed?")
        return 1
    
    console.print(f"Connecting to VM at {vm_ip}...")
    return run_command(f"ssh -o StrictHostKeyChecking=no root@{vm_ip}")


@app.command()
def dashboard():
    """Launch the Kubernetes dashboard."""
    console.print(Panel.fit("Launching Kubernetes Dashboard", title="dk3s"))
    
    # Check if dashboard is installed
    dashboard_check = subprocess.run(
        "kubectl get deployment kubernetes-dashboard -n kubernetes-dashboard 2>/dev/null",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    if dashboard_check.returncode != 0:
        # Ask if user wants to install dashboard
        install = inquirer.confirm(
            message="Kubernetes Dashboard is not installed. Would you like to install it?",
            default=True,
        ).execute()
        
        if not install:
            console.print("Dashboard launch cancelled.")
            return 0
        
        # Install dashboard
        console.print("Installing Kubernetes Dashboard...")
        run_command("kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml")
        
        # Create admin user
        console.print("Creating dashboard admin user...")
        admin_manifest = """
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
"""
        admin_file = SCRIPT_DIR / "resources" / "dashboard-admin.yaml"
        admin_file.parent.mkdir(parents=True, exist_ok=True)
        admin_file.write_text(admin_manifest)
        run_command(f"kubectl apply -f {admin_file}")
    
    # Get token
    console.print("Getting dashboard token...")
    token_cmd = "kubectl -n kubernetes-dashboard create token admin-user"
    token_process = subprocess.run(
        token_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    token = token_process.stdout.strip()
    
    # Start proxy
    console.print("Starting kubectl proxy...")
    proxy_process = subprocess.Popen(
        "kubectl proxy",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Print access instructions
    console.print("\n[bold green]Kubernetes Dashboard is running![/]")
    console.print("\nAccess the dashboard at: [bold blue]http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/[/]")
    console.print("\nUse the following token to log in:")
    console.print(f"[bold yellow]{token}[/]")
    console.print("\nPress Ctrl+C to stop the dashboard when you're done.")
    
    try:
        # Wait for user to press Ctrl+C
        proxy_process.wait()
    except KeyboardInterrupt:
        console.print("\nStopping dashboard...")
        proxy_process.terminate()
    
    return 0


@app.command()
def menu():
    """Show an interactive menu of available commands."""
    choices = [
        Choice(value="deploy", name="Deploy k3s cluster"),
        Choice(value="status", name="Check cluster status"),
        Choice(value="ssh", name="SSH into the VM"),
        Choice(value="dashboard", name="Launch Kubernetes dashboard"),
        Choice(value="clean", name="Clean up resources"),
        Choice(value="exit", name="Exit"),
    ]
    
    while True:
        console.print(Panel.fit("k3s on SUSE Micro OS with OrbStack", title="dk3s"))
        
        action = inquirer.select(
            message="Select an action:",
            choices=choices,
            default="deploy",
        ).execute()
        
        if action == "exit":
            break
        
        # Call the appropriate function based on the selected action
        if action == "deploy":
            deploy()
        elif action == "status":
            status()
        elif action == "ssh":
            ssh()
        elif action == "dashboard":
            dashboard()
        elif action == "clean":
            clean()
        
        # Pause before showing the menu again
        inquirer.text(message="Press Enter to continue...").execute()
        console.clear()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # If no arguments are provided, show the interactive menu
        menu()
    else:
        # Otherwise, run the CLI app
        app()