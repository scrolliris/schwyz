"""Route package.
"""
import pyramid.httpexceptions as exc

from . import logger, Env
from .services import IValidator


def ext_predicator_factory(ext):
    """Returns actual extension predicator.
    """
    def _ext_predicator(inf, _req):
        """Validates `ext`.
        """
        if not isinstance(ext, (list, tuple)):
            return False

        if inf['match']['ext'] not in ext:
            raise exc.HTTPForbidden()

        return True

    return _ext_predicator


def credential_predicator(inf, req):
    """Validates `project_id` and `api_key` using CredentialValidator.
    """
    if inf['route'].name in ('tracker', 'reflector', 'reflector_canvas'):
        if 'api_key' not in req.params:
            raise exc.HTTPForbidden()

        project_id = inf['match']['project_id']
        api_key = req.params['api_key']
        context = 'write' if inf['route'] == 'tracker' else 'read'

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
    """Initializes routes.
    """
    env = Env()
    js_predicator = ext_predicator_factory(['js'])

    if env.get('VIEW_TYPE') == 'tracker':
        config.add_route(
            'tracker',
            '/projects/{project_id}/tracker.{ext}',
            custom_predicates=(js_predicator, credential_predicator,)
        )
        config.scan('.views.tracker')
        config.include('.views.tracker')

    if env.get('VIEW_TYPE') == 'reflector':
        asset_preficator = ext_predicator_factory(['js', 'css'])

        config.add_route(
            'reflector',
            '/projects/{project_id}/reflector.{ext}',
            custom_predicates=(js_predicator, credential_predicator,)
        )
        config.add_route(
            'reflector_canvas',
            '/projects/{project_id}/reflector-canvas.{ext}',
            custom_predicates=(asset_preficator, credential_predicator,)
        )
        config.scan('.views.reflector')
        config.include('.views.reflector')
