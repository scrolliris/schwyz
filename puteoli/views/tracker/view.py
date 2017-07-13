"""Tracker view actions.
"""
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from puteoli import logger
from puteoli.views import no_cache, tpl_dst


@view_config(route_name='tracker',
             renderer=tpl_dst('tracker-browser', 'js'),
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
    req.add_response_callback(no_cache)
    return dict()
