# pylint: disable=redefined-outer-name,unused-argument
import os

import pytest

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
from webtest.app import TestApp

# NOTE:
# The request variable in py.test is special context of testing.
# See http://doc.pytest.org/en/latest/fixture.html#request-context

TEST_DIR = os.path.dirname(__file__)
INI_FILE = os.path.join(TEST_DIR, '..', 'config', 'testing.ini')


@pytest.fixture(scope='session')
def dotenv() -> None:
    from schwyz.env import load_dotenv_vars

    # same as schwyz:main
    dotenv_file = os.path.join(TEST_DIR, '..', '.env')
    load_dotenv_vars(dotenv_file)
    return


@pytest.fixture(scope='session')
def env(dotenv) -> dict:
    from schwyz.env import Env

    return Env()


@pytest.fixture(scope='session')
def raw_settings(dotenv) -> dict:
    from pyramid.paster import get_appsettings

    return get_appsettings('{0:s}#{1:s}'.format(INI_FILE, 'schwyz'))


@pytest.fixture(scope='session')
def resolve_settings() -> 'function':
    def _resolve_settings(raw_s):
        return raw_s

    return _resolve_settings


@pytest.fixture(scope='session')
def settings(raw_settings, resolve_settings) -> 'function':
    return resolve_settings(raw_settings)


@pytest.fixture(scope='session')
def extra_environ(env) -> dict:
    environ = {
        'SERVER_PORT': '80',
        'REMOTE_ADDR': '127.0.0.1',
        'wsgi.url_scheme': 'http',
    }
    return environ


@pytest.yield_fixture(autouse=True, scope='session')
def session_helper() -> None:
    yield


@pytest.yield_fixture(autouse=True, scope='module')
def module_helper(settings) -> None:
    yield


@pytest.yield_fixture(autouse=True, scope='function')
def function_helper() -> None:
    yield


@pytest.fixture(scope='session')
def config(request, settings) -> Configurator:
    from pyramid import testing

    config = testing.setUp(settings=settings)

    config.include('pyramid_assetviews')
    config.include('pyramid_mako')
    config.include('pyramid_services')

    config.include('schwyz.services')
    config.include('schwyz.views')

    config.include('schwyz.route')

    def teardown() -> None:
        """The teardown function
        """
        testing.tearDown()

    request.addfinalizer(teardown)

    return config


@pytest.fixture(scope='function')
def dummy_request(extra_environ) -> Request:
    from pyramid import testing
    from pyramid_services import find_service
    from zope.interface.adapter import AdapterRegistry

    locale_name = 'en'
    req = testing.DummyRequest(
        subdomain='',
        environ=extra_environ,
        _LOCALE_=locale_name,
        locale_name=locale_name,
        matched_route=None)

    # for service objects
    req.service_cache = AdapterRegistry()
    req.find_service = (lambda *args, **kwargs:
                        find_service(req, *args, **kwargs))
    return req


@pytest.fixture(scope='session')
def _app(raw_settings) -> Router:
    from schwyz import main

    global_config = {
        '__file__': INI_FILE
    }
    if '__file__' in raw_settings:
        del raw_settings['__file__']

    return main(global_config, **raw_settings)


@pytest.fixture(scope='session')
def dummy_app(_app, extra_environ) -> TestApp:
    return TestApp(_app, extra_environ=extra_environ)
