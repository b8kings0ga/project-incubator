#!/bin/bash
# install_k3s.sh
# Installs and configures k3s on the SUSE Micro OS VM

set -e

# Get VM IP from file
VM_IP_FILE="$(dirname "$0")/../resources/vm_ip.txt"
if [ ! -f "$VM_IP_FILE" ]; then
    echo "Error: VM IP file not found. Please run create_vm.sh first."
    exit 1
fi
VM_IP=$(cat "$VM_IP_FILE")

# Check if VM is reachable
if ! ping -c 1 "$VM_IP" &> /dev/null; then
    echo "Error: VM at $VM_IP is not reachable. Please check if the VM is running."
    exit 1
fi

# Paths to resources
K3S_BINARY="$(pwd)/resources/binaries/k3s"
K3S_IMAGES="$(pwd)/resources/images/k3s-airgap-images.tar.gz"
K3S_INSTALL_SCRIPT="$(pwd)/resources/binaries/k3s-install.sh"
K3S_CONFIG="$(pwd)/resources/configs/k3s-config.yaml"

# Check if resources exist
for resource in "$K3S_BINARY" "$K3S_IMAGES" "$K3S_INSTALL_SCRIPT" "$K3S_CONFIG"; do
    if [ ! -f "$resource" ]; then
        echo "Error: Resource $resource not found. Please run download_resources.sh first."
        exit 1
    fi
done

echo "Installing k3s on VM at $VM_IP..."

# Create directories on VM
echo "Creating directories on VM..."
ssh -o StrictHostKeyChecking=no root@"$VM_IP" "mkdir -p /var/lib/rancher/k3s/agent/images /etc/rancher/k3s"

# Copy k3s binary to VM
echo "Copying k3s binary to VM..."
scp -o StrictHostKeyChecking=no "$K3S_BINARY" root@"$VM_IP":/usr/local/bin/k3s
ssh -o StrictHostKeyChecking=no root@"$VM_IP" "chmod +x /usr/local/bin/k3s"

# Copy k3s airgap images to VM
echo "Copying k3s airgap images to VM..."
scp -o StrictHostKeyChecking=no "$K3S_IMAGES" root@"$VM_IP":/var/lib/rancher/k3s/agent/images/

# Copy k3s config to VM
echo "Copying k3s config to VM..."
scp -o StrictHostKeyChecking=no "$K3S_CONFIG" root@"$VM_IP":/etc/rancher/k3s/config.yaml

# Install k3s on VM
echo "Installing k3s on VM..."
ssh -o StrictHostKeyChecking=no root@"$VM_IP" << EOF
# Set environment variables for airgap installation
export INSTALL_K3S_SKIP_DOWNLOAD=true
export INSTALL_K3S_EXEC="server"

# Run k3s install script
curl -sfL https://get.k3s.io | sh -

# Wait for k3s to start
echo "Waiting for k3s to start..."
sleep 10

# Check k3s status
systemctl status k3s

# Get node status
kubectl get nodes
EOF

echo "k3s installed and configured successfully on VM at $VM_IP!"