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

"""
test_gluon
----------------------------------

Tests for `gluon` module.
"""

from gluon.tests.objects import base
from gluon.tests.objects import utils
from gluon.common import exception


class TestPort(base.ObjectTestCase):

    def test_create(self):
        port = Port()
        port.create()

    def test_create_consistency(self):
        port = utils.create_fake_port(
            uuid='24c050ab-f357-4a89-97cc-339ed7e00065')
        self.assertEqual(port.uuid, '24c050ab-f357-4a89-97cc-339ed7e00065')

    def test_already_exists(self):
        utils.create_fake_port()
        self.assertRaises(exception.PortAlreadyExists,
                          utils.create_fake_port)
