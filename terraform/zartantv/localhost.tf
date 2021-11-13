resource "okta_trusted_origin" "localhost_http" {
  name   = "zartan zartantv"
  origin = "http://zartantv.local"
  scopes = ["REDIRECT", "CORS"]
}
