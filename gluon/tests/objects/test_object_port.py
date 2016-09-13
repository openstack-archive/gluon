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

from gluon.common.particleGenerator.generator import set_package
set_package("gluon", "models/proton/net-l3vpn")

from gluon.tests.objects import base as objbase
from gluon.tests.objects import utils
from gluon.common import exception


class TestPort(objbase.ObjectTestCase):

    def test_create(self):
        pass

    def test_create_consistency(self):
        pass

    def test_already_exists(self):
        pass
