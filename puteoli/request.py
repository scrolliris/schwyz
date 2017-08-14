import re
import ipaddress

from pyramid.decorator import reify
from pyramid.request import Request

from .env import Env

__all__ = ['CustomRequest']

IPV4_ADDR = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
IPV6_ADDR = re.compile(r'[0-9a-f]+[0-9a-f:]+')

TRUSTED_NETWORKS = [ipaddress.ip_network(n) for n in [
    '127.0.0.1',       # localhost ipv4
    '::1',             # localhost ipv6
    '10.0.0.0/8',      # private ipv4 range
    '172.16.0.0/12',   # private ipv4 range
    '192.168.0.0/16',  # private ipv4 range
    'fc00::/7',        # private ipv6 range
]]

ASSET_PATH = re.compile(r'\/?(assets|favicon\.ico|.*\.txt)')


class CustomRequest(Request):
    def __init__(self, *args, **kwargs):
        env_dict = (args[0] or {})

        # self.environ is request env.
        # the `env` is os's environ handler (wrapper)
        self.env = Env()
        if self.env.is_production:
            env_dict = self._force_ssl(env_dict)
            env_dict = self._trim_port(env_dict)

        new_args = (env_dict, args[1:])
        super().__init__(*new_args, **kwargs)

    @property
    def settings(self):
        from . import get_settings

        return get_settings() or {}

    # see https://github.com/Pylons/webob/issues/77
    @reify
    def remote_ip(self):
        """
        Calculates client's ip address
        """
        from collections import OrderedDict
        import itertools

        raw_remote_addr = self._ips_at('REMOTE_ADDR')

        remote_addr = raw_remote_addr[-1] if raw_remote_addr else None
        client_ips = self._ips_at('HTTP_CLIENT_IP')[::-1]
        forwarded_ips = self._ips_at('HTTP_X_FORWARDED_FOR')[::-1]

        # ip snoofing check
        if (client_ips and client_ips[-1]) and \
           (forwarded_ips and forwarded_ips[-1]) and \
           (client_ips[-1] not in forwarded_ips):
            raise Exception(
                'It may be IP snoofing attack! '
                'HTTP_CLIENT_IP: {0!s} HTTP_X_FORWARDED_FOR: {1!s}'.format(
                    self.environ.get('HTTP_CLIENT_IP'),
                    self.environ.get('HTTP_X_FORWARDED_FOR')))

        ips = list(OrderedDict.fromkeys(itertools.chain.from_iterable(
                   [forwarded_ips, client_ips, [remote_addr]])))

        is_found_trusted_ips = False
        for ip in ips:
            ip_addr = ipaddress.ip_address(ip)
            for tp in TRUSTED_NETWORKS:
                if ip_addr in tp:
                    is_found_trusted_ips = True
                    break

        return ips[0] if is_found_trusted_ips else remote_addr

    def _ips_at(self, header):
        """
        Returns valid ip address only
        """
        value = self.environ.get(header, None)
        ips = re.split(r'[,\s]+', value) if value else []
        return [ip for ip in ips if IPV4_ADDR.match(ip) or IPV6_ADDR.match(ip)]

    def _force_ssl(self, env_dict):
        env_dict['wsgi.url_scheme'] = self.settings.get(
            'wsgi.url_scheme', 'https')
        return env_dict

    def _trim_port(self, env_dict):
        http_host = env_dict.get('HTTP_HOST', '')
        http_host = re.sub(':[0-9]+$', '', http_host)

        env_dict['HTTP_HOST'] = http_host
        env_dict['SERVER_PORT'] = ''
        return env_dict
