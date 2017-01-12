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
import six

from gluon.particleGenerator.DataBaseModelGenerator import\
    DataBaseModelProcessor as DBMProcessor
from gluon.tests.particleGenerator import base as partgen_base


class DataBaseModelGeneratorTestCase(partgen_base.ParticleGeneratorTestCase):

    # Create sample models: GluonInternalPort and foo
    # GluonInternalPort has foreign key reference to foo
    def setUp(self):
        super(DataBaseModelGeneratorTestCase, self).setUp()
        self.model = \
            {'api_objects':
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
             }
        self.table_data = self.model.get('api_objects')\
            .get("GluonInternalPort")

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

        expected_exception = None
        try:
            dbm_processor.get_table_class(api_name, "wrong_table_name")
        except Exception as e:
            expected_exception = e
        self.assertIsNotNone(expected_exception)

        try:
            dbm_processor.get_table_class("wrong_api_name", "wrong_table_name")
        except Exception as e:
            expected_exception = e
        self.assertIsNotNone(expected_exception)

    """
    test build_sqla_models
    """

    # Should raise exception if data is None
    @mock.patch(
        "gluon.particleGenerator.DataBaseModelGenerator.declarative_base")
    def test_build_sqla_models_data_None(self, mock_dec_base):
        dbm_processor = DBMProcessor()
        api_name = 'foo'
        try:
            dbm_processor.build_sqla_models(api_name, base=None)
        except(Exception) as e:
            self.assertEqual(str(e),
                             'Cannot create Database Model from empty model.')
        mock_dec_base.assert_called_once()

    # A sunny day full test
    # Use sample models in self.model which contains two models:
    # GluonInternalPort and foo.
    # After running build_sqla_models with self.model as input
    # two classes should be generated.
    # Inspect these two class to assert they are generated correctly

    # FIXME
    # is this a bug?
    # when table_name starts with uppercase, then there will be two underscores
    # between api name and table name. For example, the GluonInternalPort model
    # has table_name = "gluon_api__gluon_internal_port"
    def test_build_sqla_models(self):
        dbm_processor = DBMProcessor()
        api_name = 'gluonApi'
        port_table_name = 'GluonInternalPort'
        foo_table_name = 'foo'
        dbm_processor.add_model(self.model)
        dbm_processor.build_sqla_models(api_name, base=None)

        # ** for the GluonInternalPort model **
        # A class for GluonInternalPort should have been generated
        GluonInternalPort_class = \
            dbm_processor.db_models[api_name][port_table_name]
        self.assertIsNotNone(GluonInternalPort_class)
        # FIXME __tablename__ has two underscores between api and table name
        expected_table_name = "gluon_api__gluon_internal_port"
        self.assertEqual(GluonInternalPort_class.__tablename__,
                         expected_table_name)
        # The class name is in this form "api_name" + "table_name"
        expected_class_name = api_name + "_" + port_table_name
        self.assertEqual(GluonInternalPort_class.__name__, expected_class_name)
        # The _tname is the table_name
        self.assertEqual(GluonInternalPort_class.__tname__, port_table_name)
        # The _service_name is the api_name
        self.assertEqual(GluonInternalPort_class._service_name, api_name)
        # The class should have all the attributes from GluonInternalPort table
        GluonInternalPort_class_attrs = dir(GluonInternalPort_class)
        for col_name, col_desc in \
                six.iteritems(self.model['api_objects']
                              ['GluonInternalPort']['attributes']):
            self.assertIn(col_name, GluonInternalPort_class_attrs)

        # ** for the foo model **
        # A class for foo should have been generated
        foo_class = dbm_processor.db_models[api_name][foo_table_name]
        self.assertIsNotNone(foo_class)
        # __tablename__ is de_camel(api_name + "_" + table_name)
        expected_table_name = "gluon_api_foo"
        self.assertEqual(foo_class.__tablename__,
                         expected_table_name)
        # The class name is in this form "api_name" + "table_name"
        expected_class_name = api_name + "_" + foo_table_name
        self.assertEqual(foo_class.__name__, expected_class_name)
        # The _tname is the table_name
        self.assertEqual(foo_class.__tname__, foo_table_name)
        # The _service_name is the api_name
        self.assertEqual(foo_class._service_name, api_name)
        # The class should have all the attributes from GluonInternalPort table
        foo_class_attrs = dir(foo_class)
        for col_name, col_desc in \
                six.iteritems(self.model['api_objects']['foo']['attributes']):
            self.assertIn(col_name, foo_class_attrs)

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
