import json
import requests
from flask import Flask, jsonify, request
from variables import employees

app = Flask(__name__)


def check_access(method, path, role=None):
    user = request.args.get("user")
    input_dict = {"input": {"user": user, "method": method, "path": path, "role": role}}
    rsp = requests.post("http://127.0.0.1:8181/v1/data/httpapi/authz", json=input_dict)
    if not rsp.json()["result"]["allow"]:
        return "Unauthorized!", 401
    return "Welcome Home!", 200


@app.route("/employees", methods=["GET"])
def get_employees():
    if not check_access("GET", ["api", "users"]):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(employees)


@app.route("/employees/<string:name>", methods=["GET"])
def get_employee_by_name(name: str):
    employee = get_employee(name)
    if employee is None:
        return jsonify({"error": "Employee does not exist"}), 404
    return jsonify(employee)


def get_employee(name):
    return next((e for e in employees if e["name"] == name), None)


def employee_is_valid(employee):
    required_keys = {"name", "email"}
    return set(employee.keys()) == required_keys


@app.route("/employees", methods=["POST"])
def create_employee():
    role = request.args.get("role")
    if not check_access("POST", ["api", "users"], role):
        return jsonify({"error": "Unauthorized"}), 401

    employee = json.loads(request.data)
    if not employee_is_valid(employee):
        return jsonify({"error": "Invalid employee properties."}), 400

    employees.append(employee)

    return "", 201, {"location": f'/employees/{employee["name"]}'}


@app.route("/employees/<string:name>", methods=["PUT"])
def update_employee(name: str):
    employee = get_employee(name)
    if employee is None:
        return jsonify({"error": "Employee does not exist."}), 404

    updated_employee = json.loads(request.data)
    if not employee_is_valid(updated_employee):
        return jsonify({"error": "Invalid employee properties."}), 400

    employee.update(updated_employee)

    return jsonify(employee)


@app.route("/employees/<string:name>", methods=["DELETE"])
def delete_employee(name: str):
    global employees
    employee = get_employee(name)
    if employee is None:
        return jsonify({"error": "Employee does not exist."}), 404

    employees = [e for e in employees if e["name"] != name]
    return jsonify(employee), 200


if __name__ == "__main__":
    app.run(port=5000)
