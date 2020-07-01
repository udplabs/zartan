# Zartan Usage Guide <!-- omit in toc -->

>> WIP: Just placeholder for now and will convert this content into vuepress for readability

- [Setup Okta Org for each Vertical](#setup-okta-org-for-each-vertical)
- [How to demo](#how-to-demo)
  - [Use Cases or Scenarios: Dealer](#use-cases-or-scenarios-dealer)
  - [Use Cases or Scenarios: Travel Agency](#use-cases-or-scenarios-travel-agency)
  - [Use Cases or Scenarios: Hospitality](#use-cases-or-scenarios-hospitality)
  - [Use Cases or Scenarios: Streaming Services](#use-cases-or-scenarios-streaming-services)
  - [Use Cases or Scenarios: Finance](#use-cases-or-scenarios-finance)
- [Troubleshooting: FAQs](#troubleshooting-faqs)

### Download and Install Terraform

* Download the [Terraform binary](https://www.terraform.io/downloads.html) for your OS
* Follow the instructions for [TheTerraform Install Guide](https://learn.hashicorp.com/terraform/getting-started/install) for your OS
* Verify terraform is installed correctly by going to the command line / shell, then type the command `terraform version`, press `Enter` or `Return` and you should see a response similar to `Terraform v0.12.28`

### Configure, initialize and apply Terraform for the vertical you want to use
* Create a local `.tfvars` file in the `terraform` folder, under the `vertical` and name the file the same as the `vertical` e.g. `terraform/travelagency/travelagency.tfvars`
* Add the following variables
  * `org_name="<okta_subdomain>"`
  * `api_token="<okta_api_token>"`
  * `base_url="<oktapreview.com or okta.com>"`
  * `demo_app_name="<zartan vertical name i.e. travelagency>"`
  * `udp_subdomain="<name of your demo i.e. local>"`
  * `test_app_domain="<name of your local app domain>"`
* Next, in the command line / shell, navigate to the terraform directory then to the desired vertical e.g. `terraform/travelagency` and type `terraform init`
* Execute the plan `terraform plan -var-file <zartan vertical name>.tfvars` e.g. `terraform plan -var-file travelagency.tfvars`
* Finally apply the plan `terraform apply -var-file <zartan vertical name>.tfvars` e.g. `terraform apply -var-file travelagency.tfvars`
* Type 'yes' at the prompt and once it is completed you should see the following message similar to `Apply complete! Resources: 6 added, 0 changed, 0 destroyed.`
* Verify by checking in your okta org

## Setup Okta Org for each Vertical

>> WIP: Needs further details, just assuming. Plus attached terraform script could be reference.

* Feature Flags to enable
* Attributes to create in UD
* SignOn Policy
* Authorization Servers
* Access Policy
* Scope and Claims
* Multi-factor
* Inline and Event Hooks

## How to demo

Talking points and Steps Matrix

### Use Cases or Scenarios: Dealer

| Use Case | Demoing Steps |
| ---      | ---           |
| Self Registration | 1. etc |
| Progressive Profiling | 1. etc |
| Inline Hooks | 1. etc |

### Use Cases or Scenarios: Travel Agency

| Use Case | Demoing Steps |
| ---      | ---           |
| Self Registration | 1. etc |
| Progressive Profiling | 1. etc |

### Use Cases or Scenarios: Hospitality

| Use Case | Demoing Steps |
| ---      | ---           |
| Self Registration | 1. etc |
| Progressive Profiling | 1. etc |
| Consent Management | 1. etc |

### Use Cases or Scenarios: Streaming Services

| Use Case | Demoing Steps |
| ---      | ---           |
| Self Registration | 1. etc |
| Progressive Profiling | 1. etc |

### Use Cases or Scenarios: Finance

| Use Case | Demoing Steps |
| ---      | ---           |
| Step Authentication | 1. etc |
| Progressive Profiling | 1. etc |

## Troubleshooting: FAQs

* Question: The applications broke!