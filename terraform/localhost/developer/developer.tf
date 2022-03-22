variable "org_name" {}
variable "api_token" {}
variable "base_url" {}
variable "demo_app_name" { default = "developer" }
variable "udp_subdomain" { default = "local" }

locals {
  app_domain = var.udp_subdomain != "local" ? format("%s.%s.unidemo.info") : format("%s.%s", var.udp_subdomain, var.demo_app_name)
}

terraform {
  required_providers {
    okta = {
      source  = "okta/okta"
      version = "~> 3.17"
    }
  }
}

provider "okta" {
  org_name  = var.org_name
  api_token = var.api_token
  base_url  = var.base_url
}

data "okta_group" "all" {
  name = "Everyone"
}

resource "okta_app_oauth" "developer" {
  label       = format("%s DEMO (Generated by UDP)", local.app_domain)
  type        = "web"
  grant_types = ["authorization_code"]
  redirect_uris = [
    "https://${local.app_domain}/authorization-code/callback",
    "http://localhost:8666/authorization-code/callback"
  ]
  response_types = ["code"]
  consent_method = "TRUSTED"
  issuer_mode    = "ORG_URL"
  lifecycle {
    ignore_changes = [groups]
  }
}

resource "okta_app_group_assignment" "admin" {
  app_id   = okta_app_oauth.developer.id
  group_id = data.okta_group.all.id
}

resource "okta_trusted_origin" "developer" {
  name   = format("%s: 8666", local.app_domain)
  origin = "https://${local.app_domain}"
  scopes = ["REDIRECT", "CORS"]
}

resource "okta_auth_server" "developer" {
  name        = local.app_domain
  description = format("%s (Generated by UDP)", local.app_domain)
  audiences   = ["api://${local.app_domain}"]
}

resource "okta_auth_server_policy" "developer" {
  auth_server_id   = okta_auth_server.developer.id
  status           = "ACTIVE"
  name             = "standard"
  description      = "Generated by UDP"
  priority         = 1
  client_whitelist = [okta_app_oauth.developer.id]
}

resource "okta_auth_server_policy_rule" "developer" {
  auth_server_id       = okta_auth_server.developer.id
  policy_id            = okta_auth_server_policy.developer.id
  status               = "ACTIVE"
  name                 = "one_hour"
  priority             = 1
  group_whitelist      = [data.okta_group.all.id]
  grant_type_whitelist = ["authorization_code"]
  scope_whitelist      = ["*"]
}

# Create the .env file
resource "local_file" "dotenv" {
  content = templatefile("${path.module}/developer.dotenv.tpl", {
    client_id         = okta_app_oauth.developer.client_id,
    client_secret     = okta_app_oauth.developer.client_secret,
    domain            = format("%s.%s", var.org_name, var.base_url),
    auth_server_id    = okta_auth_server.developer.id,
    okta_app_oauth_id = okta_app_oauth.developer.id
  })
  # filename = "${path.module}/admin.env"
  filename = format("%s/%s.env", "${path.module}", var.demo_app_name)
}

# Output to the terminal
output "client_id" {
  value = okta_app_oauth.developer.client_id
}

output "client_secret" {
  value     = okta_app_oauth.developer.client_secret
  sensitive = true
}

output "domain" {
  value = format("%s.%s", var.org_name, var.base_url)
}

output "auth_server_id" {
  value = okta_auth_server.developer.id
}

output "issuer" {
  value = okta_auth_server.developer.issuer
}

output "okta_app_oauth_id" {
  value = okta_app_oauth.developer.id
}
