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
from mock import MagicMock
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

        # create new_class with db field pointing to mock_db
        new_class_name = 'new_class'
        _db_model = mock.Mock()
        attributes = {"attr_foo": str}
        new_class = baseObject.APIBaseObject.class_builder(
            new_class_name, _db_model, attributes)

        new_obj = new_class.get_from_db("any_key")
        observed = new_obj.attr_foo
        expected = "123"
        self.assertEqual(observed, expected)

    """
    test create_in_db
    """
    # mock db and mock db_obj
    # create mock_db_obj has attribute "attr_foo" with value "123"
    @patch('gluon.api.baseObject.dbapi.get_instance')
    def test_create_in_db(self, mock_get_instance):
        # mock_db_obj has as_dict function that returns a dict
        mock_db_obj = mock.Mock()
        mock_db_obj.as_dict.return_value = {"attr_foo": "123"}

        # mock_db has create function that returns mock_db_obj
        mock_db = mock.Mock()
        mock_db.create.return_value = mock_db_obj

        # set the dbapi.get_instance to return mock_db
        mock_get_instance.return_value = mock_db

        # create new_class with db field pointing to mock_db
        new_class_name = 'new_class'
        _db_model = mock.Mock()
        attributes = {"attr_foo": str}
        new_class = baseObject.APIBaseObject.class_builder(
            new_class_name, _db_model, attributes)

        new_obj = new_class.create_in_db({"attr_foo": "123"})
        observed = new_obj.attr_foo
        expected = "123"
        self.assertEqual(observed, expected)
        # also assert create() has called once
        mock_db.create.assert_called_once()

    """
    test update_in_db
    """
    # mock db and mock db_obj
    # create mock_db_obj has attribute "attr_foo" with value "123"
    @patch('gluon.api.baseObject.dbapi.get_instance')
    def test_update_in_db(self, mock_get_instance):
        # mock_db_obj has as_dict function that returns a dict
        mock_db_obj = mock.Mock()
        mock_db_obj.as_dict.return_value = {"attr_foo": "123"}

        # mock_db has get_by_primary_key function that returns mock_db_obj
        mock_db = mock.Mock()
        mock_db.get_by_primary_key.return_value = mock_db_obj

        # set the dbapi.get_instance to return mock_db
        mock_get_instance.return_value = mock_db

        # create new_class with db field pointing to mock_db
        new_class_name = 'new_class'
        _db_model = mock.Mock()
        attributes = {"attr_foo": str}
        new_class = baseObject.APIBaseObject.class_builder(
            new_class_name, _db_model, attributes)

        new_obj = new_class.update_in_db("any_key", {"attr_foo": "123"})
        observed = new_obj.attr_foo
        expected = "123"
        self.assertEqual(observed, expected)
        # also assert get_by_primary_key(), save(), update() has called once
        mock_db.get_by_primary_key.assert_called_once()
        mock_db_obj.update.assert_called_once()
        mock_db_obj.save.assert_called_once()

    """
    test delete_from_db
    """
    # mock db and mock db_obj
    # create mock_db_obj has attribute "attr_foo" with value "123"
    @patch('gluon.api.baseObject.dbapi.get_instance')
    def test_delete_from_db(self, mock_get_instance):
        # mock_db_obj
        mock_db_obj = mock.Mock()

        # mock_db has get_by_primary_key function that returns mock_db_obj
        mock_db = mock.Mock()
        mock_db.get_by_primary_key.return_value = mock_db_obj

        # set the dbapi.get_instance to return mock_db
        mock_get_instance.return_value = mock_db

        # create new_class with db field pointing to mock_db
        new_class_name = 'new_class'
        _db_model = mock.Mock()
        attributes = {"attr_foo": str}
        new_class = baseObject.APIBaseObject.class_builder(
            new_class_name, _db_model, attributes)

        new_class.delete_from_db("any_key")

        # assert get_by_primary_key(), delete()has called once
        mock_db.get_by_primary_key.assert_called_once()
        mock_db_obj.delete.assert_called_once()


