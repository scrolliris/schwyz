ifeq (, $(ENV))
	env := development
else ifeq (test, $(ENV))
	env := testing
else
	env := $(ENV)
endif

app := schwyz

# -- installation

setup:
	pip install -e '.[${env}]' -c constraints.txt
.PHONY: setup

# -- database

db-init:
	${app}_manage 'config/${env}.ini#${app}' db init
.PHONY: db-init

ds-seed:
	${app}_manage 'config/${env}.ini#${app}' ds seed
.PHONY: ds-seed

# -- application

serve:
	./bin/serve --env ${env} --config config/${env}.ini --reload
.PHONY: serve

# -- testing

test:
	ENV=test py.test -c 'config/testing.ini' -q
.PHONY: test

test-cov:
	ENV=test py.test -c 'config/testing.ini' -q --cov=${app} \
	  --cov-report term-missing:skip-covered
.PHONY: test-cov

cov: | test-cov
.PHONY: cov

test-coverage:
	ENV=test py.test -c 'config/testing.ini' -q --cov=${app} \
	  --cov-report term-missing \
	  --cov-report html:tmp/coverage
.PHONY: test-coverage

coverage: | test-coverage
.PHONY: coverage

# -- utility

check:
	flake8
.PHONY: check

lint:
	pylint test ${app}
.PHONY: lint

vet: | check lint
.PHONY: vet

build:
ifeq (, $(shell which gulp 2>/dev/null))
	$(info gulp command not found. run `npm install -g gulp-cli`)
	$(info )
else
	NODE_ENV=$(NODE_ENV) gulp
endif
.PHONY: build

clean:
	find . ! -readable -prune -o \
	  ! -path "./.git/*" ! -path "./node_modules/*" ! -path "./venv*" \
	  ! -path "./doc/*" ! -path "./locale/*" ! -path "./tmp/*" \
	  ! -path "./lib/*" -print | \
	  grep -E "(__pycache__|\.egg-info|\.pyc|\.pyo)" | \
	  xargs rm -rf
ifneq (, $(shell which gulp 2>/dev/null))
	gulp clean
endif
.PHONY: clean

.DEFAULT_GOAL = coverage
default: coverage
