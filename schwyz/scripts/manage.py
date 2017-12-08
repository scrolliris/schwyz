from __future__ import absolute_import, print_function
import os
import sys

import boto3

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

from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from schwyz import resolve_env_vars
from schwyz.env import load_dotenv_vars


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <command> <action> [var=value]\n'
          '(example: "%s \'development.ini#\' db seed")' % (cmd, cmd))
    sys.exit(1)


class DbCli(object):
    def __init__(self, settings):
        self.settings = settings

    def init(self):
        session = boto3.session.Session(
            aws_access_key_id=self.settings['aws.access_key_id'],
            aws_secret_access_key=self.settings['aws.secret_access_key']
        )
        options = {
            'use_ssl': True,
            'region_name': self.settings['dynamodb.region_name']
        }
        if self.settings.get('dynamodb.endpoint_url', ''):
            options['endpoint_url'] = self.settings['dynamodb.endpoint_url']
        db = session.resource('dynamodb', **options)
        table_name = self.settings['dynamodb.table_name']
        table = db.Table(table_name)
        try:
            db.create_table(
                TableName=table_name,
                KeySchema=[{
                    'AttributeName': 'token',
                    'KeyType': 'HASH',
                }, {
                    'AttributeName': 'initiated_at',
                    'KeyType': 'RANGE',
                }],
                AttributeDefinitions=[{
                    'AttributeName': 'token',
                    'AttributeType': 'S'
                }, {
                    'AttributeName': 'initiated_at',
                    'AttributeType': 'N'
                }],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            table.meta.client.get_waiter('table_exists').wait(
                TableName=table_name)  # pylint: disable=no-member
            print('table was created: {0!s}'.format(table.creation_date_time))
        except Exception as e:  # pylint: disable=broad-except
            print(e)
            print('check configuration')
            exit(1)


class DsCli(object):
    def __init__(self, settings):
        self.settings = settings

    def seed(self):
        client = datastore.Client()
        with client.transaction():
            site_key = client.key(
                self.settings['datastore.entity_kind'], '1-1')
            obj = datastore.Entity(key=site_key)
            # TODO
            # this is static single record for development.
            # use seeds yaml
            obj.update({
                'project_access_key_id': 'PROJECT_ID',
                'site_id': '1',
                'read_key': 'READ_KEY',
                'write_key': 'WRITE_KEY',
            })
            client.put(obj)


def main(argv=None):
    if not argv:
        argv = sys.argv

    if len(argv) < 4:
        usage(argv)
    config_uri = argv[1]
    command = argv[2]
    action = argv[3]
    options = parse_vars(argv[4:])

    setup_logging(config_uri)

    if command not in ('db', 'ds',):
        raise Exception('Run with valid command {db,ds} :\'(')

    shared_actions = ('help',)
    err_msg = 'Run with valid action {0!s} :\'('

    actions = []
    if command == 'db':
        actions += shared_actions + ('init',)
    elif command == 'ds':
        actions += shared_actions + ('seed',)

    if action not in actions:
        raise Exception(err_msg.format('|'.join(actions)))

    settings = get_appsettings(config_uri, options=options)
    load_dotenv_vars()
    settings = resolve_env_vars(settings)

    cli = '{0}{1}'.format(command.capitalize(), 'Cli')
    c = globals()[cli](settings)
    getattr(c, action.lower())()
