"""Puteoli Application.
"""
import logging
from os import path
import sys
from wsgiref.handlers import BaseHandler

from paste.translogger import TransLogger
from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry
import pyramid.httpexceptions as exc

from .env import Env

# -- configurations

STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), '../static')


# pylint: disable=protected-access
def ignore_broken_pipes(self):
    """Ignores unused error message about broken pipe.
    """
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
    """Returns settings from current ini.
    """
    return get_current_registry().settings


def resolve_env_vars(settings):
    """Loads environment variables into settings
    """
    env = Env()
    s = settings.copy()
    for k, v in env.settings_mappings.items():
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
    """The main function.
    """
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

    def project_id_predicator(info, request):
        """Validates `project_id` parameter.
        """
        if info['route'].name in ('tracker', 'reflector', 'reflector_canvas'):
            # FIXME:
            return info['match']['project_id'] == 'development'

    config.scan('.request')

    if env.get('VIEW_TYPE') == 'tracker':
        config.add_route(
            'tracker',
            '/projects/{project_id}/tracker.js',
            custom_predicates=(project_id_predicator,)
        )
        config.include('.views.tracker')
        config.scan('.views.tracker')

    if env.get('VIEW_TYPE') == 'reflector':
        config.add_route(
            'reflector',
            '/projects/{project_id}/reflector.js',
            custom_predicates=(project_id_predicator,)
        )
        config.add_route(
            'reflector_canvas',
            '/projects/{project_id}/reflector-canvas.{ext}',
            custom_predicates=(project_id_predicator,)
        )
        config.include('.views.reflector')
        config.scan('.views.reflector')

    app = config.make_wsgi_app()
    app = TransLogger(app, setup_console_handler=False)
    return app