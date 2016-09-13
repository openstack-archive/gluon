from oslo_log import log as logging
from gluon.common import exception as exc
from requests import get, put, post, delete
import json

LOG = logging.getLogger(__name__)
logger = LOG


class Client(object):

    def __init__(self, service):
        self._service = service

    def json_get(self, url):
        resp = get(url)
        if resp.status_code != 200:
            raise exc.GluonClientException('Bad return status %d'
                                           % resp.status_code,
                                           status_code=resp.status_code)
        try:
            rv = json.loads(resp.content)
        except Exception as e:
            raise exc.MalformedResponseBody(reason="JSON unreadable: %s on %s"
                                               % (e.message, resp.content))
        return rv

    def do_delete(self, url):
        resp = delete(url)
        if resp.status_code != 200:
            raise exc.GluonClientException('Bad return status %d'
                                           % resp.status_code,
                                           status_code=resp.status_code)

    def do_post(self, url, values):
        resp = post(url, json=values)
        if resp.status_code != 201 or resp.status_code != 201:
            raise exc.GluonClientException('Bad return status %d'
                                           % resp.status_code,
                                           status_code=resp.status_code)
        try:
            rv = json.loads(resp.content)
        except Exception as e:
            raise exc.MalformedResponseBody(reason="JSON unreadable: %s on %s"
                                                   % (e.message, resp.content))
        return rv

    def do_put(self, url, values):
        resp = put(url, json=values)
        if resp.status_code != 200:
            raise exc.GluonClientException('Bad return status %d'
                                           % resp.status_code,
                                           status_code=resp.status_code)
        try:
            rv = json.loads(resp.content)
        except Exception as e:
            raise exc.MalformedResponseBody(reason="JSON unreadable: %s on %s"
                                                   % (e.message, resp.content))
        return rv
