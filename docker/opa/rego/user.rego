package httpapi.authz

default allow = false

# any authenticated user can list users
allow if {
  input.method == "GET"
  input.path == ["api", "users"]
  input.user != ""
  input.user != null
}

# only admin role can create new users
allow if {
  input.method == "POST"
  input.path == ["api", "users"]
  input.role == "admin"
}

# only admin role can update new users
allow if {
  input.method == "PUT"
  count(input.path) == 3
  input.path[0] == "api"
  input.path[1] == "users"
  input.role == "admin"
}

# only admin role can delete new users
allow if {
  input.method == "DELETE"
  count(input.path) == 3
  input.path[0] == "api"
  input.path[1] == "users"
  input.role == "admin"
}
