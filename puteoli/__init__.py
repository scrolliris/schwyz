"""Puteoli Application.
"""
import logging
from os import path
import sys
from wsgiref.handlers import BaseHandler

from paste.translogger import TransLogger
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.view import forbidden_view_config, notfound_view_config
import pyramid.httpexceptions as exc

from .env import Env

# -- configurations

STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), '../static')


def ignore_broken_pipes(self):
    """Ignores unused error message about broken pipe.
    """
    if sys.exc_info()[0] != BrokenPipeError:
        BaseHandler.__handle_error_original_(self)


BaseHandler.__handle_error_original_ = BaseHandler.handle_error
BaseHandler.handle_error = ignore_broken_pipes

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
logger.setLevel(logging.INFO)

sh = logging.StreamHandler()  # pylint: disable=invalid-name
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(sh)


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


def tpl(filename):
    """HTML Template Utility.
    """
    return './templates/{0:s}.mako'.format(filename)


def tpl_js(filename):
    """JS Template Utility.
    """
    return STATIC_DIR + '/dist/{0:s}.min.js.mako'.format(filename)


# -- views


@notfound_view_config(renderer=tpl('404'),
                      append_slash=exc.HTTPMovedPermanently)
def notfound(req):
    """404 Not Found Error.
    """
    req.response.status = 404
    return dict()


@forbidden_view_config(renderer=tpl('403'))
def forbidden(req):
    """403 Forbidden Error.
    """
    req.response.status = 403
    return dict()


@view_config(context=exc.HTTPInternalServerError, renderer='string')
def internal_server_error(req):
    """Internal Server Error.
    """
    body = 'Cannot {} {}'.format(req.method, req.path)
    return Response(body, status='500 Internal Server Error')


@view_config(route_name='tracker',
             renderer=tpl_js('tracker-browser'),
             request_method='GET')
def tracker(req):
    """Returns a tracker script for valid request.
    """
    if 'api_key' not in req.params:
        raise exc.HTTPForbidden()

    project_id = req.matchdict['project_id']
    scroll_key = req.params['api_key']

    # FIXME
    logger.info('project_id -> %s', project_id)
    logger.info('scroll_key -> %s', scroll_key)

    res = req.response
    res.content_type = 'text/javascript'
    res.headers['Cache-Control'] = 'no-cache,no-store,must-revalidate'
    res.headers['Pragma'] = 'no-cache'
    res.headers['Expires'] = '0'
    return dict()


# -- main


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
        if info['route'].name in ('tracker', 'reflector'):
            # FIXME:
            return info['match']['project_id'] == 'development'

    config.add_route(
        'tracker',
        '/projects/{project_id}/tracker.js',
        custom_predicates=(project_id_predicator,)
    )

    config.scan()
    app = config.make_wsgi_app()
    app = TransLogger(app, setup_console_handler=False)
    return app
