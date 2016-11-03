# -*- encoding: utf-8 -*-
#
# Copyright ï¿½ 2012 New Dream Network, LLC (DreamHost)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from gluon.api.baseObject import APIBase
from gluon.api.controller.v1.base import API as v1
from gluon.api import link


class Version(APIBase):
    """An API version representation."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    links = [link.Link]
    """A Link that point to a specific version of the API"""

    @staticmethod
    def convert(id):
        version = Version()
        version.id = id
        version.links = [link.Link.make_link('self', pecan.request.host_url,
                                             id, '', bookmark=True)]
        return version


class Root(APIBase):

    name = wtypes.text
    """The name of the API"""

    description = wtypes.text
    """Some information about this API"""

    versions = [Version]
    """Links to all the versions available in this API"""

    default_version = Version
    """A link to the default version of the API"""

    @staticmethod
    def convert():
        root = Root()
        root.name = "Gluon API"
        root.description = ("OpenStack Gluon acts as a port arbiter between "
                            "Nova and port-provider such as Neutron")
        root.versions = [Version.convert('v1')]
        root.default_version = Version.convert('v1')
        return root


class RootController(rest.RestController):

    _versions = ['v1']
    """All supported API versions"""

    _default_version = 'v1'
    """The default API version"""

    v1 = v1()

    @wsme_pecan.wsexpose(Root)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return Root.convert()

    @pecan.expose()
    def _route(self, args, request=None):
        """Overrides the default routing behavior.

        It redirects the request to the default version of the Gluon API
        if the version number is not specified in the url.
        """

        if args[0] and args[0] not in self._versions:
            args = [self._default_version] + args
        return super(RootController, self)._route(args)
