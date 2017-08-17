"""Tracker view actions.
"""
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from puteoli import logger
from puteoli.views import no_cache, tpl_dst
from puteoli.services import IInitiator, IValidator


@view_config(route_name='tracker',
             renderer=tpl_dst('tracker-browser', 'js'),
             request_method='GET')
def tracker(req):
    """Returns a tracker script for valid request.
    """
    project_id = req.matchdict['project_id']
    api_key = req.params['api_key']

    validator = req.find_service(iface=IValidator, name='credential')
    site_id = validator.site_id
    if not site_id:
        raise exc.HTTPInternalServerError()

    initiator = req.find_service(iface=IInitiator, name='session')
    token = initiator.provision(project_id=project_id, site_id=site_id,
                                api_key=api_key, context='write')
    if not token:
        logger.error('no token')
        raise exc.HTTPInternalServerError()

    res = req.response
    res.content_type = 'text/javascript'
    req.add_response_callback(no_cache)
    return dict(token=token)
