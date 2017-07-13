# Puteoli

`/p(j)utɪ́ːəlɑ̀ɪ/`

[![build status](https://gitlab.com/lupine-software/puteoli/badges/master/build.svg)](
https://gitlab.com/lupine-software/puteoli/commits/master) [![coverage report](
https://gitlab.com/lupine-software/puteoli/badges/master/coverage.svg)](
https://gitlab.com/lupine-software/puteoli/commits/master)

```txt
 , __                     _
/|/  \                   | | o
 |___/      _|_  _   __  | |
 |    |   |  |  |/  /  \_|/  |
 |     \_/|_/|_/|__/\__/ |__/|_/

Puteoli; uPstrem UTility & widgEt hOsting appLIcation
```

[https://gitlab.com/lupine-software/puteoli](
https://gitlab.com/lupine-software/puteoli)


## Requirements

* Python `3.5.0`
* Node.js `7.8.0` (build)


## Setup

```zsh
: setup python environment (e.g. virtualenv)
% python3.5 -m venv venv
% source venv/bin/activate
(venv) % pip install --upgrade pip setuptools

: node.js (e.g. nodeenv)
(venv) % pip install nodeenv
(venv) % nodeenv --python-virtualenv --with-npm --node=7.8.0
: re-activate for node.js at this time
(venv) % source venv/bin/activate
(venv) % npm --version
5.3.0
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

At first, setup for production environment.

```zsh
: e.g. use google app engine
(venv) % curl -sLO https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-157.0.0-linux-x86_64.tar.gz

: check sha256 checksum
(venv) % sha256sum google-cloud-sdk-157.0.0-linux-x86_64.tar.gz
95b98fc696f38cd8b219b4ee9828737081f2b5b3bd07a3879b7b2a6a5349a73f  google-cloud-sdk-157.0.0-linux-x86_64.tar.gz

(venv) % tar zxvf google-cloud-sdk-157.0.0-linux-x86_64.tar.gz

: we don\'t install this global environment even if development
(venv) % CLOUDSDK_ROOT_DIR=. ./google-cloud-sdk/install.sh

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

Puteoli; Copyright (c) 2017 Lupine Software, LLC.


This is free software;  
You can redistribute it and/or modify it under the terms of the
GNU Affero General Public License (AGPL).

See [LICENSE](LICENSE).