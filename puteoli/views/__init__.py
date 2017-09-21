"""Views.
"""
from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    notfound_view_config,
    view_config,
)
import pyramid.httpexceptions as exc

from puteoli import STATIC_DIR


def tpl(filename):
    """HTML Template Utility.
    """
    return 'puteoli:templates/{0:s}.mako'.format(filename)


def tpl_dst(filename, extname='js'):
    """{JS|CSS} Template Utility.
    """
    return STATIC_DIR + '/dst/{0:s}.min.{1:s}.mako'.format(filename, extname)


def no_cache(_request, response):
    """Sets no-cache using cache_control
    """
    response.pragma = 'no-cache'
    response.expires = '0'
    response.cache_control = 'no-cache,no-store,must-revalidate'


# -- errors

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


def includeme(config):
    """Initializes the view for puteoli

    Activate this setup using ``config.include('puteoli.views')``.
    """
    # see route.py
    # config.include('.tracker')
    # config.include('.reflector')
    pass
