resource "okta_trusted_origin" "localhost_http" {
  name   = "zartan zstreamingservice"
  origin = "http://zstreamingservice.local"
  scopes = ["REDIRECT", "CORS"]
}
