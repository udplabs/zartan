variable "org_name" {}
variable "api_token" {}
variable "base_url" {}
variable "demo_app_name" { default = "zartantv" }
variable "udp_subdomain" { default = "local" }

locals {
  app_domain       = "${var.udp_subdomain}.${var.demo_app_name}.unidemo.info"
  nodash_subdomain = replace(var.udp_subdomain, "-", "_")
}

provider "okta" {
  org_name  = var.org_name
  api_token = var.api_token
  base_url  = var.base_url
  version   = "~> 3.11"
}
data "okta_group" "all" {
  name = "Everyone"
}
resource "okta_app_oauth" "zartantv" {
  label       = "${var.udp_subdomain} ${var.demo_app_name} Demo (Generated by UDP)"
  type        = "web"
  grant_types = ["authorization_code"]
  redirect_uris = [
    "https://${local.app_domain}/authorization-code/callback",
    "http://localhost:8666/authorization-code/callback"
  ]
  post_logout_redirect_uris = [
    "https://${local.app_domain}/index",
    "http://localhost:8666/index"
  ]
  response_types = ["code"]
  consent_method = "TRUSTED"
  issuer_mode    = "ORG_URL"
  groups         = ["${data.okta_group.all.id}"]
}
# # sign on policy for the app
# data "okta_app_signon_policy" "zartantv" {
#   app_id = okta_app_oauth.zartantv.id
#   depends_on = [okta_app_oauth.zartantv]
# }
# # policy rule for the app
# resource "okta_app_signon_policy_rule" "zartantv_policy" {
#   name = "Any 1 authenticator"
#   policy_id = data.okta_app_signon_policy.zartantv.id
#   constraints = [
#       jsonencode({
#       "type": "ASSURANCE",
#       "factorMode": "1FA",
#       "constraints": [],
#       "reauthenticateIn": "PT4H"
#     })
#   ]
#   depends_on = [data.okta_app_signon_policy.zartantv]
# }
resource "okta_app_oauth" "networktv" {
  label       = "${var.udp_subdomain} ${var.demo_app_name} network tv (Generated by UDP)"
  type        = "native"
  token_endpoint_auth_method = "client_secret_basic"
  grant_types = [
    "authorization_code",
    #"urn:ietf:params:oauth:grant-type:device_code",
    "refresh_token"
  ]
  redirect_uris = [
    "https://${local.app_domain}/authorization-code/callback",
    "http://localhost:8666/authorization-code/callback"
  ]
  post_logout_redirect_uris = [
    "https://${local.app_domain}/index",
    "http://localhost:8666/index"
  ]
  response_types = ["code"]
  consent_method = "TRUSTED"
  issuer_mode    = "ORG_URL"
  groups         = ["${data.okta_group.all.id}"]
}
# # sign on policy for the app
# data "okta_app_signon_policy" "networktv" {
#   app_id = okta_app_oauth.networktv.id
#   depends_on = [okta_app_oauth.networktv]
# }
# # policy rule for the app
# resource "okta_app_signon_policy_rule" "networktv_policy" {
#   name = "Any 1 authenticator"
#   policy_id = data.okta_app_signon_policy.networktv.id
#   constraints = [
#       jsonencode({
#       "type": "ASSURANCE",
#       "factorMode": "1FA",
#       "constraints": [],
#       "reauthenticateIn": "PT4H"
#     })
#   ]
#   depends_on = [data.okta_app_signon_policy.networktv]
# }
resource "okta_trusted_origin" "zartantv_https" {
  name   = "${var.udp_subdomain} ${var.demo_app_name} HTTPS"
  origin = "https://${local.app_domain}"
  scopes = ["REDIRECT", "CORS"]
}
resource "okta_auth_server" "zartantv" {
  name        = "${var.udp_subdomain} ${var.demo_app_name}"
  description = "Generated by UDP"
  #issuer_mode = "DYNAMIC"
  audiences   = ["api://${local.app_domain}"]
}
resource "okta_auth_server_policy" "zartantv" {
  auth_server_id   = okta_auth_server.zartantv.id
  status           = "ACTIVE"
  name             = "standard"
  description      = "Generated by UDP"
  priority         = 1
  client_whitelist = ["${okta_app_oauth.zartantv.id}","${okta_app_oauth.networktv.id}"]
}
resource "okta_auth_server_policy_rule" "zartantv" {
  auth_server_id       = okta_auth_server.zartantv.id
  policy_id            = okta_auth_server_policy.zartantv.id
  status               = "ACTIVE"
  name                 = "Web app (auth/interaction code flow)"
  priority             = 1
  group_whitelist      = ["${data.okta_group.all.id}"]
  grant_type_whitelist = ["authorization_code"]
  scope_whitelist      = ["*"]
}
resource "okta_auth_server_policy_rule" "networktv" {
  auth_server_id       = okta_auth_server.zartantv.id
  policy_id            = okta_auth_server_policy.zartantv.id
  status               = "ACTIVE"
  name                 = "Network TV devices"
  priority             = 2
  group_whitelist      = ["${data.okta_group.all.id}"]
  #grant_type_whitelist = ["urn:ietf:params:oauth:grant-type:device_code"]
  grant_type_whitelist = ["authorization_code"]
  scope_whitelist      = ["*"]
  access_token_lifetime_minutes = 5
}
resource "okta_app_user_schema" "customfield1" {
  app_id      = "${okta_app_oauth.networktv.id}"
  index       = "${local.nodash_subdomain}_${var.demo_app_name}_authorized_devices"
  title       = "${var.udp_subdomain}_${var.demo_app_name}_authorized_devices"
  type        = "array"
  array_type  = "string"
  description = "Authorized Devices"
  master      = "OKTA"
  scope       = "SELF"
  permissions = "READ_WRITE"
}
output "client_id" {
  value = "${okta_app_oauth.zartantv.client_id}"
}
output "client_secret" {
  value = "${okta_app_oauth.zartantv.client_secret}"
}
output "domain" {
  value = "${var.org_name}.${var.base_url}"
}
output "auth_server_id" {
  value = "${okta_auth_server.zartantv.id}"
}
output "issuer" {
  value = "${okta_auth_server.zartantv.issuer}"
}
output "okta_app_oauth_id" {
  value = "${okta_app_oauth.zartantv.id}"
}