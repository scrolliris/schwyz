# pylint: disable=inherit-non-class,no-self-argument,no-method-argument
from __future__ import absolute_import
import base64
import logging
import os
import re
import sys
import uuid

import boto3
import redis
from zope.interface import Interface


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


class BaseRedisServiceObject(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, *args, **_kwargs):
        req = args[0]
        pool = redis.ConnectionPool.from_url(req.settings['store.url'])
        self.client = redis.Redis(connection_pool=pool)


class CredentialValidator(BaseRedisServiceObject):
    def __init__(self, *args, **kwargs):
        self.site_id = None

        if sys.version_info[0] > 3:
            # pylint: disable=missing-super-argument
            super().__init__(*args, **kwargs)
        else:
            super(CredentialValidator, self).__init__(*args, **kwargs)

    @classmethod
    def options(cls, settings):
        return {
            'store.url': settings['store.url']
        }

    def validate(self, project_id='', api_key='', ctx='read'):
        """Validates project_id and api_key."""
        if ctx not in ('read', 'write'):
            raise ContextError('invalid ctx {0:s}'.format(ctx))

        name = '{}-{}'.format(project_id, ctx)
        site_id = self.client.hget(name, api_key)

        if site_id is None:
            logger = logging.getLogger(__name__)
            logger.error('api_key is missing: %s', api_key)
            return False

        # cache site_id for views
        self.site_id = site_id.decode()
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
        import time

        # NOTE:
        # this method returns unix timestamp in seconds.
        #
        # >>> dt = datetime.datetime.now(tz=pytz.utc)
        # >>> time.mktime(dt.timetuple())
        # 1512592023.0
        #
        # only in python 3
        # >>> dt.timestamp()
        # 1512624423.035536
        dt = datetime.datetime.now(tz=pytz.utc)
        return int(time.mktime(dt.timetuple()))

    def provision(self, project_id='', site_id='', api_key='', ctx='read'):
        if ctx not in ('read', 'write'):
            raise ContextError('invalid ctx {0:s}'.format(ctx))

        token = self.__class__.generate_token()
        try:
            self.table.put_item(Item={
                'token': token,
                'initiated_at': self.__class__.generate_timestamp(),
                'project_id': project_id,
                'site_id': site_id,
                'context': ctx,
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
