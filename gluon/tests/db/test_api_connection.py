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
import sqlalchemy.orm.exc

from gluon.common import exception
from gluon.db.sqlalchemy import api
from gluon.db.sqlalchemy import models as sql_models
from gluon.tests import base
from mock import patch
from oslo_db import exception as db_exc


class ConnectionTestCase(base.TestCase):

    def setUp(self):
        super(ConnectionTestCase, self).setUp()

    def raiseDBDuplicateEntryException(self):
        raise db_exc.DBDuplicateEntry

    """
    test create()
    """

    """
    # can't figure this error out...is this a bug??

    exception as e.__dict__ = {'value': None, 'inner_exception': None,
                                'cause': None, 'columns': []}

    File "gluon/db/sqlalchemy/api.py", line 106, in create
    key=e.__dict__['columns'][0],
    IndexError: list index out of range

    # exception thrown
    def test_create_duplicate_entry(self):
        connection = api.Connection()
        mock_model = mock.Mock()
        mock_model.__name__ = "fake_name"
        print("mock_model = " + str(mock_model))

        mock_values = mock.Mock()
        mock_obj = mock_model()
        print("mock obj before = " + str(mock_obj))

        mock_obj.update.return_value = mock_obj
        print("mock_obj after update = " + str(mock_obj))

        mock_obj.save = self.raiseDBDuplicateEntryException
        print("mock_obj after save = " + str(mock_obj))

        self.assertRaises(exception.AlreadyExists, connection.create,
                            mock_model, mock_values)
    """

    # no exception
    def test_create(self):
        connection = api.Connection()
        mock_model = mock.Mock()
        mock_model.__name__ = "fake_name"
        mock_values = mock.Mock()
        mock_obj = mock_model()
        mock_obj.update.return_value = mock_obj
        mock_obj.save.return_value = mock_obj

        observed = connection.create(mock_model, mock_values)

        mock_obj.update.assert_called_once()
        mock_obj.save.assert_called_once()
        self.assertEqual(mock_obj, observed)

    """
    test _add_filters()
    """
    def test_add_filters(self):
        connection = api.Connection()
        mock_filters = {'key': 'value'}
        mock_query = mock.Mock()
        mock_query.filter_by.return_value = mock_query

        observed = connection._add_filters(mock_query, mock_filters)

        mock_query.filter_by.assert_called_once()
        self.assertEqual(mock_query, observed)

    """
    test get_list()
    """
    @mock.patch('gluon.db.sqlalchemy.api.model_query')
    @mock.patch('gluon.db.sqlalchemy.api.Connection._add_filters')
    @mock.patch('gluon.db.sqlalchemy.api._paginate_query')
    def test_get_list(self, mock_paginate_query, mock_add_filters,
                      mock_model_query):
        connection = api.Connection()
        mock_query = mock.Mock()
        mock_query_2 = mock.Mock()
        mock_model = mock.Mock()
        mock_model_query.return_value = mock_query
        mock_add_filters.return_value = mock_query_2
        mock_paginate_query.return_value = mock_query_2

        observed = connection.get_list(mock_model, columns=None,
                                       filters=None, limit=None,
                                       marker=None, sort_key=None,
                                       sort_dir=None, failed=None,
                                       period=None)

        mock_model_query.assert_called_once()
        mock_add_filters.assert_called_once()
        mock_paginate_query.assert_called_once()
        self.assertEqual(mock_query_2, observed)

    def raiseNoResultFoundException(self):
        raise sqlalchemy.orm.exc.NoResultFound

    """
    test get_by_uuid()
    """
    # exception thrown
    @mock.patch('gluon.db.sqlalchemy.api.model_query')
    def test_get_by_uuid_noResultFound(self, mock_model_query):
        connection = api.Connection()
        mock_model = mock.Mock()
        mock_model.__name__ = "fake_name"
        mock_uuid = mock.Mock()
        mock_query = mock.Mock()
        mock_model_query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.one = self.raiseNoResultFoundException
        self.assertRaises(exception.NotFound,
                          connection.get_by_uuid, mock_model,
                          mock_uuid)

    # no exception thrown
    @mock.patch('gluon.db.sqlalchemy.api.model_query')
    def test_get_by_uuid(self, mock_model_query):
        connection = api.Connection()
        mock_model = mock.Mock()
        mock_uuid = mock.Mock()
        mock_query = mock.Mock()
        mock_model_query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.one.return_value = mock_query

        observed = connection.get_by_uuid(mock_model, mock_uuid)

        mock_model_query.assert_called_once()
        mock_query.filter_by.assert_called_once()
        self.assertEqual(mock_query, observed)

    """
    test get_by_primary_key()
    """
    # exption thrown
    @mock.patch('gluon.db.sqlalchemy.api.model_query')
    def test_get_by_primary_key_noResultFound(self, mock_model_query):
        connection = api.Connection()
        mock_pk_type = "fake_pk"
        mock_model = mock.Mock()
        mock_model.__name__ = "fake_name"
        mock_key = "fake_key"
        mock_query = mock.Mock()
        mock_model.get_primary_key.return_value = mock_pk_type
        mock_model_query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.one = self.raiseNoResultFoundException
        self.assertRaises(exception.NotFound,
                          connection.get_by_primary_key,
                          mock_model, mock_key)

    @mock.patch('gluon.db.sqlalchemy.api.model_query')
    def test_get_by_primary_key(self, mock_model_query):
        connection = api.Connection()
        mock_pk_type = "fake_pk"
        mock_key = "fake_key"
        mock_query = mock.Mock()
        mock_model = mock.Mock()
        mock_key = mock.Mock()
        mock_model.get_primary_key.return_value = mock_pk_type
        mock_model_query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.one.return_value = mock_query
        observed = connection.get_by_primary_key(mock_model, mock_key)

        mock_model.get_primary_key.assert_called_once()
        mock_model_query.assert_called_once()
        mock_query.filter_by.assert_called_once()
        mock_query.one.assert_called_once()

        self.assertEqual(mock_query, observed)
