"""Reflector view actions.
"""
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from puteoli import logger
from puteoli.views import no_cache, tpl_dst
from puteoli.services import IInitiator


@view_config(route_name='reflector',
             renderer=tpl_dst('reflector-browser', 'js'),
             request_method='GET')
def reflector(req):
    """Returns just a reflector script for valid request.
    """
    res = req.response
    res.content_type = 'text/javascript'
    req.add_response_callback(no_cache)
    return dict()


@view_config(route_name='reflector_canvas',
             request_method='GET')
def reflector_canvas(req):
    """Returns a reflector canvas for valid request.
    """
    if req.matchdict['ext'] not in ('js', 'css'):
        raise exc.HTTPForbidden()

    project_id = req.matchdict['project_id']
    api_key = req.params['api_key']
    ext = req.matchdict['ext']

    initiator = req.find_service(iface=IInitiator, name='session')
    token = initiator.provision(project_id=project_id, api_key=api_key,
                                context='read')
    if not token:
        logger.error('no token')
        raise exc.HTTPInternalServerError()

    result = render(tpl_dst('reflector-canvas', ext), {}, req)
    res = Response(result)
    res.content_type = 'text/{0:s}'.format(
        'javascript' if ext == 'js' else 'css')
    req.add_response_callback(no_cache)
    return res
