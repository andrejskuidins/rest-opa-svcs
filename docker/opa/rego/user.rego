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
