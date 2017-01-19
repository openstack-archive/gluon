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

from gluon.db.sqlalchemy import models as sql_models
from gluon.particleGenerator.ApiGenerator import APIGenerator
from gluon.particleGenerator.DataBaseModelGenerator \
    import DataBaseModelProcessor
from gluon.particleGenerator import generator
from gluon.tests.particleGenerator import base as partgen_base


class GeneratorTestCase(partgen_base.ParticleGeneratorTestCase):

    def setUp(self):
        super(GeneratorTestCase, self).setUp()

    # The generator.py module hardcodes the package_name and model_dir which
    # limits these testcases to use data in net-l3vpn
    # If the content of net-l3vpn is modified, these testcases may fail

    """
    test load_model(service)
    """
    def test_load_model(self):
        service_models = generator.load_model("gluon",
                                              "models",
                                              "test")
        self.assertIn('TestService', service_models['api_objects'])
        self.assertIn('Port', service_models['api_objects'])
        self.assertIn('Interface', service_models['api_objects'])

    """
    test build_sql_models(service_list)
    """
    @mock.patch('gluon.particleGenerator.generator.load_model')
    @mock.patch.object(DataBaseModelProcessor, 'build_sqla_models')
    @mock.patch.object(DataBaseModelProcessor, 'add_model')
    def test_build_sql_models(self,
                              mock_add_model,
                              mock_build_sqla_models,
                              mock_load_model):
        mock_service = {'foo': 'bar'}
        mock_load_model.return_value = mock_service

        generator.build_sql_models(['test'])
        # TODO(hambtw): Need to rework
        # mock_load_model.assert_called_with('foo')
        # mock_add_model.assert_called_with(mock_service)
        mock_build_sqla_models.assert_called_with('test', sql_models.Base)

    """
    test build_api
    """
    @mock.patch('gluon.particleGenerator.generator.load_model')
    @mock.patch.object(APIGenerator, 'create_controller')
    @mock.patch.object(APIGenerator, 'add_model')
    @mock.patch.object(APIGenerator, 'create_api')
    @mock.patch('gluon.particleGenerator.generator.GenData.DBGeneratorInstance'
                )
    def test_build_api(self,
                       mock_DBGeneratorInstance,
                       mock_create_api,
                       mock_add_model,
                       mock_create_controller,
                       mock_load_model):
        root = object()
        service_list = ['test']
        mock_service = {'foo': 'bar'}
        mock_load_model.return_value = mock_service
        db_models = mock.Mock()
        mock_DBGeneratorInstance.get_db_models.return_value = db_models
        service_root = mock.Mock()
        mock_create_controller.return_value = service_root

        generator.build_api(root, service_list)

        mock_load_model.assert_called_with('gluon', 'models', 'test')
        mock_create_controller.assert_called_with('test', root)
        mock_add_model.assert_called_with(mock_service)
        mock_DBGeneratorInstance.get_db_models.assert_called_with('test')
        mock_create_api.assert_called_with(service_root,
                                           'test',
                                           db_models)
    """
    test get_db_gen
    """
    @mock.patch('gluon.particleGenerator.generator.GenData.DBGeneratorInstance'
                )
    def test_get_db_gen(self, mock_DBGeneratorInstance):
        self.assertEqual(generator.get_db_gen(),
                         mock_DBGeneratorInstance)
