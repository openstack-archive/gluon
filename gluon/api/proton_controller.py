#    Copyright 2015, Ericsson AB
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

import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from gluon.api.baseObject import APIBase
from gluon.api import link
from gluon.particleGenerator import generator as particle_generator
from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class ProtonRoot(APIBase):
    """The representation of the version 1 of the API."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    links = [link.Link]

    @staticmethod
    def convert():
        root = ProtonRoot()
        root.id = "proton"
        root.links = [link.Link.make_link('self', pecan.request.host_url,
                                          'proton', '', bookmark=True), ]
        return root


class ProtonController(rest.RestController):
    """Version 1 API controller root."""

    def __init__(self):
        services = str(cfg.CONF.api.service_list).split(',')
        service_list = list()
        for api_name in services:
            service_list.append(api_name.strip())
        particle_generator.build_api(self, service_list)

    @wsme_pecan.wsexpose(ProtonRoot)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return ProtonRoot.convert()
