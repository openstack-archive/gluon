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
from mock import patch

from gluon.particleGenerator.DataBaseModelGenerator import\
    DataBaseModelProcessor as DBMProcessor
from gluon.tests.particleGenerator import base as partgen_base


class DataBaseModelGeneratorTestCase(partgen_base.ParticleGeneratorTestCase):

    def setUp(self):
        super(DataBaseModelGeneratorTestCase, self).setUp()

    """
    test get_db_models
    """
    def test_get_db_models(self):
        dbm_processor = DBMProcessor()
        api_name = "foo"
        model = mock.Mock()
        dbm_processor.db_models[api_name] = model

        observed = dbm_processor.get_db_models(api_name)
        self.assertEqual(model, observed)

    """
    test add_model
    """
    def test_add_model(self):
        dbm_processor = DBMProcessor()
        mock_model = mock.Mock()

        dbm_processor.add_model(mock_model)
        self.assertEqual(mock_model, dbm_processor.data)

    """
    test get_table_class
    """
    def test_get_table_class(self):
        api_name = "foo"
        table_name = "bar"
        mock_model = mock.Mock()
        dbm_processor = DBMProcessor()
        dbm_processor.db_models[api_name] = {table_name: mock_model}

        observed = dbm_processor.get_table_class(api_name, table_name)
        self.assertEqual(mock_model, observed)
        self.assertRaises(KeyError,
                          dbm_processor.get_table_class,
                          api_name,
                          "wrong_table_name")
        self.assertRaises(TypeError,
                          dbm_processor.get_table_class,
                          "wrong_api_name",
                          "wrong_table_name")
    """
    test build_sqla_models
    """
    def test_build_sqla_models(self):
        pass
