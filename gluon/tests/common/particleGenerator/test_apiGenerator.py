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

import mock
from mock import patch
import six
import sys
import yaml

import os

from gluon.api import types
from gluon.api.baseObject import APIBaseObject
from gluon.api.baseObject import RootObjectController
from gluon.api.baseObject import SubObjectController
from gluon.common.particleGenerator.DataBaseModelGenerator\
     import DataBaseModelProcessor
from gluon.core.manager import get_api_manager
from gluon.objects import base as obj_base
from oslo_versionedobjects import fields

from gluon.common.particleGenerator import ApiGenerator
from gluon.tests.common.particleGenerator import base as partgen_base


class ApiGeneratorTestCase(partgen_base.ParticleGeneratorTestCase):

    def setUp(self):
        super(ApiGeneratorTestCase, self).setUp()
        mock_db_models = mock.MagicMock()
        mock_models = mock.Mock()
        self.apiGenerator = ApiGenerator.APIGenerator(mock_db_models)
        self.apiGenerator.add_model(mock_models)

    #generate a testing_model with one table from the testing_model.yaml file
    #create empty object as root
    #create_api should add the table's api name into root
    @patch('gluon.common.particleGenerator.ApiGenerator.get_api_manager')
    @mock.patch.object(RootObjectController, 'class_builder')
    @mock.patch.object(APIBaseObject, 'class_builder')
    @mock.patch.object(obj_base.GluonObject, 'class_builder')
    def test_creat_api(self, mock_GluonObject_CB, mock_APIObject_CB,
                       mock_RootObject_CB, mock_get_api_mgr):
        testing_model = self.load_testing_model()

        root = t = type('test', (object,), {})()
        self.apiGenerator.add_model(testing_model)
        self.apiGenerator.create_api(root)
        mock_GluonObject_CB.assert_called_once()
        mock_get_api_mgr.assert_called_once()
        mock_APIObject_CB.assert_called_once()
        mock_RootObject_CB.assert_called_once()
        api_name = testing_model.values()[0]['api']['name']
        self.assertEqual(True, hasattr(root, api_name))

    @mock.patch.object(DataBaseModelProcessor, 'get_primary_key')
    def test_get_primary_key_type(self, mock_get_pk):
        primary_key = 'pk'
        foo = 'foo'
        table_data = {'attributes': {primary_key: {'type': foo}}}
        mock_get_pk.return_value = primary_key
        type_= self.apiGenerator.get_primary_key_type(table_data)
        mock_get_pk.assert_called_once_with(table_data)
        self.assertEqual(type_, foo)

    @mock.patch.object(fields, 'BooleanField')
    @mock.patch.object(fields, 'IntegerField')
    @mock.patch.object(fields, 'EnumField')
    @mock.patch.object(fields, 'StringField')
    @mock.patch.object(fields, 'UUIDField')
    @mock.patch.object(ApiGenerator.APIGenerator, 'get_primary_key_type')
    def test_translate_model_to_real_obj_type(self,
                                mock_get_pkt, mock_UUID, mock_String,
                                mock_Enum, mock_Int, mock_Bool):
        m = mock.Mock()
        model_type = 'a'
        self.apiGenerator.add_model({model_type : m})
        mock_get_pkt.return_value = "string"
        self.apiGenerator.translate_model_to_real_obj_type(model_type, [])
        mock_get_pkt.assert_called_once_with(m)
        mock_UUID.return_value = m
        self.assertEqual(m,
            self.apiGenerator.translate_model_to_real_obj_type('uuid', []))
        mock_String.return_value = m
        self.assertEqual(m,
            self.apiGenerator.translate_model_to_real_obj_type('string', []))
        mock_Enum.return_value = m
        self.assertEqual(m,
            self.apiGenerator.translate_model_to_real_obj_type('enum', []))
        mock_Int.return_value = m
        self.assertEqual(m,
            self.apiGenerator.translate_model_to_real_obj_type('integer', []))
        mock_Bool.return_value = m
        self.assertEqual(m,
            self.apiGenerator.translate_model_to_real_obj_type('boolean', []))
        self.assertRaises( Exception,
            self.apiGenerator.translate_model_to_real_obj_type,
            'foo',
            []
            )

    @mock.patch.object(types, 'create_enum_type')
    @mock.patch.object(ApiGenerator.APIGenerator, 'get_primary_key_type')
    def test_translate_model_to_api_type(self, mock_get_pkt, mock_enum):
        m = mock.Mock()
        model_type = 'a'
        self.apiGenerator.add_model( {model_type : m})
        mock_get_pkt.return_value = "string"
        self.apiGenerator.translate_model_to_api_type(model_type, [])
        mock_get_pkt.assert_called_once_with(m)
        self.assertEqual(types.uuid,
                self.apiGenerator.translate_model_to_api_type('uuid', []))
        self.assertEqual(unicode,
                self.apiGenerator.translate_model_to_api_type('string', []))
        values = ['foo', 'bar', 'baz']
        self.apiGenerator.translate_model_to_api_type('enum',values)
        mock_enum.assert_called_once_with(*values)
        self.assertEqual(types.int_type,
                self.apiGenerator.translate_model_to_api_type('integer', []))
        self.assertEqual(types.boolean,
                self.apiGenerator.translate_model_to_api_type('boolean', []))
