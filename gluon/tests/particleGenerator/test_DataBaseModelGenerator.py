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
        self.model = \
            {'GluonInternalPort':
             {'api':
              {'name': 'ports',
               'parent': {'type': 'root'}
               },
              'attributes':
              {'device_id':
               {'description': 'UUID of bound VM',
                'type': 'uuid'
                },
               'device_owner':
               {'description':
                'Name of compute or network service (if bound)',
                'length': 128,
                'type': 'string'
                },
               'id':
               {'description': 'UUID of port',
                'primary': True,
                'required': True,
                'type': 'uuid'
                },
               'owner':
               {'description':
                'Pointer to backend service instance (name)',
                'required': True,
                'type': 'string',
                'length': 128
                },
               'fk_reference':
               {'type': 'foo',
                'description': 'foreign key reference'
                }
               }
              },

             'foo':
             {'api':
              {'name': 'foos',
               'parent': {'type': 'root'}
               },
              'attributes':
              {'foo_id':
               {'type': 'uuid',
                'description': 'UUID of foo',
                'required': True,
                'primary': True
                }
               }
              }
             }
        self.table_data = self.model.get("GluonInternalPort")

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

    # should raise exception if data is None
    @mock.patch(
        "gluon.particleGenerator.DataBaseModelGenerator.declarative_base")
    def test_build_sqla_models_data_None(self, mock_dec_base):
        dbm_processor = DBMProcessor()
        api_name = 'foo'
        # pep fails on asserting Exception, use try and except
        # self.assertRaises(Exception,
        #                  dbm_processor.build_sqla_models,
        #                  api_name,
        #                 base=None)
        try:
            dbm_processor.build_sqla_models(api_name, base=None)
        except(Exception) as e:
            self.assertEqual(str(e),
                             'Cannot create Database Model from empty model.')
        mock_dec_base.assert_called_once()

    # sunny day
    def test_build_sqla_models(self):
        dbm_processor = DBMProcessor()
        api_name = 'gluonApi'
        port_table_name = 'GluonInternalPort'
        foo_table_name = 'foo'
        dbm_processor.add_model(self.model)
        dbm_processor.build_sqla_models(api_name, base=object)

        # a class for GluonInternalPort should have been generated
        self.assertIsNotNone(
            dbm_processor.db_models[api_name][port_table_name])
        # the class name is in this form "api_name" + "table_name"
        class_name = api_name + "_" + port_table_name
        self.assertEqual(
            dbm_processor.db_models[api_name]['GluonInternalPort'].__name__,
            class_name)
        # create an instance of GluonInternalPort and inspect its attributes
        GluonInternalPort = \
            dbm_processor.db_models[api_name]['GluonInternalPort']
        port_instance = GluonInternalPort()
        print("__tablename__is {0}".format(port_instance.__tablename__))
        # self.assertEqual("a", "b")

        # a class for foo should have been generated
        self.assertIsNotNone(
            dbm_processor.db_models[api_name][foo_table_name])

    """
    test get_primary_key
    """
    # id is the primary key in our sample table_data
    def test_get_primary_key_pk(self):
        observed = DBMProcessor.get_primary_key(self.table_data)
        self.assertEqual("id", observed)

    # test table_data without primay key, should set "uuid" by default
    def test_get_primary_key_no_pk(self):
        table_data = {'attributes': {}}
        observed = DBMProcessor.get_primary_key(table_data)
        self.assertEqual("uuid", observed)
