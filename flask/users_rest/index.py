import json
from flask import Flask, jsonify, request
app = Flask(__name__)

employees = [
  { 'name': 'Barbara Jones', 'email': 'barbara.jones@outlook.com' },
  { 'name': 'Ruth Young', 'email': 'ruth.young@infra.org' },
  { 'name': 'Aaron Graves', 'email': 'aaron.graves@infra.org' },
  { 'name': 'Patrick Johnson', 'email': 'patrick.johnson@systems.com' },
  { 'name': 'Matthew Santiago', 'email': 'matthew.santiago@digital.io' },
  { 'name': 'Gary Clark', 'email': 'gary.clark@apps.com' },
  { 'name': 'Ronald Holland', 'email': 'ronald.holland@tech.io' },
  { 'name': 'Joshua Thomas', 'email': 'joshua.thomas@yahoo.com' },
  { 'name': 'George Norris', 'email': 'george.norris@enterprise.com' },
  { 'name': 'David Poole', 'email': 'david.poole@innovate.io' },
  { 'name': 'Brandon Harris', 'email': 'brandon.harris@cyber.net' },
  { 'name': 'Dennis Stokes', 'email': 'dennis.stokes@enterprise.com' },
  { 'name': 'Samuel Carlson', 'email': 'samuel.carlson@cloud.org' },
  { 'name': 'Maria Thompson', 'email': 'maria.thompson@cloud.org' },
  { 'name': 'Anna Gonzalez', 'email': 'anna.gonzalez@devops.net' }
]

nextEmployeeId = 4
3
@app.route('/employees', methods=['GET'])
def get_employees():
 return jsonify(employees)

@app.route('/employees/<int:id>', methods=['GET'])
def get_employee_by_id(id: int):
 employee = get_employee(id)
 if employee is None:
   return jsonify({ 'error': 'Employee does not exist'}), 404
 return jsonify(employee)

def get_employee(id):
 return next((e for e in employees if e['id'] == id), None)

def employee_is_valid(employee):
 for key in employee.keys():
   if key != 'name':
    return False
 return True

@app.route('/employees', methods=['POST'])
def create_employee():
 global nextEmployeeId
 employee = json.loads(request.data)
 if not employee_is_valid(employee):
   return jsonify({ 'error': 'Invalid employee properties.' }), 400

 employee['id'] = nextEmployeeId
 nextEmployeeId += 1
 employees.append(employee)

 return '', 201, { 'location': f'/employees/{employee["id"]}' }

@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id: int):
 employee = get_employee(id)
 if employee is None:
   return jsonify({ 'error': 'Employee does not exist.' }), 404

 updated_employee = json.loads(request.data)
 if not employee_is_valid(updated_employee):
   return jsonify({ 'error': 'Invalid employee properties.' }), 400

 employee.update(updated_employee)

 return jsonify(employee)

@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id: int):
 global employees
 employee = get_employee(id)
 if employee is None:
   return jsonify({ 'error': 'Employee does not exist.' }), 404

 employees = [e for e in employees if e['id'] != id]
 return jsonify(employee), 200

if __name__ == '__main__':
   app.run(port=5000)