class APIBaseListTestCase(base.APITestCase):

    def setUp(self):
        super(APIBaseListTestCase, self).setUp()
        pass

    """
    test class_builder
    """
    # create api_object_class whose instances will be elements of list
    # create new_class by calling class_builder with api_object_class
    @patch('gluon.api.baseObject.dbapi.get_instance')
    def test_class_builder(self, mock_get_instance):
        _db_model = type("FooDb", (object, ), {"foo": str})
        api_object_class = baseObject.APIBaseObject.class_builder(
            "FooAPI", _db_model, {"foo": str})
        class_name = 'FooListAPI'
        list_name = "listOfFoo"

        new_class = baseObject.APIBaseList.class_builder(
            class_name, list_name, api_object_class)

        self.assertEqual(new_class.list_name, "listOfFoo")
        self.assertEqual(new_class.api_object_class, api_object_class)

        # test assigning valuse to the new_api_list
        # its listOfFoo should only take list of FooClass objects
        new_api_list = new_class()
        # case 1: throws error if assign list of string
        expected_exception = None
        try:
            new_api_list.listOfFoo = ["foo"]
        except Exception as e:
            expected_exception = e
        self.assertIsNotNone(expected_exception)
        # case 2: NO error if assign list of FooClass objects
        expected_exception = None
        try:
            new_api_list.listOfFoo = [api_object_class()]
        except Exception as e:
            expected_exception = e
        self.assertIsNone(expected_exception)

    """
    test build
    """
    # create api_object_class whose instances will be elements of list
    # create new_class by calling class_builder with this api_object_class
    # mock the db to return a list of db_objs
    # call new_class.build() with the mock db data to generate api_obj_list
    @patch('gluon.api.baseObject.dbapi.get_instance')
    def test_build(self, mock_get_instance):
        _db_model = type("FooDb", (object, ), {"foo": str})
        api_object_class = baseObject.APIBaseObject.class_builder(
            "FoodAPI", _db_model, {"foo": str})
        class_name = 'FooListAPI'
        list_name = "listOfFoo"

        new_class = baseObject.APIBaseList.class_builder(
            class_name, list_name, api_object_class)

        # mock db setups that will return a list of db_obj
        mock_db_obj = mock.Mock()
        mock_db_obj.as_dict.return_value = {"foo": "123"}
        mock_db = mock.Mock()
        mock_db.get_list.return_value = [mock_db_obj]
        mock_get_instance.return_value = mock_db

        # start testing by calling build() on new_class
        api_obj_list = new_class.build()
        # listOfFoo should contain one element
        self.assertEqual(len(api_obj_list.listOfFoo), 1)
        # this element should have foo field with value "123"
        api_obj = api_obj_list.listOfFoo[0]
        self.assertEqual(api_obj.foo, "123")


class RootObjectControllerTestCase(base.APITestCase):

    def setUp(self):
        super(RootObjectControllerTestCase, self).setUp()
        pass

    """
    test class_builder
    """
    # FIXME write test cases for this function
    # have trouble with @wsme_pecan.wsexpose
    @patch('gluon.managers.manager_base.get_api_manager')
    @patch('gluon.api.baseObject.APIBaseList.class_builder')
    @patch('gluon.api.baseObject.wsme_pecan.wsexpose')
    def test_class_builder(self,
                           mock_wsexpose,
                           mock_APIBaseList_class_builder,
                           mock_get_api_manager):
        api_object_class = mock.Mock()
        name = "FooController"
        primary_key_type = str
        api_name = "foo"
        list_object_class = mock.Mock()
        mock_APIBaseList_class_builder.return_value = list_object_class

        baseObject.RootObjectController.class_builder(
            name, api_object_class, primary_key_type, api_name)
        pass


class RootSubObjectControllerTestCase(base.APITestCase):

    def setUp(self):
        super(RootSubObjectControllerTestCase, self).setUp()
        pass

    """
    test class_builder
    """
    # FIXME write test cases for this function
    # have trouble with @wsme_pecan.wsexpose
    def test_class_builder(self):
        pass
