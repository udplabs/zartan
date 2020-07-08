# Zartan LOCAL Usage Guide <!-- omit in toc -->

This document is how to set up and run Zartan in your own local environment, outside of UDP

>> WIP: Just placeholder for now and will convert this content into vuepress for readability

- [Setup Okta Org for each Vertical](#setup-okta-org-for-each-vertical)
- [How to demo](#how-to-demo)
  - [Use Cases or Scenarios: Dealer](#use-cases-or-scenarios-dealer)
  - [Use Cases or Scenarios: Travel Agency](#use-cases-or-scenarios-travel-agency)
  - [Use Cases or Scenarios: Hospitality](#use-cases-or-scenarios-hospitality)
  - [Use Cases or Scenarios: Streaming Services](#use-cases-or-scenarios-streaming-services)
  - [Use Cases or Scenarios: Finance](#use-cases-or-scenarios-finance)
- [Troubleshooting: FAQs](#troubleshooting-faqs)

## Requirements

These items need to be downloaded and installed in order to properly run a Zartan demo

* Python 3.6+ and Flask
* Okta tenant. [Free tenant](https://developer.okta.com/)
* (Optional) git client [git client installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Python

Zartan Requires Python 3.6 or higher to run properly.  Python can be downloaded here [Python Download](https://www.python.org/downloads/)

You can also leverage services like Heroku and AWS Elastic Beanstalk to run Zartan as well.

NOTE: There mmay be compatability issues with MacOS and Catalina.  Please refer to your OS version when installing Python

### Zartan

* You can clone the Zartan codebase down from github [Zartan on github](https://github.com/udplabs/zartan) to your local system
  * (optional)Create a directory to serve the Zartan app off of in your local environment
  * (Git cloning instruction)[https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository]
  * `git clone git@github.com:udplabs/zartan.git` for ssh
  * `git clone https://github.com/udplabs/zartan.git` for https
* Use venv [venv reference](https://docs.python.org/3/tutorial/venv.html) This will set up a contained environment to run the zartan app on without impacting your entire python environment.  Please run this from a directory/folder that you specifically create for it
  * `python -m venv zartan-env` or `python3 -m venv zartan-env` depending on your python installation. This will create and siloed environment called `zartan-env` you can change this name if you want but just remember what you used as you will need to activate the environment to run zartan.
  * Activate the zartan environment from the folder you set up for it: for MacOS/Linux `source zartan-env/bin/activate` for Windows `zartan-env\Scripts\activate.bat`
  * `pip install -r requirements.txt` from the root app folder NOTE: you may need to run as `pip3 install -r requirements.txt` if you have python 2.7 on your local instance along with python 3.x

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

## General Config

* Set up a `.env` file [see .env sample](../.env.sample)
* Enter the proper values based on your vertical after running your terraform script for the vertical (see below)

`.env` settings in general

* Okta Setting
  * OKTA_CLIENT_ID="_GET_THIS_OKTA_"
  * OKTA_CLIENT_SECRET="_GET_THIS_OKTA_"
  * OKTA_ISSUER="_GET_THIS_OKTA_"
  * OKTA_ORG_URL="_GET_THIS_OKTA_"
  * OKTA_OIDC_REDIRECT_URI="http://localhost:8080/authorization-code/callback"
  * OKTA_API_TOKEN="_GET_THIS_OKTA_"

* Zartan Setting
  * APP_TEMPLATE="sample"
  * APP_LOGINMETHOD="standard-widget"
  * APP_NAME="Sample App"
  * APP_SLOGAN="Some Slogan"
  * APP_SUBSLOGAN="Some Sub Text Slogan"
  * APP_LOGO="URL_TO_LOGO"
  * APP_FAVICON="URL_TO_FAVICON"
  * APP_BANNER_1="URL_TO_BANNER_IMG"
  * APP_PRIMARY_COLOR="#0061f2"
  * APP_SECONDARY_COLOR="#6900c7"
  * APP_SUCCESS_COLOR="#00ac69"
  * APP_INFO_COLOR="#00cfd5"
  * APP_WARNING_COLOR="#f4a100"
  * APP_DANGER_COLOR="#e81500"

* Third Party Setting
  * SPARKPOST_API_KEY="[Box Link To Key](https://okta.box.com/s/cgp429sqbbowuuyiqgckq6t836lyp8jw)"

* Flask Setting
  * SECRET_KEY="SOME_RANDOM_GUID"


## Config: Admin vertical

`.env` settings: Change this value to use this vertical

* Zartan Setting
  * APP_TEMPLATE="admin"

## Config: Credit vertical

`.env` settings: Change/Add these values to use this vertical

* Zartan Setting
  * APP_TEMPLATE="credit"

* Step Up
  * APP_STEPUP_AUTH_CLIENTID="_GET_THIS_OKTA_"
  * APP_STEPUP_AUTH_CLIENTURL="_GET_THIS_OKTA_"

## Config: Dealer vertical

`.env` settings: Change this value to use this vertical

* Zartan Setting
  * APP_TEMPLATE="dealer"

## Config: Finance vertical

.env` settings: Change/Add these values to use this vertical

* Zartan Setting
  * APP_TEMPLATE="finance"

* Step Up
  * APP_STEPUP_AUTH_CLIENTID="_GET_THIS_OKTA_"
  * APP_STEPUP_AUTH_CLIENTURL="_GET_THIS_OKTA_"

## Config: Healthcare vertical

.env` settings: Change/Add these values to use this vertical

* Zartan Setting
  * APP_TEMPLATE="healthcare"

* Step Up
  * APP_STEPUP_AUTH_CLIENTID="_GET_THIS_OKTA_"
  * APP_STEPUP_AUTH_CLIENTURL="_GET_THIS_OKTA_"

## Config: Hospitality vertical

`.env` settings: Change this value to use this vertical

* Zartan Setting
  * APP_TEMPLATE="hospitality"

## Config: Streaming Service vertical

`.env` settings: Change this value to use this vertical

* Zartan Setting
  * APP_TEMPLATE="streamingservice"

## Config: Travelagency vertical

`.env` settings: Change this value to use this vertical

* Zartan Setting
  * APP_TEMPLATE="travelagency"

## Run The App

Remember to activate your zartan-env specified [in the Zartan configuration section](#zartan)

then enter `python app.py` at the command prompt. NOTE: you may need to run as `python3 app.py` if you have python 2.7 on your local instance along with python 3.x

The app will run on `http://localhost:8080` by default

## Setup Okta Org for each Vertical (outside of terraform)

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