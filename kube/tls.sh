#!/bin/bash
set -e

mkdir -p ~/.ssh/flask

# Generate self-signed cert
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ~/.ssh/flask/tls.key -out ~/.ssh/flask/tls.crt \
  -subj "/CN=localhost/O=localhost"

# Create Kubernetes secret
kubectl create secret tls flask-tls \
  --cert=~/.ssh/flask/tls.crt \
  --key=~/.ssh/flask/tls.key
