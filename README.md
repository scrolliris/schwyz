# Puteoli

`/p(j)utɪ́ːəlɑ̀ɪ/`

[![pipeline status][pipeline]][commit] [![coverage report][coverage]][commit]




```txt
 , __                     _
/|/  \                   | | o
 |___/      _|_  _   __  | |
 |    |   |  |  |/  /  \_|/  |
 |     \_/|_/|_/|__/\__/ |__/|_/

Puteoli; uPstrem UTility & widgEt hOsting appLIcation
```

## Repository

https://gitlab.com/scrolliris/puteoli


## Requirements

* Python `3.5.4`
* Node.js `7.10.1` (build, npm `5.2.0`)
* DynamoDB
* Datastore


## Setup

```zsh
: setup python environment (e.g. virtualenv)
% python3.5 -m venv venv
% source venv/bin/activate
(venv) % pip install --upgrade pip setuptools

: node.js (e.g. nodeenv)
(venv) % pip install nodeenv
(venv) % nodeenv --python-virtualenv --with-npm --node=7.10.1
: re-activate for node.js at this time
(venv) % source venv/bin/activate
(venv) % npm install --global npm@5.2.0
(venv) % npm --version
5.2.0
```

### Development

Use `waitress` as wsgi server.  
Check `Makefile`.

```zsh
% cd /path/to/puteoli
% source venv/bin/activate

: set env
(venv) % cp .env.sample .env

: install packages
(venv) % ENV=development make setup

: install node modules & run gulp task
(venv) % npm install --global gulp-cli eslint
(venv) % npm install --ignore-scripts

(venv) % gulp

: run server
(venv) % make serve
```

TODO

```zsh
(venv) % ./bin/dynamodb_local
(venv) % ./bin/datastore_local --project <PROJECT_ID> --clean
```


## Configuration

Set `VIEW_TYPE={tracker|reflector}` as environment variable.


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
(venv) % echo "<CHECKSUM>" "" ./google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz \
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


## Style check & Lint

* flake8
* pylint

```zsh
: check style with flake8
(venv) % make check
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
Puteoli
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


[pipeline]: https://gitlab.com/scrolliris/puteoli/badges/master/pipeline.svg
[coverage]: https://gitlab.com/scrolliris/puteoli/badges/master/coverage.svg
[commit]: https://gitlab.com/scrolliris/puteoli/commits/master
