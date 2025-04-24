#!/bin/bash
# setup_access.sh
# Configures access to the k3s cluster from the host machine

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

echo "Setting up access to k3s cluster on VM at $VM_IP..."

# Create directory for kubeconfig
mkdir -p ~/.kube
mkdir -p "$(dirname "$0")/../resources/configs"

# Copy kubeconfig from VM
echo "Copying kubeconfig from VM..."
scp -o StrictHostKeyChecking=no root@"$VM_IP":/etc/rancher/k3s/k3s.yaml "$(dirname "$0")/../resources/configs/k3s.yaml"

# Update server address in kubeconfig
echo "Updating server address in kubeconfig..."
sed -i '' "s/127.0.0.1/$VM_IP/g" "$(dirname "$0")/../resources/configs/k3s.yaml"

# Create a merged kubeconfig
echo "Creating merged kubeconfig..."
KUBECONFIG=~/.kube/config:"$(dirname "$0")/../resources/configs/k3s.yaml" kubectl config view --flatten > /tmp/merged-config
mv /tmp/merged-config ~/.kube/config
chmod 600 ~/.kube/config

# Set current context to k3s
echo "Setting current context to k3s..."
kubectl config use-context default

# Verify connection to cluster
echo "Verifying connection to cluster..."
kubectl cluster-info
kubectl get nodes

echo "Access to k3s cluster configured successfully!"
echo "You can now use kubectl to interact with your k3s cluster."