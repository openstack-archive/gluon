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
from gluon.particleGenerator.cli import load_model
from gluon.tests import base


class ParticleGeneratorTestCase(base.TestCase):

    def setUp(self):
        super(ParticleGeneratorTestCase, self).setUp()
        pass

    def load_testing_model(self):
        testing_model = load_model("gluon.tests.particleGenerator",
                                   "",
                                   "models")
        return testing_model
