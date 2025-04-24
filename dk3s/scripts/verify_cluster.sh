#!/bin/bash
# verify_cluster.sh
# Verifies the k3s cluster is working correctly

set -e

echo "Verifying k3s cluster functionality..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if we can connect to the cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to the k3s cluster. Please run setup_access.sh first."
    exit 1
fi

# Check node status
echo "Checking node status..."
kubectl get nodes -o wide

# Check pod status
echo "Checking pod status..."
kubectl get pods --all-namespaces

# Create a test namespace
echo "Creating test namespace..."
kubectl create namespace test

# Deploy a test application
echo "Deploying test application..."
cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:stable
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
  namespace: test
spec:
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: nginx
  type: ClusterIP
EOF

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl -n test rollout status deployment/nginx --timeout=120s

# Check if pods are running
echo "Checking if pods are running..."
kubectl -n test get pods

# Create a port-forward to test the application
echo "Creating port-forward to test the application..."
kubectl -n test port-forward svc/nginx 8080:80 &
PORT_FORWARD_PID=$!

# Wait for port-forward to be ready
sleep 5

# Test the application
echo "Testing the application..."
if curl -s http://localhost:8080 | grep -q "Welcome to nginx"; then
    echo "Test application is working correctly!"
else
    echo "Error: Test application is not working correctly."
    kill $PORT_FORWARD_PID
    exit 1
fi

# Clean up
kill $PORT_FORWARD_PID
kubectl delete namespace test

echo "k3s cluster verification completed successfully!"
echo "Your k3s cluster is working correctly."