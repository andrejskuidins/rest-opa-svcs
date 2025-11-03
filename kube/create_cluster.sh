#!/bin/bash
set -e  # Exit on any error

cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 8000
    hostPort: 8000
    protocol: TCP
  - containerPort: 8181
    hostPort: 8181
    protocol: TCP
EOF

echo "Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml

echo "Cluster created successfully!"

echo ###############################
echo "Creating TLS"

CERT_DIR="$HOME/.ssh/flask"
mkdir -p "$CERT_DIR"

# Generate self-signed cert
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$CERT_DIR/tls.key" -out "$CERT_DIR/tls.crt" \
  -subj "/CN=localhost/O=localhost"

# Delete existing secret if it exists
kubectl delete secret flask-tls --ignore-not-found

# Create Kubernetes secret
kubectl create secret tls flask-tls \
  --cert="$CERT_DIR/tls.crt" \
  --key="$CERT_DIR/tls.key"

echo "TLS secret created successfully!"