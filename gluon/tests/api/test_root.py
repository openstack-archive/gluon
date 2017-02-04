#    Copyright 2016, AT&T
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

import mock
from mock import MagicMock
from mock import patch

import datetime
import six
import wsme

from gluon.api.root import Root
from gluon.api.root import RootController
from gluon.api.root import Version
from gluon.tests.api import base


class VersionTestCase(base.APITestCase):

    def setUp(self):
        super(VersionTestCase, self).setUp()
        pass

    @patch('gluon.api.root.pecan.request')
    def test_convert(self, mock_request):
        mock_request.host_url = "http://localhost:6385"
        id = "proton"

        observed = Version.convert(id)

        self.assertEqual(id, observed.id)
        self.assertEqual('self', observed.links[0].rel)
        self.assertEqual('http://localhost:6385/proton/',
                         observed.links[0].href)


class RootTestCase(base.APITestCase):

    def setUp(self):
        super(RootTestCase, self).setUp()
        pass

    @patch('gluon.api.root.pecan.request')
    def test_convert(self, mock_request):
        mock_request.host_url = "http://localhost:6385"

        root = Root.convert()

        self.assertEqual('Gluon API', root.name)
        self.assertEqual('v1', root.default_version.id)
        self.assertEqual('http://localhost:6385/v1/',
                         root.default_version.links[0].href)


class RootControllerTestCase(base.APITestCase):

    def setUp(self):
        super(RootControllerTestCase, self).setUp()
        pass

    @patch('gluon.api.root.wsme_pecan.wsexpose')
    @patch('gluon.api.root.pecan.request')
    def test_get(self, mock_request, mock_wsexpose):
        mock_request.host_url = "http://localhost:6385"
        # mock_wsexpose.return_value = \
        #     Root.convert(version=RootController._default_version)

        # rootController = RootController()
        # rootController.get()
        pass
