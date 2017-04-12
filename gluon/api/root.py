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
from gluon.api import link
from gluon.api.proton_controller import ProtonController
from gluon.api import types


class Version(APIBase):
    """An API version representation."""

    status = types.create_enum_type('CURRENT', 'STABLE', 'DEPRECATED')
    """Status of the API, which can be CURRENT, STABLE, DEPRECATED"""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    links = [link.Link]
    """A Link that point to a specific version of the API"""

    @staticmethod
    def convert(id, status='CURRENT'):
        version = Version()
        version.status = status
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
    def convert(version='v1'):
        root = Root()
        root.name = "Gluon API"
        root.description = ("OpenStack Gluon is a port arbiter that maintains "
                            "a list of ports and bindings of different "
                            "network backends. A Proton Server is the API "
                            "server that hosts multiple Protons, i.e. "
                            "multiple sets of APIs.")
        root.versions = [Version.convert(version)]
        root.default_version = Version.convert(version)
        return root


class RootController(rest.RestController):

    _versions = ['proton']
    """All supported API versions"""

    _default_version = 'proton'
    """The default API version"""

    proton = ProtonController()

    @wsme_pecan.wsexpose(Root)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return Root.convert(version=self._default_version)

    @pecan.expose()
    def _route(self, args, request=None):
        """Overrides the default routing behavior.

        It redirects the request to the default version of the Gluon API
        if the version number is not specified in the url.
        """

        if args[0] and args[0] not in self._versions:
            args = [self._default_version] + args
        return super(RootController, self)._route(args)
