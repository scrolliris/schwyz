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
        'measure',  # ctx: write
        'heatmap', 'heatmap_minimap', 'heatmap_overlay'  # ctx: read
    )
    if route_name in valid_routes:
        if 'api_key' not in req.params:
            raise exc.HTTPForbidden()

        project_id = inf['match']['project_id']
        api_key = req.params['api_key']
        ctx = 'write' if route_name == 'measure' else 'read'

        logger.info('project_id -> %s, api_key -> %s, ctx -> %s',
                    project_id, api_key, ctx)

        validator = req.find_service(iface=IValidator, name='credential')
        if not validator.validate(
                project_id=project_id, api_key=api_key, ctx=ctx):
            logger.error('invalid credentials')
            raise exc.HTTPNotAcceptable()

        return True

    return False


def includeme(config):
    only_javascript = ext_predicator_factory(['js'])
    both_components = ext_predicator_factory(['js', 'css'])

    # latest
    # v1.0

    # [v1.0]
    # -- script / tracker
    # measure (scrolliris-readability-tracker)
    config.add_route(
        'measure',
        '/script/v1.0/projects/{project_id}/measure.{ext}',
        custom_predicates=(only_javascript, credential_predicator,)
    )

    # -- widget / reflector
    # heatmap (scrolliris-readability-reflector)
    config.add_route(
        'heatmap',
        '/widget/v1.0/projects/{project_id}/heatmap.{ext}',
        custom_predicates=(only_javascript, credential_predicator,)
    )
    # addon:type: heatmap-minimap (widget: frame)
    config.add_route(
        'heatmap_minimap',
        '/widget/v1.0/projects/{project_id}/heatmap-minimap.{ext}',
        custom_predicates=(both_components, credential_predicator,)
    )
    # addon:type: heatmap-overlay (widget: layer)
    config.add_route(
        'heatmap_overlay',
        '/widget/v1.0/projects/{project_id}/heatmap-overlay.{ext}',
        custom_predicates=(both_components, credential_predicator,)
    )

    # -- plugin
    # badge: coverage (through winterthur)
    # TODO: /plugin/v1.0/project/{project_id}/coverage.svg?type=ratio
    # TODO: /plugin/v1.0/project/{project_id}/coverage.svg?type=score

    # badge: tracking (through st.gallen)
    # TODO: /plugin/v1.0/project/{project_id}/tracking.svg
