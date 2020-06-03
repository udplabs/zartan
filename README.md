# zartan
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
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
* [Shawn Recinto](https://github.com/srecinto)
* [Dan Zadik](https://github.com/dzadikdev)
* [Bhanchand Prasad](https://github.com/bhanchand)

[logo]: https://cdn-zartan.s3.us-east-2.amazonaws.com/static/img/zartan.png "Zartan is a master of make-up and disguise and so is this demo platform"

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/bhanchand"><img src="https://avatars0.githubusercontent.com/u/18057642?v=4" width="100px;" alt=""/><br /><sub><b>bhanchand</b></sub></a><br /><a href="https://github.com/noinarisak/zartan/commits?author=bhanchand" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/noinarisak"><img src="https://avatars3.githubusercontent.com/u/341437?v=4" width="100px;" alt=""/><br /><sub><b>Noi Narisak</b></sub></a><br /><a href="https://github.com/noinarisak/zartan/commits?author=noinarisak" title="Code">💻</a> <a href="https://github.com/noinarisak/zartan/commits?author=noinarisak" title="Documentation">📖</a> <a href="#infra-noinarisak" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    <td align="center"><a href="https://github.com/srecinto"><img src="https://avatars2.githubusercontent.com/u/2954123?v=4" width="100px;" alt=""/><br /><sub><b>Shawn Recinto</b></sub></a><br /><a href="https://github.com/noinarisak/zartan/commits?author=srecinto" title="Code">💻</a> <a href="#projectManagement-srecinto" title="Project Management">📆</a> <a href="https://github.com/noinarisak/zartan/commits?author=srecinto" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/dzadikdev"><img src="https://avatars0.githubusercontent.com/u/57756515?v=4" width="100px;" alt=""/><br /><sub><b>dzadikdev</b></sub></a><br /><a href="https://github.com/noinarisak/zartan/commits?author=dzadikdev" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!