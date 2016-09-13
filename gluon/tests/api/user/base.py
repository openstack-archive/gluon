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
from gluonclient import api as gc_api
from gluon.tests.api import base


class ClientAPITestCase(base.APITestCase):

    def setUp(self):
        super(APITestCase, self).setUp()
        self.gluonclient = gc_api.ClientAPI('http://%s/v1/' % self.gluon_url)
