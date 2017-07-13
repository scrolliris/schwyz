"""Reflector view actions.
"""
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from puteoli import logger
from puteoli.views import no_cache, tpl_dst


@view_config(route_name='reflector',
             renderer=tpl_dst('reflector-browser', 'js'),
             request_method='GET')
def reflector(req):
    """Returns a reflector script for valid request.
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
    req.add_response_callback(no_cache)
    return dict()


@view_config(route_name='reflector_canvas',
             request_method='GET')
def reflector_canvas(req):
    """Returns a reflector canvas for valid request.
    """
    if 'api_key' not in req.params:
        raise exc.HTTPForbidden()

    if req.matchdict['ext'] not in ('js', 'css'):
        raise exc.HTTPForbidden()

    ext = req.matchdict['ext']
    project_id = req.matchdict['project_id']
    scroll_key = req.params['api_key']

    # FIXME
    logger.info('ext -> %s', ext)
    logger.info('project_id -> %s', project_id)
    logger.info('scroll_key -> %s', scroll_key)

    result = render(tpl_dst('reflector-browser-canvas', ext), {}, req)
    res = Response(result)
    res.content_type = 'text/{0:s}'.format(
        'javascript' if ext == 'js' else 'css')
    req.add_response_callback(no_cache)
    return res
