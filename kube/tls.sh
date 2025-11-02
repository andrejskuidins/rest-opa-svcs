#!/bin/bash
set -e

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
