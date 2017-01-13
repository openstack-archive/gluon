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
from gluon.db.sqlalchemy import api
from gluon.tests import base


class ApiTestCase(base.TestCase):

    def setUp(self):
        super(ApiTestCase, self).setUp()

    """
    test _create_facade_lazily()
    """
    @mock.patch('gluon.db.sqlalchemy.api.db_session')
    def test_create_facade_lazily(self, mock_db_session):
        mock_return = mock.Mock()
        mock_db_session.EngineFacade.from_config.return_value = mock_return
        api._FACADE = None

        api._create_facade_lazily()

        mock_db_session.EngineFacade.from_config.assert_called_with(api.CONF)
        self.assertIsNotNone(api._FACADE)
        self.assertEqual(api._FACADE, mock_return)

    """
    test get_engine
    """
    @mock.patch('gluon.db.sqlalchemy.api._create_facade_lazily')
    def test_get_engine(self, mock_create_facade_lazily):
        re = mock.Mock()
        mock_create_facade_lazily.return_value.get_engine.return_value = re

        observed = api.get_engine()

        mock_create_facade_lazily.assert_called_once()
        self.assertEqual(re, observed)

    """
    test get_session
    """
    @mock.patch('gluon.db.sqlalchemy.api._create_facade_lazily')
    def test_get_session(self, mock_create_facade_lazily):
        re = mock.Mock()
        mock_create_facade_lazily.return_value.get_session.return_value = re

        observed = api.get_session()

        mock_create_facade_lazily.assert_called_once()
        self.assertEqual(re, observed)

    """
    test get_backend
    """
    @mock.patch('gluon.db.sqlalchemy.api.Connection')
    def test_get_backend(self, mock_Connection):
        api.get_backend()
        mock_Connection.assert_called_once()
 
    """
    test model_query
    """
    def test_model_query_with_session(self):
        model = mock.Mock()
        session = mock.Mock()
        query = mock.Mock()
        session.query.return_value = query
        observed=api.model_query(model, session=session)
        session.query.assert_called_once()
        self.assertEqual(query, observed)

    @mock.patch('gluon.db.sqlalchemy.api.get_session')
    def test_model_query_no_session(self, mock_get_session):
        model = mock.Mock()
        query = mock.Mock()
        session = mock.Mock()
        mock_get_session.return_value = session
        session.query.return_value = query
        observed = api.model_query(model)
        mock_get_session.assert_called_once()
        session.query.assert_called_once()
        self.assertEqual(query, observed)

    """
    test _paginate_query
    """
    """
    @mock.patch('gluon.db.sqlalchemy.api.model_query')
    def test_paginate_query(self, mock_model_query):
        model = mock.MagicMock()
        queryReturn = mock.Mock()
        query = None
        sort_key = mock.Mock()
        sort_keys = [mock.Mock()]
        mock_model_query.return_value = queryReturn

        observed = api._paginate_query(model, limit=None, marker=None,
                                        sort_key=sort_key, sort_dir=None,
                                        query=query)
    """
