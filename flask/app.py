import json
import requests
import os
from flask import Flask, jsonify, request
import redis
from redis import ConnectionPool
from variables import users

app = Flask(__name__)

# Redis connection pool for efficient multi-worker communication
REDIS_URL = os.getenv("REDIS_URL", "redis://redis-service:6379/0")
redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)


def get_redis():
    """Get Redis connection from pool"""
    return redis.Redis(connection_pool=redis_pool)


OPA_URL = os.getenv("OPA_URL", "http://opa-service:8181/v1/data/httpapi/authz")


def load_users_into_redis():
    """Load users from variables module into Redis on startup"""
    try:
        r = get_redis()
        for user in users:
            user_key = f"user:{user['name']}"
            r.set(user_key, json.dumps(user))
        # Store list of user names for listing all users
        user_names = [user["name"] for user in users]
        r.set("user_names", json.dumps(user_names))
        print(f"Loaded {len(users)} users into Redis")
    except Exception as e:
        print(f"Error loading users: {e}")
        raise


def check_access(method, path, role=None):
    user = request.args.get("user")
    input_dict = {"input": {"user": user, "method": method, "path": path, "role": role}}
    print(f"Sending to OPA: {json.dumps(input_dict, indent=2)}")
    rsp = requests.post(OPA_URL, json=input_dict)
    result = rsp.json()
    print(f"OPA response: {json.dumps(result, indent=2)}")
    return result["result"]["allow"]


@app.route("/api/users", methods=["GET"])
def get_users_endpoint():
    if not check_access("GET", ["api", "users"]):
        return jsonify({"error": "Unauthorized"}), 401

    r = get_redis()
    user_names = json.loads(r.get("user_names") or "[]")
    users_list = []
    for name in user_names:
        user_data = r.get(f"user:{name}")
        if user_data:
            users_list.append(json.loads(user_data))
    return jsonify(users_list)


@app.route("/api/users/<string:name>", methods=["GET"])
def get_user_by_name(name: str):
    if not check_access("GET", ["api", "users", name]):
        return jsonify({"error": "Unauthorized"}), 401

    user = get_user(name)
    if user is None:
        return jsonify({"error": "user does not exist"}), 404
    return jsonify(user)


def get_user(name):
    r = get_redis()
    user_data = r.get(f"user:{name}")
    return json.loads(user_data) if user_data else None


def user_is_valid(user):
    required_keys = {"name", "email"}
    return set(user.keys()) == required_keys


@app.route("/api/users", methods=["POST"])
def create_user():
    role = request.args.get("role")
    if not check_access("POST", ["api", "users"], role):
        return jsonify({"error": "Unauthorized"}), 401

    user = json.loads(request.data)
    if not user_is_valid(user):
        return jsonify({"error": "Invalid user properties."}), 400

    r = get_redis()
    user_key = f"user:{user['name']}"

    if r.exists(user_key):
        return jsonify({"error": "User already exists."}), 409

    r.set(user_key, json.dumps(user))

    user_names = json.loads(r.get("user_names") or "[]")
    user_names.append(user["name"])
    r.set("user_names", json.dumps(user_names))

    return "", 201, {"location": f'/api/users/{user["name"]}'}


@app.route("/api/users/<string:name>", methods=["PUT"])
def update_user(name: str):
    role = request.args.get("role")
    if not check_access("PUT", ["api", "users", name], role):
        return jsonify({"error": "Unauthorized"}), 401

    r = get_redis()
    user = get_user(name)
    if user is None:
        return jsonify({"error": "user does not exist."}), 404

    updated_user = json.loads(request.data)
    if not user_is_valid(updated_user):
        return jsonify({"error": "Invalid user properties."}), 400

    user.update(updated_user)
    r.set(f"user:{name}", json.dumps(user))

    return jsonify(user)


@app.route("/api/users/<string:name>", methods=["DELETE"])
def delete_user(name: str):
    role = request.args.get("role")
    if not check_access("DELETE", ["api", "users", name], role):
        return jsonify({"error": "Unauthorized"}), 401

    user = get_user(name)
    if user is None:
        return jsonify({"error": "user does not exist."}), 404

    r = get_redis()
    r.delete(f"user:{name}")

    user_names = json.loads(r.get("user_names") or "[]")
    user_names = [u for u in user_names if u != name]
    r.set("user_names", json.dumps(user_names))

    return jsonify(user), 200


# Load users when the module is imported (works with Gunicorn)
load_users_into_redis()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
