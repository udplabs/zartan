variable "org_name" {}
variable "api_token" {}
variable "base_url" {}
variable "demo_app_name" { default="credit" }
variable "udp_subdomain" { default="local_zartan" }

locals {
    app_domain = "${var.udp_subdomain}.${var.demo_app_name}.unidemo.info"
}

provider "okta" {
  org_name  = var.org_name
  api_token = var.api_token
  base_url  = var.base_url
  version   = "~> 3.0"
}
data "okta_group" "all" {
  name = "Everyone"
}
resource "okta_app_oauth" "credit" {
  label          = "${var.demo_app_name} Demo (Generated by UDP)"
  type           = "web"
  grant_types    = ["authorization_code"]
  redirect_uris  = [
    "https://${local.app_domain}/authorization-code/callback",
    "http://localhost:8666/authorization-code/callback"
  ]
  response_types = ["code"]
  issuer_mode    = "ORG_URL"
  consent_method = "TRUSTED"
  groups         = ["${data.okta_group.all.id}"]
}
resource "okta_trusted_origin" "credit_https" {
  name   = "${var.demo_app_name} HTTPS"
  origin = "https://${local.app_domain}"
  scopes = ["REDIRECT", "CORS"]
}
resource "okta_auth_server" "credit" {
  name        = "${var.demo_app_name}"
  description = "Generated by UDP"
  audiences   = ["api://${local.app_domain}"]
}
resource "okta_auth_server_policy" "credit" {
  auth_server_id   = okta_auth_server.credit.id
  status           = "ACTIVE"
  name             = "standard"
  description      = "Generated by UDP"
  priority         = 1
  client_whitelist = ["${okta_app_oauth.credit.id}"]
}
resource "okta_auth_server_policy_rule" "credit" {
  auth_server_id       = okta_auth_server.credit.id
  policy_id            = okta_auth_server_policy.credit.id
  status               = "ACTIVE"
  name                 = "one_hour"
  priority             = 1
  group_whitelist      = ["${data.okta_group.all.id}"]
  grant_type_whitelist = ["authorization_code"]
  scope_whitelist      = ["*"]
}
output "client_id" {
  value = "${okta_app_oauth.credit.client_id}"
}
output "client_secret" {
  value = "${okta_app_oauth.credit.client_secret}"
}
output "domain" {
  value = "${var.org_name}.${var.base_url}"
}
output "auth_server_id" {
  value = "${okta_auth_server.credit.id}"
}
output "issuer" {
  value = "${okta_auth_server.credit.issuer}"
}
output "okta_app_oauth_id" {
  value = "${okta_app_oauth.credit.id}"
}
