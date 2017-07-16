# pylint: disable=inherit-non-class,no-self-argument,no-method-argument
"""Service package.
"""
import base64
import datetime
import logging
import uuid

import boto3
from boto3.dynamodb.conditions import Attr
from zope.interface import Attribute, Interface


class IValidator(Interface):
    """Interface as validator service.
    """
    # pylint: disable=missing-docstring

    def validate():
        pass


class IInitiator(Interface):
    """Interface as initiator service.
    """
    # pylint: disable=missing-docstring

    def provision():
        pass


class ContextError(Exception):
    """Custom error class for session context.
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class BaseServiceObject(object):  # pylint: disable=too-few-public-methods
    """Service for session provision.
    """
    def __init__(self, *_, **kwargs):
        session = boto3.session.Session(
            aws_access_key_id=kwargs['aws_access_key_id'],
            aws_secret_access_key=kwargs['aws_secret_access_key']
        )
        options = {
            'use_ssl': True,
            'region_name': kwargs['region_name']
        }
        if kwargs.get('endpoint_url', ''):
            options['endpoint_url'] = kwargs['endpoint_url']
        self.db = session.resource('dynamodb', **options)
        self.table = self.db.Table(kwargs['table_name'])


class CredentialValidator(BaseServiceObject):
    """CredentialValidator Service.
    """
    @classmethod
    def options(cls, settings):
        """Returns options for this initiator.
        """
        return {
            'aws_access_key_id': settings['aws.access_key_id'],
            'aws_secret_access_key': settings['aws.secret_access_key'],
            'region_name': settings['db.region_name'],
            'endpoint_url': settings['db.endpoint_url'],
            'table_name': settings['db.credential_table_name'],
        }

    def validate(self, project_id, api_key, context='read'):
        """Validates project_id and api_key.
        """
        if context not in ('read', 'write'):
            raise ContextError('invalid context {0:s}'.format(context))

        res = self.table.get_item(Key={
            'project_id': project_id,
        })
        item = res['Item'] if 'Item' in res else None
        key = '{0:s}_key'.format(context)  # {read|write}_key
        if item and key in item:
            return api_key == item[key]
        return False



class SessionInitiator(BaseServiceObject):
    """SessionInitiator Service.
    """
    @classmethod
    def options(cls, settings):
        """Returns options for this initiator.
        """
        return {
            'aws_access_key_id': settings['aws.access_key_id'],
            'aws_secret_access_key': settings['aws.secret_access_key'],
            'region_name': settings['db.region_name'],
            'endpoint_url': settings['db.endpoint_url'],
            'table_name': settings['db.session_table_name'],
        }

    @classmethod
    def generate_token(cls):
        """Generates uuid4 based token.
        """
        return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')

    @classmethod
    def generate_timestamp(cls):
        """Generates Unix Timestamp int in UTC.

        NOTE:
          `datetime.utcnow().timestamp()` is invalid, because `timestamp()`
          method assumes that time object has local time.
        """
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def provision(self, project_id='', api_key='', context='read'):
        """Save new session record.
        """
        if context not in ('read', 'write'):
            raise ContextError('invalid context {0:s}'.format(context))

        token = self.__class__.generate_token()
        try:
            self.table.put_item(Item={
                'token': token,
                'initiated_at': self.__class__.generate_timestamp(),
                'project_id': project_id,
                'context': context,
                'api_key': api_key,
            })
        except Exception as e:  # pylint: disable=broad-except
            logger = logging.getLogger(__name__)
            logger.error('session provisioning error -> %s', e)
        return token


def credential_validator_factory():
    """The credential validator service factory.
    """

    def _credential_validator(_, req):
        """Actual validator factory method.
        """
        options = CredentialValidator.options(req.settings)
        return CredentialValidator(req, **options)

    return _credential_validator


def session_initiator_factory():
    """The session initiator service factory.
    """

    def _session_initiator(_, req):
        """Actual initiator factory method.
        """
        options = SessionInitiator.options(req.settings)
        return SessionInitiator(req, **options)

    return _session_initiator


def includeme(config):
    """Initializes service objects.
    """
    config.register_service_factory(
        credential_validator_factory(),
        iface=IValidator,
        name='credential')
    config.register_service_factory(
        session_initiator_factory(),
        iface=IInitiator,
        name='session')
