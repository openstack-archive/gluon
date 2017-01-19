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

import datetime
import six
import wsme

from gluon.api import baseObject
from gluon.tests.api import base


class APIBaseTestCase(base.APITestCase):

    def setUp(self):
        super(APIBaseTestCase, self).setUp()
        pass

    """
    test get_fields
    """
    # each APIBase object should always has two fields:
    # created_at and updated_at
    def test_get_fields(self):
        api_base = baseObject.APIBase()
        fields = api_base.get_fields()
        self.assertIn("created_at", fields)
        self.assertIn("updated_at", fields)

    """
    test as_dict
    """
    # each APIBase object should always has two fields:
    # created_at and updated_at
    def test_as_dict(self):
        api_base = baseObject.APIBase()
        # set the created_at and updated_at fields
        now = datetime.datetime.now()
        api_base.created_at = now
        api_base.updated_at = now

        fields_dict = api_base.as_dict()

        self.assertIn("created_at", fields_dict)
        self.assertIn("updated_at", fields_dict)
        self.assertEqual(fields_dict["created_at"], now)
        self.assertEqual(fields_dict["updated_at"], now)

    """
    test unset_fields_except
    """
    # unset created_at and keep updated_at
    def test_unset_fields_except(self):
        api_base = baseObject.APIBase()
        # set the created_at and updated_at fields
        today = datetime.datetime.today()
        api_base.created_at = today
        api_base.updated_at = today
        except_list = ["updated_at"]

        api_base.unset_fields_except(except_list)

        self.assertEqual(api_base.created_at, wsme.Unset)
        self.assertEqual(api_base.updated_at, today)


class APIBaseObjectTestCase(base.APITestCase):

    def setUp(self):
        super(APIBaseObjectTestCase, self).setUp()
        pass

    """
    test class_builder
    """
    # new_class should have __name__ and db_model attribute
    # new_class object has attribute attr_foo which only accept str value
    @patch('gluon.api.baseObject.dbapi.get_instance')
    def test_class_builder(self, mock_get_instance):
        new_class_name = 'new_class'
        _db_model = mock.Mock()
        attributes = {"attr_foo": str}

        new_class = baseObject.APIBaseObject.class_builder(
            new_class_name, _db_model, attributes)

        self.assertEqual(new_class.db_model, _db_model)
        self.assertEqual(new_class.__name__, new_class_name)
        mock_get_instance.assert_called_once()
        # create new_class object and assign value to it
        new_obj = new_class()
        try:
            # should throw wsme.exc.InvalidInput since attr_foo is str type
            new_obj.attr_foo = 123
        except wsme.exc.InvalidInput as e:
            self.assertIsNotNone(e)

    """
    test build
    """
    # create new_class which has attribute "attr_foo"
    # create mock_db_obj has attribute "attr_foo" with value "123"
    # build() should return object whose attr_foo attribute is "123"
    def test_build(self):
        new_class_name = 'new_class'
        _db_model = mock.Mock()
        attributes = {"attr_foo": str}
        new_class = baseObject.APIBaseObject.class_builder(
            new_class_name, _db_model, attributes)
        mock_db_obj = mock.Mock()
        mock_db_obj.as_dict.return_value = {"attr_foo": "123"}

        new_obj = new_class.build(mock_db_obj)
        observed = new_obj.attr_foo
        expected = "123"
        self.assertEqual(observed, expected)

    """
    test get_from_db
    """
    # mock db and mock db_obj
    # create mock_db_obj has attribute "attr_foo" with value "123"
    @patch('gluon.api.baseObject.dbapi.get_instance')
    def test_get_from_db(self, mock_get_instance):
        # mock_db_obj has as_dict function that returns a dict
        mock_db_obj = mock.Mock()
        mock_db_obj.as_dict.return_value = {"attr_foo": "123"}

        # mock_db has get_by_primary_key function that returns mock_db_obj
        mock_db = mock.Mock()
        mock_db.get_by_primary_key.return_value = mock_db_obj

        # set the dbapi.get_instance to return mock_db
        mock_get_instance.return_value = mock_db

        # create new_class with db attribute pointing to mock_db
        new_class_name = 'new_class'
        _db_model = mock.Mock()
        attributes = {"attr_foo": str}
        new_class = baseObject.APIBaseObject.class_builder(
            new_class_name, _db_model, attributes)

        new_obj = new_class.get_from_db("any_key")
        observed = new_obj.attr_foo
        expected = "123"
        self.assertEqual(observed, expected)
