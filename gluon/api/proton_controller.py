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
from gluon.api import types
from gluon.particleGenerator import generator as particle_generator
from oslo_config import cfg


class Proton(APIBase):

    proton_service = wtypes.text
    """The name of Proton service"""

    status = types.create_enum_type('CURRENT', 'STABLE', 'DEPRECATED')
    """Status of the API, which can be CURRENT, STABLE or DEPRECATED"""

    links = [link.Link]
    """A Link that point to the root of proton"""

    @staticmethod
    def convert(service, status='CURRENT'):
        proton = Proton()
        proton.status = status
        proton.proton_service = service
        proton.links = [link.Link.make_link('self',
                                            pecan.request.host_url,
                                            'proton',
                                            service,
                                            bookmark=True)]
        return proton


class ProtonRoot(APIBase):

    protons = [Proton]
    """List of protons in their current version"""

    @staticmethod
    def convert():
        service_list = particle_generator.get_service_list()
        protons = list()
        for service in service_list:
            proton = Proton.convert(service)
            protons.append(proton)

        root = ProtonRoot()
        root.protons = protons
        return root


class ProtonController(rest.RestController):
    """Version 1 API controller root."""

    def __init__(self):
        service_list = particle_generator.get_service_list()
        particle_generator.build_api(self, service_list)

    @wsme_pecan.wsexpose(ProtonRoot)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return ProtonRoot.convert()
