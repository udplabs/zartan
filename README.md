# Zartan
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<!-- markdownlint-disable -->
<a href="https://en.wikipedia.org/wiki/Zartan">
  <img src="./docs/_img/zartan.png" width="200px;" />
</a>
<!-- markdownlint-enable -->

Zartan is a master of make-up and disguise and so is this demo platform. :tada::unicorn::rainbow:

## Requirements

* Python >= 3.7+
* Flask >= 1.x
* A Okta tenant. [Free](https://developer.okta.com/) :wink:

## Features

<table><tbody><tr style="height: 115px;"><td>Application</td><td>Okta Session Auto Login</td><td>Login Widget (Social Login, IDP Discovery, MFA)</td><td>Password-less <br />Widget&nbsp;</td><td>Custom Widget</td><td>Custom&nbsp; Registration</td><td>Profile<br />(ID Token and Access Token Viewer)</td><td>Custom MFA Enrollment</td><td>User Apps (Display Other User Apps, B2B)</td><td>Manage Users (Create User, Update User, Suspend User, Password Reset)</td><td>Step Up Authentication using MFA</td><td>ID Verification (Uses Evident)</td><td>Consent&nbsp;</td><td>Progressive Profiling&nbsp;</td><td>Temporary MFA for Users</td><td>Hard Token Setup</td><td>User Approve Workflow</td><td>IDP Management</td><td>Device Flow</td></tr><tr style="height: 36px;"><td>Travel Agency</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr style="height: 39px;"><td>Streaming Service</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>✓</td></tr><tr style="height: 24px;"><td>Hospitality</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr style="height: 24px;"><td>Credit</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr style="height: 24px;"><td>Finance</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr style="height: 27px;"><td>Dealer</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr style="height: 27px;"><td>Healthcare</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr style="height: 25px;"><td>Admin</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>✓</td><td>&nbsp;</td></tr><tr style="height: 49px;"><td>Ecommerce</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr></tbody></table>

## Setup

### Manual
[Local Zartan Setup instructions](./docs/README.md)

### Docker-Compose

Pre-requirements
* [docker-desktop](https://www.docker.com/products/docker-desktop) => 2.3.0.4
* :warning: Assumed an OAuth/OpenID Client has already been created. Either by [terraform](https://github.com/udplabs/zartan/blob/master/docs/README.md#configure-initialize-and-apply-terraform-for-the-vertical-you-want-to-use) or [manually](https://github.com/udplabs/zartan/blob/master/docs/README.md#setup-okta-org-for-each-vertical-outside-of-terraform), with `.env` filed configured.

```bash
# Validate .env exist and configured
$ cat .env
# Okta Setting
OKTA_CLIENT_ID="0oa****************"
OKTA_CLIENT_SECRET="ntd************************"
OKTA_ISSUER="https://udp-narisak-a59.oktapreview.com/oauth2/aus**********"
OKTA_ORG_URL="https://udp-narisak-a59.oktapreview.com"
OKTA_OIDC_REDIRECT_URI="http://localhost:8666/authorization-code/callback"
OKTA_API_TOKEN="00iq*******7NHYULle5"
...

# Start the container(app) in the background (eg. '-d' flag). NOTE: Will take awhile since container needs to be built.
$ docker-compose up -d

# Navigate http://localhost:8666 with your favorite browser (eg. macOS default Chrome)
$ open http://localhost:8666

# Stop the container
$ docker-compose stop

# Clean up
$ docker-compose down
```

## Authors
* [Shawn Recinto](https://github.com/srecinto)
* [Dan Zadik](https://github.com/dzadikdev)
* [Bhanchand Prasad](https://github.com/bhanchand)

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
    <td align="center"><a href="https://github.com/zeekhoo-okta"><img src="https://avatars1.githubusercontent.com/u/20686224?v=4" width="100px;" alt=""/><br /><sub><b>zeekhoo-okta</b></sub></a><br /><a href="https://github.com/noinarisak/zartan/commits?author=zeekhoo-okta" title="Documentation">📖</a> <a href="https://github.com/noinarisak/zartan/commits?author=zeekhoo-okta" title="Code">💻</a> <a href="https://github.com/noinarisak/zartan/issues?q=author%3Azeekhoo-okta" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://joel.franusic.com"><img src="https://avatars0.githubusercontent.com/u/41538?v=4" width="100px;" alt=""/><br /><sub><b>Joël Franusic</b></sub></a><br /><a href="https://github.com/noinarisak/zartan/commits?author=jpf" title="Documentation">📖</a> <a href="https://github.com/noinarisak/zartan/commits?author=jpf" title="Code">💻</a></td>
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
