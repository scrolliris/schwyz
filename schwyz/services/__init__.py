# pylint: disable=inherit-non-class,no-self-argument,no-method-argument
from __future__ import absolute_import
import base64
import logging
import os
import re
import sys
import uuid

import boto3
from zope.interface import Interface

try:
    # TODO:
    # Remove this, if this namespace issue is fixed.
    # It's related to:
    # * https://github.com/PyCQA/pylint/issues/1686
    # * https://github.com/PyCQA/astroid/pull/460
    #
    # NOTE:
    # A fix using `.pylintrc`
    # init-hook='import sys; sys.path.append(
    #     "venv27/lib/python2.7/site-packages/google/cloud/")'
    from google.cloud import datastore
except ImportError:
    pass


class IValidator(Interface):
    # pylint: disable=missing-docstring

    def validate():
        pass


class IInitiator(Interface):
    # pylint: disable=missing-docstring

    def provision():
        pass


class ContextError(Exception):
    def __init__(self, value):
        if sys.version_info[0] > 3:
            # pylint: disable=missing-super-argument
            super().__init__()
        else:
            super(ContextError, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class BaseDynamoDBServiceObject(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, *_, **kwargs):
        session = boto3.session.Session(
            aws_access_key_id=kwargs['aws_access_key_id'],
            aws_secret_access_key=kwargs['aws_secret_access_key']
        )
        options = {
            'use_ssl': True,
            'region_name': kwargs['region_name']
        }
        if 'endpoint_url' in kwargs and kwargs['endpoint_url']:
            options['endpoint_url'] = kwargs['endpoint_url']
        self.db = session.resource('dynamodb', **options)
        self.table = self.db.Table(kwargs['table_name'])


class BaseDatastoreServiceObject(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, *_, **kwargs):
        if kwargs['credentials']:
            # https://google-cloud-python.readthedocs.io/en/latest/core/auth.html#service-accounts
            self.client = datastore.Client.from_service_account_json(
                kwargs['credentials'])
        else:
            self.client = datastore.Client()
        self.kind = kwargs['kind']


class CredentialValidator(BaseDatastoreServiceObject):
    def __init__(self, *args, **kwargs):
        self.site = None
        if sys.version_info[0] > 3:
            # pylint: disable=missing-super-argument
            super().__init__(*args, **kwargs)
        else:
            super(CredentialValidator, self).__init__(*args, **kwargs)

    @classmethod
    def options(cls, settings):
        # credentials file must be in lib
        credentials = ''
        if settings['gcp.account_credentials']:
            credentials = '{}/{}'.format(
                os.path.dirname(__file__) + '/../../lib',
                os.path.basename(settings['gcp.account_credentials']))
        _options = {
            'credentials': credentials,
            'kind': settings['datastore.entity_kind'],
        }
        if 'datastore.emulator_host' in settings and \
           settings['datastore.emulator_host']:
            _options['emulator_host'] = settings['datastore.emulator_host']
        return _options

    @property
    def site_id(self):
        site = self.site
        if not isinstance(site, datastore.Entity):
            return None
        try:
            return int(re.sub(r'^(\d*)-(\d*)$', r'\2', site.key.name))
        except Exception as e:  # pylint: disable=broad-except
            logger = logging.getLogger(__name__)
            logger.error('site_id is missing-> %s, site: %s', e, site)
            return None

    def validate(self, project_id='', api_key='', context='read'):
        """Validates project_id (project_access_key_id) and api_key."""
        if context not in ('read', 'write'):
            raise ContextError('invalid context {0:s}'.format(context))

        sites = []
        try:
            query = self.client.query(kind=self.kind)
            query.add_filter('project_access_key_id', '=', project_id)
            query.add_filter('{0:s}_key'.format(context), '=', api_key)
            query.keys_only()
            sites = list(query.fetch() or ())
        except Exception as e:  # pylint: disable=broad-except
            logger = logging.getLogger(__name__)
            logger.error('session provisioning error -> %s', e)
            return None

        if len(sites) != 1:
            return False

        # set site after view
        self.site = sites[0]
        return True


class SessionInitiator(BaseDynamoDBServiceObject):
    @classmethod
    def options(cls, settings):
        _options = {
            'aws_access_key_id': settings['aws.access_key_id'],
            'aws_secret_access_key': settings['aws.secret_access_key'],
            'region_name': settings['dynamodb.region_name'],
            'table_name': settings['dynamodb.table_name'],
        }
        if settings['dynamodb.endpoint_url']:
            _options['endpoint_url'] = settings['dynamodb.endpoint_url']
        return _options

    @classmethod
    def generate_token(cls):
        return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')

    @classmethod
    def generate_timestamp(cls):
        """Generates Unix Timestamp int in UTC.

        NOTE:
          `datetime.utcnow().timestamp()` is invalid, because `timestamp()`
          method assumes that time object has local time.
        """
        import datetime
        import pytz

        def utcnow():
            return datetime.datetime.now(tz=pytz.utc)

        return int(utcnow().timestamp())

    def provision(self, project_id='', site_id='', api_key='', context='read'):
        if context not in ('read', 'write'):
            raise ContextError('invalid context {0:s}'.format(context))

        token = self.__class__.generate_token()
        try:
            self.table.put_item(Item={
                'token': token,
                'initiated_at': self.__class__.generate_timestamp(),
                'project_id': project_id,
                'site_id': site_id,
                'context': context,
                'api_key': api_key,
            })
        except Exception as e:  # pylint: disable=broad-except
            logger = logging.getLogger(__name__)
            logger.error('session provisioning error -> %s', e)
            return None
        return token


def credential_validator_factory():
    def _credential_validator(_, req):
        options = CredentialValidator.options(req.settings)
        return CredentialValidator(req, **options)

    return _credential_validator


def session_initiator_factory():
    def _session_initiator(_, req):
        options = SessionInitiator.options(req.settings)
        return SessionInitiator(req, **options)

    return _session_initiator


def includeme(config):
    config.register_service_factory(
        credential_validator_factory(),
        iface=IValidator,
        name='credential')
    config.register_service_factory(
        session_initiator_factory(),
        iface=IInitiator,
        name='session')
