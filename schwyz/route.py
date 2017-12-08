import pyramid.httpexceptions as exc

from schwyz import logger
from schwyz.services import IValidator


def ext_predicator_factory(ext):
    """Returns actual extension predicator."""
    def _ext_predicator(inf, _req):
        if not isinstance(ext, (list, tuple)):
            return False

        if inf['match']['ext'] not in ext:
            raise exc.HTTPForbidden()

        return True

    return _ext_predicator


def credential_predicator(inf, req):
    """Validates `project_id` and `api_key` using CredentialValidator."""
    route_name = inf['route'].name
    valid_routes = (
        'tracker',
        'minimap', 'minimap_canvas'
    )
    if route_name in valid_routes:
        if 'api_key' not in req.params:
            raise exc.HTTPForbidden()

        project_id = inf['match']['project_id']
        api_key = req.params['api_key']
        context = 'write' if route_name == 'tracker' else 'read'

        logger.info('project_id -> %s, api_key -> %s, context -> %s',
                    project_id, api_key, context)

        validator = req.find_service(iface=IValidator, name='credential')
        if not validator.validate(project_id=project_id, api_key=api_key,
                                  context=context):
            logger.error('invalid credentials')
            raise exc.HTTPNotAcceptable()

        return True

    return False


def includeme(config):
    only_javascript = ext_predicator_factory(['js'])
    both_components = ext_predicator_factory(['js', 'css'])

    # v1.0
    # -- script
    # tracker
    config.add_route(
        'tracker',
        '/script/v1.0/project/{project_id}/tracker.{ext}',
        custom_predicates=(only_javascript, credential_predicator,)
    )

    # -- widget
    # minimap (reflector)
    config.add_route(
        'minimap',
        '/widget/v1.0/project/{project_id}/minimap.{ext}',
        custom_predicates=(only_javascript, credential_predicator,)
    )
    config.add_route(
        'minimap_canvas',
        '/widget/v1.0/project/{project_id}/minimap-canvas.{ext}',
        custom_predicates=(both_components, credential_predicator,)
    )
    # overlay (reflector)
    # TODO
