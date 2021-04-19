resource "okta_trusted_origin" "localhost_http" {
  name   = "zartan localhost 8666"
  origin = "http://localhost:8666"
  scopes = ["REDIRECT", "CORS"]
}
