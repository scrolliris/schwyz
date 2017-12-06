import logging
from os import path
import sys
from wsgiref.handlers import BaseHandler

from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry

from schwyz.env import Env

# -- configurations

STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), '../static')


# pylint: disable=protected-access
def ignore_broken_pipes(self):
    """Ignores unused error message about broken pipe."""
    if sys.exc_info()[0] != BrokenPipeError:
        BaseHandler.__handle_error_original_(self)


BaseHandler.__handle_error_original_ = BaseHandler.handle_error
BaseHandler.handle_error = ignore_broken_pipes
# pylint: enable=protected-access

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(sh)
# pylint: enable=invalid-name


def get_settings():
    return get_current_registry().settings


def resolve_env_vars(settings):
    env = Env()
    s = settings.copy()
    for k, v in Env.settings_mappings().items():
        # ignores missing key or it has a already value in config
        if k not in s or s[k]:
            continue
        new_v = env.get(v, None)
        if not isinstance(new_v, str):
            continue
        # ignores empty string
        if ',' in new_v:
            s[k] = [nv for nv in new_v.split(',') if nv != '']
        elif new_v:
            s[k] = new_v
    return s


def main(_, **settings):
    from .request import CustomRequest

    env = Env()

    config = Configurator(settings=resolve_env_vars(settings))
    config.set_request_factory(CustomRequest)

    # routes
    # static files at /*
    filenames = [f for f in ('robots.txt', 'humans.txt')
                 if path.isfile((STATIC_DIR + '/{}').format(f))]
    if filenames:
        cache_max_age = 3600 if env.is_production else 0
        config.add_asset_views(
            STATIC_DIR, filenames=filenames, http_cache=cache_max_age)

    config.scan('.request')
    config.include('.services')

    config.include('.route')

    app = config.make_wsgi_app()
    # from paste.translogger import TransLogger
    # app = TransLogger(app, setup_console_handler=False)
    return app
