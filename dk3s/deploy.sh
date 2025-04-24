#!/bin/bash
# deploy.sh
# Main script to deploy k3s on SUSE Micro OS with OrbStack

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==================================================================="
echo "Deploying k3s on SUSE Micro OS with OrbStack"
echo "==================================================================="

# Make all scripts executable
chmod +x "$SCRIPT_DIR/scripts/"*.sh

# Step 1: Download resources
echo -e "\n\n=== Step 1: Downloading resources ===\n"
"$SCRIPT_DIR/scripts/download_resources.sh"

# Step 2: Create VM
echo -e "\n\n=== Step 2: Creating VM ===\n"
"$SCRIPT_DIR/scripts/create_vm.sh"

# Step 3: Install k3s
echo -e "\n\n=== Step 3: Installing k3s ===\n"
"$SCRIPT_DIR/scripts/install_k3s.sh"

# Step 4: Setup access
echo -e "\n\n=== Step 4: Setting up access ===\n"
"$SCRIPT_DIR/scripts/setup_access.sh"

# Step 5: Verify cluster
echo -e "\n\n=== Step 5: Verifying cluster ===\n"
"$SCRIPT_DIR/scripts/verify_cluster.sh"

echo -e "\n\n==================================================================="
echo "k3s on SUSE Micro OS with OrbStack deployed successfully!"
echo "==================================================================="
echo "You can now use kubectl to interact with your k3s cluster."
echo "To access the VM: ssh root@\$(cat $SCRIPT_DIR/resources/vm_ip.txt)"
echo "==================================================================="