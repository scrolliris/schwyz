import os
import sys

import cherrypy
from pyramid.paster import (
    get_app,
    setup_logging
)

from puteoli.env import Env


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s {staging|production}.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv, quiet=False):
    """ start server process. """
    if len(argv) < 2:
        usage(argv)

    Env.load_dotenv_vars()
    env = Env()

    config = argv[1]
    wsgi_app = get_app(config)
    setup_logging(config)

    cherrypy.tree.graft(wsgi_app, '/')

    cherrypy.server.unsubscribe()
    server = cherrypy._cpserver.Server()
    server.socket_host = env.host
    server.socket_port = env.port
    server.thread_pool = 30
    server.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    sys.exit(main() or 0)
