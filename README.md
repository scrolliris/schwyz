# Scrolliris Widget API

Code Name: `Schwyz /ʃviːt͡s/`

[![pipeline status][pipeline]][commit] [![coverage report][coverage]][commit]

[pipeline]: https://gitlab.com/scrolliris/scrolliris-widget-api/badges/master/pipeline.svg
[coverage]: https://gitlab.com/scrolliris/scrolliris-widget-api/badges/master/coverage.svg
[commit]: https://gitlab.com/scrolliris/scrolliris-widget-api/commits/master


```txt
           _
  ()      | |
  /\  __  | |                   __
 /  \/    |/ \   |  |  |_|   | / / _
/(__/\___/|   |_/ \/ \/   \_/|/ /_/
                            /|   /|
                            \|   \|

Schwyz; SCript and Hosted Widget for You schwyZ
```

## Repository

https://gitlab.com/scrolliris/scrolliris-widget-api


## Requirements

* Python `3.5.5` (Python `2.7.14`)
* Node.js `8.11.4` (build, npm `6.4.1`)
* DynamoDB


## Setup

```zsh
: setup python environment (e.g. virtualenv)
% python3.5 -m venv venv
% source venv/bin/activate
(venv) % pip install --upgrade pip setuptools

: node.js (e.g. nodeenv)
(venv) % pip install nodeenv
(venv) % nodeenv --python-virtualenv --with-npm --node=8.11.4
: re-activate for node.js at this time
(venv) % source venv/bin/activate
(venv) % npm install --global npm@6.4.1
(venv) % npm --version
6.4.1
```

### Development

Use `waitress` as wsgi server.  
Check `Makefile`.

```zsh
% cd /path/to/schwyz
% source venv/bin/activate

: set env
(venv) % cp .env.sample .env

: install packages
(venv) % ENV=development make setup

: install node modules & run gulp task
(venv) % npm install --global gulp-cli eslint
(venv) % npm install --ignore-scripts

: run gulp
(venv) % make build

: run server
(venv) % make serve
```

TODO

```zsh
(venv) % ./bin/dynamodb_local
```

## Deployment

### Serve

Use `CherryPy` as wsgi server.

```zsh
: run install and start server for production
(venv) % ENV=production make setup

: or start server by yourself
(venv) % ./bin/serve --env production --config config/production.ini --install
```

### Publish

E.g. Google App Engine

```zsh
: take latest sdk from https://cloud.google.com/sdk/downloads
% cd lib
(venv) % curl -sLO https://dl.google.com/dl/cloudsdk/channels/rapid/ \
  downloads/google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz

: check sha256 checksum
(venv) % echo "CHECKSUM" "" ./google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz \
  | sha256sum -c -
./google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz: OK
(venv) % tar zxvf google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz

: setup lib/ as a root for sdk
(venv) % CLOUDSDK_ROOT_DIR=. ./google-cloud-sdk/install.sh
(venv) % cd ../

: load sdk tools
(venv) % source ./bin/load-gcloud
(venv) % gcloud init
```

### Deployment

E.g. to publish to gcp (appengine)

```zsh
: deploy website
(venv) % source ./bin/load-gcloud
(venv) % gcloud app deploy ./app.yaml --project <project-id> --verbosity=info
```


### Style Check and Lint

* flake8
* flake8-docstrings (pep257)
* pylint
* eslint

#### Python

```zsh
: add hook
(venv) % flake8 --install-hook git

(venv) % make check
(venv) % make lint

: run both
(venv) % make vet
```

#### JavaScript

```zsh
(venv) % npm install eslint -g

(venv) % eslint gulpfile.js
```


## CI

You can check it by yourself using `gitlab-ci-multi-runner` on locale machine.
It requires `docker`.

```zsh
% ./bin/setup-gitlab-ci-multi-runner

: use script
% ./bin/ci-runner test
```


## License

```txt
Scrolliris Widget API
Copyright (c) 2017 Lupine Software LLC
```

`AGPL-3.0`

The project is distributed as GNU Affero General Public License. (version 3.0)

```txt
This is free software: You can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

See [LICENSE](LICENSE).
