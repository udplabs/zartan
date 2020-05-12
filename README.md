# zartan
![Zartan Logo][logo]

Zartan is a master of make-up and disguise and so is this demo platform

## Requirements
* Python 3.7+ and Flask
* Okta tenant. [Free tenant](https://developer.okta.com/)
* Sparlpost account. [Here](https://www.sparkpost.com/)

## Setup

### Setup Okta tenant.

* TODO

### Setup Sparkpost account.

* TODO

### Setup Application.

Copy `.env.sample` to `.env`.

```bash
$ cp .env.sample .env
```

Update `.env` file favorite editor.

```bash
# i.e. .env file
# Okta Setting
OKTA_CLIENT_ID="_GET_THIS_OKTA_"
OKTA_CLIENT_SECRET="_GET_THIS_OKTA_"
OKTA_ISSUER="_GET_THIS_OKTA_"
OKTA_ORG_URL="_GET_THIS_OKTA_"
OKTA_OIDC_REDIRECT_URI="http://localhost:8080/authorization-code/callback"
OKTA_API_TOKEN="_GET_THIS_OKTA_"

...
```

Run it!

```bash
$ python -m venv venv
$ source venv/bin/activate
$ python app.py

# i.e.
 * Serving Flask app "app.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 293-952-088
```

Navigate to http://127.0.0.1:5000.

## Authors
* Shawn Recinto

[logo]: README/img/zartan.png "Zartan is a master of make-up and disguise and so is this demo platform"
