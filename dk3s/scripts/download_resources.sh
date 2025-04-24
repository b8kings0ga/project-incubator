#!/bin/bash
# download_resources.sh
# Downloads all required resources locally for k3s deployment on SUSE Micro OS

set -e

# Create directories for downloaded resources
mkdir -p resources/images
mkdir -p resources/binaries
mkdir -p resources/configs

echo "Starting download of required resources..."

# Download SUSE Micro OS image
echo "Downloading SUSE Micro OS image..."
curl -L -o resources/images/suse-microos.qcow2 https://download.opensuse.org/tumbleweed/appliances/openSUSE-MicroOS.x86_64-ContainerHost-kvm-and-xen.qcow2

# Download k3s binary
echo "Downloading k3s binary..."
curl -L -o resources/binaries/k3s https://github.com/k3s-io/k3s/releases/download/v1.28.6%2Bk3s2/k3s
chmod +x resources/binaries/k3s

# Download k3s images for air-gapped installation
echo "Downloading k3s airgap images..."
curl -L -o resources/images/k3s-airgap-images.tar.gz https://github.com/k3s-io/k3s/releases/download/v1.28.6%2Bk3s2/k3s-airgap-images-amd64.tar.gz

# Download k3s install script
echo "Downloading k3s install script..."
curl -L -o resources/binaries/k3s-install.sh https://get.k3s.io
chmod +x resources/binaries/k3s-install.sh

# Create a basic configuration for k3s
cat > resources/configs/k3s-config.yaml << EOF
# k3s configuration
write-kubeconfig-mode: "0644"
tls-san:
  - "k3s.local"
disable:
  - traefik
  - servicelb
  - metrics-server
EOF

echo "All resources downloaded successfully!"
echo "Resources are available in the 'resources' directory."