# Copyright (c) 2015 Cisco Systems, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json

from oslo_log import log as logging
from requests import delete
from requests import get
from requests import post
from requests import put

from gluon.common import exception as exc

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
            msg = "JSON unreadable: %s on %s" % (e.args[0], resp.content)
            raise exc.MalformedResponseBody(reason=msg)
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
                                                   % (e.args[0], resp.content))
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
                                                   % (e.args[0], resp.content))
        return rv
