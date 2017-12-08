from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from schwyz import logger
from schwyz.views import no_cache, tpl_dst
from schwyz.services import IInitiator, IValidator


@view_config(route_name='minimap',
             renderer=tpl_dst('minimap-browser', 'js'),
             request_method='GET')
def minimap(req):
    """Returns just a minimap widget for valid request."""
    # version 1.0
    res = req.response
    res.content_type = 'text/javascript'
    req.add_response_callback(no_cache)
    # TODO:
    # Use CDN
    return dict()


@view_config(route_name='minimap_canvas',
             request_method='GET')
def minimap_canvas(req):
    """Returns a minimap canvas for valid request."""
    if req.matchdict['ext'] not in ('js', 'css'):
        raise exc.HTTPForbidden()

    # version 1.0
    project_id = req.matchdict['project_id']
    api_key = req.params['api_key']
    ext = req.matchdict['ext']

    validator = req.find_service(iface=IValidator, name='credential')
    site_id = validator.site_id
    if not site_id:
        raise exc.HTTPInternalServerError()

    initiator = req.find_service(iface=IInitiator, name='session')
    token = initiator.provision(project_id=project_id, site_id=site_id,
                                api_key=api_key, context='read')
    if not token:
        logger.error('no token')
        raise exc.HTTPInternalServerError()
    # minified
    result = render(tpl_dst('minimap-canvas', ext), dict(token=token), req)
    res = Response(result)
    res.content_type = 'text/{0:s}'.format(
        'javascript' if ext == 'js' else 'css')
    req.add_response_callback(no_cache)
    return res
