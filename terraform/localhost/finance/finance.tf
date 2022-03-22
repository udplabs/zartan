variable "org_name" {}
variable "api_token" {}
variable "base_url" {}
variable "demo_app_name" { default = "finance" }
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

resource "okta_app_oauth" "finance" {
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

resource "okta_app_group_assignment" "finance" {
  app_id   = okta_app_oauth.finance.id
  group_id = data.okta_group.all.id
}

resource "okta_trusted_origin" "finance" {
  name   = format("%s: 8666", local.app_domain)
  origin = "https://${local.app_domain}"
  scopes = ["REDIRECT", "CORS"]
}

resource "okta_auth_server" "finance" {
  name        = local.app_domain
  description = format("%s (Generated by UDP)", local.app_domain)
  audiences   = ["api://${local.app_domain}"]
}

resource "okta_auth_server_policy" "finance" {
  auth_server_id   = okta_auth_server.finance.id
  status           = "ACTIVE"
  name             = "standard"
  description      = "Generated by UDP"
  priority         = 1
  client_whitelist = [okta_app_oauth.finance.id]
}

resource "okta_auth_server_policy_rule" "finance" {
  auth_server_id       = okta_auth_server.finance.id
  policy_id            = okta_auth_server_policy.finance.id
  status               = "ACTIVE"
  name                 = "one_hour"
  priority             = 1
  group_whitelist      = [data.okta_group.all.id]
  grant_type_whitelist = ["authorization_code", "implicit"]
  scope_whitelist      = ["*"]
}

# Create the .env file
resource "local_file" "dotenv" {
  content = templatefile("${path.module}/finance.dotenv.tpl", {
    client_id         = okta_app_oauth.finance.client_id,
    client_secret     = okta_app_oauth.finance.client_secret,
    domain            = format("%s.%s", var.org_name, var.base_url),
    auth_server_id    = okta_auth_server.finance.id,
    okta_app_oauth_id = okta_app_oauth.finance.id
  })

  filename = format("%s/%s.env", "${path.module}", var.demo_app_name)
}

# Output to the terminal
output "client_id" {
  value = okta_app_oauth.finance.client_id
}

output "client_secret" {
  value     = okta_app_oauth.finance.client_secret
  sensitive = true
}

output "domain" {
  value = "${var.org_name}.${var.base_url}"
}

output "auth_server_id" {
  value = okta_auth_server.finance.id
}

output "issuer" {
  value = okta_auth_server.finance.issuer
}

output "okta_app_oauth_id" {
  value = okta_app_oauth.finance.id
}
