#!/bin/bash
# create_vm.sh
# Creates and configures the SUSE Micro OS VM in OrbStack

set -e

# Configuration variables
VM_NAME="k3s-master"
CPU_CORES=2
MEMORY_GB=4
DISK_GB=20
IMAGE_PATH="$(pwd)/resources/images/suse-microos.qcow2"

echo "Creating SUSE Micro OS VM in OrbStack..."

# Check if OrbStack CLI is available
if ! command -v orb &> /dev/null; then
    echo "Error: OrbStack CLI not found. Please install OrbStack first."
    exit 1
fi

# Check if the VM already exists
if orb vm list | grep -q "$VM_NAME"; then
    echo "VM '$VM_NAME' already exists. Stopping and removing it..."
    orb vm stop "$VM_NAME" || true
    orb vm rm "$VM_NAME" || true
fi

# Check if the image exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: SUSE Micro OS image not found at $IMAGE_PATH"
    echo "Please run download_resources.sh first."
    exit 1
fi

# Create the VM
echo "Creating VM '$VM_NAME' with $CPU_CORES cores, ${MEMORY_GB}GB memory, and ${DISK_GB}GB disk..."
orb vm create \
    --name "$VM_NAME" \
    --cpu "$CPU_CORES" \
    --memory "${MEMORY_GB}GB" \
    --disk "${DISK_GB}GB" \
    --image "$IMAGE_PATH"

# Start the VM
echo "Starting VM '$VM_NAME'..."
orb vm start "$VM_NAME"

# Wait for VM to boot
echo "Waiting for VM to boot..."
sleep 10

# Get VM IP address
VM_IP=$(orb vm ip "$VM_NAME")
echo "VM IP address: $VM_IP"

# Add VM IP to /etc/hosts for easier access
if ! grep -q "$VM_NAME.local" /etc/hosts; then
    echo "Adding VM IP to /etc/hosts..."
    echo "$VM_IP $VM_NAME.local" | sudo tee -a /etc/hosts > /dev/null
fi

# Save VM IP to a file for other scripts to use
echo "$VM_IP" > "$(dirname "$0")/../resources/vm_ip.txt"

# Wait for SSH to be available
echo "Waiting for SSH to be available..."
for i in {1..30}; do
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@"$VM_IP" echo "SSH is available"; then
        break
    fi
    echo "Waiting for SSH... ($i/30)"
    sleep 5
    if [ $i -eq 30 ]; then
        echo "Error: SSH not available after 150 seconds. Please check the VM status."
        exit 1
    fi
done

# Configure VM
echo "Configuring VM..."
ssh -o StrictHostKeyChecking=no root@"$VM_IP" << EOF
# Set hostname
hostnamectl set-hostname $VM_NAME

# Update system
zypper refresh
zypper update -y

# Install required packages
zypper install -y curl tar gzip

# Configure firewall to allow k3s
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=6443/tcp
    firewall-cmd --permanent --add-port=8472/udp
    firewall-cmd --permanent --add-port=10250/tcp
    firewall-cmd --reload
fi

# Disable swap
swapoff -a
sed -i '/swap/d' /etc/fstab

# Enable IP forwarding
echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/k8s.conf
sysctl --system
EOF

echo "VM '$VM_NAME' created and configured successfully!"
echo "VM IP address: $VM_IP"
echo "You can SSH into the VM using: ssh root@$VM_IP"