# Zartan LOCAL Usage Guide <!-- omit in toc -->

This document is how to set up and run Zartan in your own local environment, outside of UDP

>> WIP: Just placeholder for now and will convert this content into vuepress for readability

- [Setup Okta Org for each Vertical](#setup-okta-org-for-each-vertical-outside-of-terraform)
- [How to demo](#how-to-demo)
  - [Use Cases or Scenarios: Dealer](https://github.com/udplabs/zartan/tree/master/docs/dealer)
  - [Use Cases or Scenarios: Travel Agency](https://github.com/udplabs/zartan/tree/master/docs/travelagency)
  - [Use Cases or Scenarios: Hospitality](https://github.com/udplabs/zartan/tree/master/docs/hospitality)
  - [Use Cases or Scenarios: Streaming Services](https://github.com/udplabs/zartan/tree/master/docs/streamingservice)
  - [Use Cases or Scenarios: Finance](https://github.com/udplabs/zartan/tree/master/docs/finance)
- [Troubleshooting: FAQs](#troubleshooting-faqs)

## Requirements

These items need to be downloaded and installed in order to properly run a Zartan demo

* Python 3.6+ and Flask
* Okta tenant. [Free tenant](https://developer.okta.com/)
* (Optional) git client [git client installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* (Optional) [Terraform](https://www.terraform.io/downloads.html) to automatically configure your Okta Org

### Python
Zartan Requires Python 3.6 or higher to run properly.
* Please refer to your OS specific instructions on installing [Python](https://www.python.org/downloads/)
    * e.g. for Mac users, you can use homebrew:
    ```bash
    brew install python
    ```
* You can also leverage services like Heroku and AWS Elastic Beanstalk to run Zartan as well.


> ℹ️  Mac users: If you've never run a Python app locally before, your machine is in an unknown state when it comes to Python development. It is a known issue for Python dependencies to have moved, become unlinked or deleted during MacOS upgrades (e.g. an upgrade to Catalina). If you have issues during any of the install steps (below) or when running Zartan locally, try reinstalling Python:
```bash
brew reinstall python
```

### Terraform
We've provided terraform files for easy configuration of the Okta Org. Specific verticals' `.tf` files are located in their respective `/terraform/{vertical}` folder. If you'd rather configure your Org manually, refer to [these steps](#setup-okta-org-for-each-vertical-outside-of-terraform).

* Download the [Terraform binary](https://www.terraform.io/downloads.html) for your OS
* Follow the instructions for [Terraform Install Guide](https://learn.hashicorp.com/terraform/getting-started/install) for your OS
* Verify terraform is installed correctly by going to the command line / shell, then type the command `terraform version`, press `Enter` or `Return` and you should see a response similar to `Terraform v0.12.28`

---

## Install
Open up a terminal/shell then:
1. Git [`clone`](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) this repo:
    ```bash
    # e.g. using https
    git clone https://github.com/udplabs/zartan.git
    ```
2. After cloning, `cd` into the `zartan` folder
3. Use [`venv`](https://docs.python.org/3/tutorial/venv.html) to setup a contained environment to run the zartan app without impacting your entire Python environment.
    ```
    python3 -m venv venv
    ```
    Or,  just `python -m venv venv` if you only have python 3.x installed on your system. Python allows multiple versions to be installed; For Mac users, most likely you'll have both python 2.7 on your local instance along with python 3.x.
4. Activate the `venv` environment: <a name="venv-activate"></a>
    * On Mac/Linux
    ```bash
    source venv/bin/activate
    ```
    * On Windows:
    ```
    venv\Scripts\activate.bat
    ```
5. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
    NOTE: You may need to run as `pip3 install -r requirements.txt` if you have python 2.7 on your local instance along with python 3.x

---

### Configure, initialize and apply Terraform for the vertical you want to use
> ℹ️  Zartan is a collection of demos for different verticals. In addition to the `.tf` files in the `/terraform/{vertical}` folders, there are also vertical specific READMEs in `/docs/{vertical}`. __For readability, this documentation will perform all following steps as if we're in the `travelagency` vertical.__ If you're installing/setting up a different vertical, simply reference the folder and/or file for that vertical.

1. `cd` into `/terraform/travelagency`
2. Copy `travelagency.tfvars.sample` into `travelagency.tfvars`
3. Edit in the variables of the `travelagency.tfvars` file:
    ```
    org_name        = "<okta_subdomain, e.g. atko>"
    api_token       = "<okta_api_token>"
    base_url        = "<enter oktapreview.com or okta.com>"
    ```
3. Initialize terraform:
    ```
    terraform init
    ```
4. Execute the "plan":
    ```
    terraform plan -var-file travelagency.tfvars
    ```
5. "Apply" the plan:
    ```
    terraform apply -var-file travelagency.tfvars
    ```
    Type `'yes'` at the prompt. Once it is completed you should see a message similar to `Apply complete! Resources: 6 added, 0 changed, 0 destroyed.`
6. Verify by checking in your Okta Org
    > NOTE: The terraform script for `travelagency` generates: 1) an OIDC Client, 2) an Auth Server, and 3) adds CORS for http://localhost:8666 and https://localhost:8666


---

### Local Environment Variables
Set up the `.env` file:
* Copy the [`.env.sample`](../.env.sample) (in the root directory) file into `.env`. Look for and edit these values in the file:

    | Variable               | Value | 
    | ---------------------- | ----- | 
    | OKTA_CLIENT_ID         | Terraform created an OIDC client named `local_zartan travelagency Demo (Generated by UDP)`. Provide its `client_id` |
    | OKTA_CLIENT_SECRET     | Terraform created an OIDC client named `local_zartan travelagency Demo (Generated by UDP)`. Provide its `client_secret` |
    | OKTA_ISSUER            | Terraform created an Auth Server named `local_zartan travelagency`. Provide its `issuer_uri` |
    | OKTA_ORG_URL           | Your org url. e.g. `https://dev-13485.oktapreview.com` |
    | OKTA_OIDC_REDIRECT_URI | Use `http://localhost:8666/authorization-code/callback` as this was set by Terraform.
    | OKTA_API_TOKEN         | Provide an okta SSWS key |
* (Optional) Provide values for the other variables. Refer to [this section](#env-variables-details) for details.

---

### Run The App
* Remember to get out of the `/terraform/travelagency` folder! __Return to the root folder, then:__
* Remember to activate your `venv` specified [in the __Install__ section](#venv-activate) (if you haven't done it already).
* Then, run python:
    ```
    python app.py
    ```
    NOTE: you may need to run as `python3 app.py` if you have python 2.7 on your local instance along with python 3.x
* Open up a browser and navigate to `http://localhost:8666`

---

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
Navigate to the respective `/docs/{vertical}` section for vertical specific READMEs.

## Additional Env File Configuration Variables
<a name="env-variables-details"></a>
The `.env` file provides additional confuration depending on the functionality supported by Zartan. Refer to the tables below to decide the proper values based on vertical. 

### Variables common to all verticals:
* Okta Setting

    | Variable               | Value | Example |
    | ---------------------- | ----- | ------- |
    | OKTA_CLIENT_ID         | {{client_id}}     | |
    | OKTA_CLIENT_SECRET     | {{client_secret}} | |
    | OKTA_ISSUER            | {{issuer_uri}} | |
    | OKTA_ORG_URL           | {{org_url}} | |
    | OKTA_OIDC_REDIRECT_URI | http://localhost:8666/authorization-code/callback | |
    | OKTA_API_TOKEN         | {{ssws token}} | |

* Zartan Setting

    | Variable            | Value | Default/Example |
    | ------------------- | ----- | ------- |
    | APP_TEMPLATE        | Enter the specific value based on the [vertical](#vertical-specific-variables) | |
    | APP_LOGINMETHOD     | the login UX, widget, custom or redirect | standard-widget
    | APP_NAME            | some app name prominently displayed | |
    | APP_SLOGAN          | some slogan | |
    | APP_SUBSLOGAN       | some subtitle | |
    | APP_LOGO            | url to some logo | |
    | APP_FAVICON         | url to some favicon | |
    | APP_BANNER_1        | url to some banner image | |
    | APP_PRIMARY_COLOR   | some primary color | #0061f2 |
    | APP_SECONDARY_COLOR | some secondary color | #6900c7 |
    | APP_SUCCESS_COLOR   | some "success" status color | #00ac69 |
    | APP_INFO_COLOR      | some "info" status color | #00cfd5 |
    | APP_WARNING_COLOR   | some "warning" status color | #f4a100 |
    | APP_DANGER_COLOR    | some "error" status color |#e81500 |

* Third Party Setting

    | Variable          | Value |
    | ----------------- | ----- |
    | SPARKPOST_API_KEY | ℹ️ Mandatory. Get the value from [Box](https://okta.box.com/s/cgp429sqbbowuuyiqgckq6t836lyp8jw) |


* Flask Setting

    | Variable   | Value |
    | ---------- | ----- |
    | SECRET_KEY | some random guid |
    | APP_SCHEME | http or https depending if you have an ssl cert|

* Unused for local installation

    ℹ️ You can ignore these as they are for UDP and not applicable when running locally
    | Variable          |
    | ----------------- |
    | UDP_CONFIG_URL    |
    | UDP_ISSUER        |
    | UDP_CLIENT_ID     |
    | UDP_CLIENT_SECRET |

---

### Vertical specific variables

* Config: Admin vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | admin |

* Config: Credit vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | credit |


    Add these values to use this vertical
    | Variable                  | Value |
    | ------------------------- | ----- |
    | APP_STEPUP_AUTH_CLIENTID  | client_id of the "Step up" app |
    | APP_STEPUP_AUTH_CLIENTURL | |


* Config: Dealer vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | dealer |


* Config: Finance vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | finance |


    Add these values to use this vertical
    | Variable                  | Value |
    | ------------------------- | ----- |
    | APP_STEPUP_AUTH_CLIENTID  | client_id of the "Step up" app |
    | APP_STEPUP_AUTH_CLIENTURL | |


* Config: Healthcare vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | healthcare |


    Add these values to use this vertical
    | Variable                  | Value |
    | ------------------------- | ----- |
    | APP_STEPUP_AUTH_CLIENTID  | client_id of the "Step up" app |
    | APP_STEPUP_AUTH_CLIENTURL | |


* Config: Hospitality vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | hospitality |


* Config: Streaming Service vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | streamingservice |



* Config: Travelagency vertical

    Set this value to use this vertical
    | Variable     | Value |
    | ------------ | ----- |
    | APP_TEMPLATE | travelagency |

## Troubleshooting: FAQs

* Question: The applications broke!