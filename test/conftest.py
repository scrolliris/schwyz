"""Configuration for testing
"""
# pylint: disable=redefined-outer-name,unused-argument
import os

import pytest


# NOTE:
# The request variable in py.test is special context of testing.
# See http://doc.pytest.org/en/latest/fixture.html#request-context

# -- Shared fixtures

@pytest.fixture(scope='session')
def dotenv():
    """Loads dotenv file
    """
    from puteoli.env import Env

    # same as puteoli:main
    dotenv_file = os.path.join(os.getcwd(), '.env')
    Env.load_dotenv_vars(dotenv_file)

    return


@pytest.fixture(scope='session')
def env(dotenv):
    """Returns env object
    """
    from puteoli.env import Env
    return Env()


@pytest.fixture(scope='session')
def raw_settings(dotenv):
    """Returns raw setting dict
    """
    from pyramid.paster import get_appsettings

    ini_file = os.path.join(os.getcwd(), 'config/testing.ini#puteoli')
    return get_appsettings(ini_file)


@pytest.fixture(scope='session')
def resolve_settings():
    """Returns resolving function for settings
    """
    def _resolve_settings(raw_s):
        # pass
        return raw_s

    return _resolve_settings


@pytest.fixture(scope='session')
def settings(raw_settings, resolve_settings):
    """Returns (environ) resolved settings
    """
    return resolve_settings(raw_settings)


@pytest.fixture(scope='session')
def extra_environ(env):
    """Returns extra environ object
    """
    environ = {
        'SERVER_PORT': '80',
        'REMOTE_ADDR': '127.0.0.1',
        'wsgi.url_scheme': 'http',
    }
    return environ


# auto fixtures

@pytest.yield_fixture(autouse=True, scope='session')
def session_helper():
    """A helper function for session scope
    """
    yield


@pytest.yield_fixture(autouse=True, scope='module')
def module_helper(settings):
    """A helper function for module scope
    """
    yield


@pytest.yield_fixture(autouse=True, scope='function')
def function_helper():
    """A helper function for function scope
    """
    yield


# -- View tests

@pytest.fixture(scope='session')
def config(request, settings):
    """Returns the testing config
    """
    from pyramid import testing

    config = testing.setUp(settings=settings)

    # FIXME:
    #    these includings from .ini file are not evaluated
    #    in unit tests.
    config.include('pyramid_assetviews')
    config.include('pyramid_mako')
    config.include('pyramid_services')

    config.include('puteoli.services')
    config.include('puteoli.views')

    config.include('puteoli.route')

    # FIXME:
    #    these includings from .ini file are not evaluated
    #    in unit tests.
    # config.include('pyramid_mako')

    def teardown():
        """The teardown function
        """
        testing.tearDown()

    request.addfinalizer(teardown)

    return config


@pytest.fixture(scope='function')
def dummy_request(extra_environ):
    """Returns Dummy request object
    """
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


# -- Functional tests

@pytest.fixture(scope='session')
def _app(raw_settings):
    """Returns the internal app of app for testing
    """
    from puteoli import main
    global_config = {
        '__file__': raw_settings['__file__']
    }
    del raw_settings['__file__']

    return main(global_config, **raw_settings)


@pytest.fixture(scope='session')
def dummy_app(_app, extra_environ):
    """Returns a dummy test app
    """
    from webtest import TestApp

    return TestApp(_app, extra_environ=extra_environ)