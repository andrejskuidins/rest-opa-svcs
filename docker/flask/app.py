import json
import requests
import os
from flask import Flask, jsonify, request
from variables import users

app = Flask(__name__)

OPA_URL = os.getenv("OPA_URL", "http://opa-service:8181/v1/data/httpapi/authz")


def check_access(method, path, role=None):
    user = request.args.get("user")
    input_dict = {"input": {"user": user, "method": method, "path": path, "role": role}}
    print(f"Sending to OPA: {json.dumps(input_dict, indent=2)}")  # Debug
    rsp = requests.post(OPA_URL, json=input_dict)
    result = rsp.json()
    print(f"OPA response: {json.dumps(result, indent=2)}")  # Debug
    return result["result"]["allow"]


@app.route("/api/users", methods=["GET"])
def get_users():
    if not check_access("GET", ["api", "users"]):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(users)


@app.route("/api/users/<string:name>", methods=["GET"])
def get_user_by_name(name: str):
    if not check_access("GET", ["api", "users", name]):
        return jsonify({"error": "Unauthorized"}), 401

    user = get_user(name)
    if user is None:
        return jsonify({"error": "user does not exist"}), 404
    return jsonify(user)


def get_user(name):
    return next((e for e in users if e["name"] == name), None)


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

    users.append(user)

    return "", 201, {"location": f'/api/users/{user["name"]}'}


@app.route("/api/users/<string:name>", methods=["PUT"])
def update_user(name: str):
    role = request.args.get("role")
    if not check_access("PUT", ["api", "users", name], role):
        return jsonify({"error": "Unauthorized"}), 401

    user = get_user(name)
    if user is None:
        return jsonify({"error": "user does not exist."}), 404

    updated_user = json.loads(request.data)
    if not user_is_valid(updated_user):
        return jsonify({"error": "Invalid user properties."}), 400

    user.update(updated_user)

    return jsonify(user)


@app.route("/api/users/<string:name>", methods=["DELETE"])
def delete_user(name: str):
    global users
    role = request.args.get("role")
    if not check_access("DELETE", ["api", "users", name], role):
        return jsonify({"error": "Unauthorized"}), 401

    user = get_user(name)
    if user is None:
        return jsonify({"error": "user does not exist."}), 404

    users = [e for e in users if e["name"] != name]
    return jsonify(user), 200


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "8000"))
    app.run(host='0.0.0.0', port=port)
