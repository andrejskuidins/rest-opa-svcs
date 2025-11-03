# Flask-OPA Userbase Authorization API

A user database REST API built with **Flask** and **Open Policy Agent (OPA)**, containerized with **Docker** and orchestrated with **Kubernetes**.

## Overview

This project demonstrates a complete user databse where:

- **Flask** provides a REST API for user management (CRUD operations)
- **OPA** (Open Policy Agent) enforces authorization policies written in **Rego**
- **Kubernetes** orchestrates both services with service discovery and ingress routing
- **Docker** containers package both the Flask application and OPA policy engine

The authorization system implements role-based access control with granular policies for different HTTP methods and API endpoints.

## Architecture

```
Client Request
    ↓
Flask API (Port 8000)
    ↓
OPA Policy Engine (Port 8181)
    ↓
Authorization Decision
    ↓
Response to Client
```

### Components

**Flask Application** (`flask/`)
- User management REST API

**OPA Policy Engine** (`kube/configmap_opa.yml`)
- Policy-as-code using Rego language

**Kubernetes Resources** (`kube/dep_opa.yml`)
- Kind cluster creation script with port mappings

## API Endpoints

All endpoints require a `user` query parameter for identification. Certain operations require a `role` parameter.

| Method | Endpoint | Authentication | Required Role | Description |
|--------|----------|---|---|---|
| `GET` | `/api/users` | Yes (user param) | None | List all users |
| `GET` | `/api/users/<name>` | Yes (user param) | None | Get specific user |
| `POST` | `/api/users` | Yes | admin | Create new user |
| `PUT` | `/api/users/<name>` | Yes | admin | Update user |
| `DELETE` | `/api/users/<name>` | Yes | admin | Delete user |

### Example Requests

```bash
# List all users (any authenticated user)
curl "http://localhost:8000/api/users?user=alice"

# Create new user (admin only)
curl -X POST "http://localhost:8000/api/users?user=admin&role=admin" \
  -H "Content-Type: application/json" \
  -d '{"name": "bob", "email": "bob@example.com"}'

# Update user (admin only)
curl -X PUT "http://localhost:8000/api/users/alice?user=admin&role=admin" \
  -H "Content-Type: application/json" \
  -d '{"name": "alice", "email": "newemail@example.com"}'

# Delete user (admin only)
curl -X DELETE "http://localhost:8000/api/users/bob?user=admin&role=admin"
```

## Authorization Policies

The OPA Rego policies (`docker/opa/rego/user.rego`) enforce the following rules:

- **Default**: Deny all access (fail-secure)
- **GET /api/users**: Allow any authenticated user
- **POST /api/users**: Allow only admin role
- **PUT /api/users/{name}**: Allow only admin role
- **DELETE /api/users/{name}**: Allow only admin role

Users are identified via the `user` query parameter, and must be non-empty and non-null to authenticate.

## Quick Start

### Kubernetes Deployment

Create a local Kind cluster:

```bash
cd kube
bash create_cluster.sh
```

Deploy to Kubernetes:

```bash
kubectl apply -f kube/configmap_opa.yml
kubectl apply -f kube/dep_opa.yml
```

Verify deployments:

```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

Access the API:

```bash
# Through Ingress (HTTPS on localhost)
curl -k "https://localhost/api/users?user=testuser"

# Or directly to service port
kubectl port-forward service/flask-service 8000:8000
curl "http://localhost:8000/api/users?user=testuser"
```

## License

This project is provided as-is for educational and development purposes.

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Open Policy Agent Documentation](https://www.openpolicyagent.org/)
- [Rego Language Guide](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kind - Kubernetes in Docker](https://kind.sigs.k8s.io/)