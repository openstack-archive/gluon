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

    # every testcase file need to have its own setUp method
    # normally just inherit its parent's setup by cally super().setUP()
    def setUp(self):
        super(ApiTestCase, self).setUp()

    """
    simple test for setup
    """
    # Usually the first thing I do in a test case file to make sure it
    # is set up correctly. So I create a simple test case and run tox on it:
    # tox -e py27 gluon.tests.db.sqlalchemy.test_api
    # After it is confirmed working, this simple test method can be deleted
    def test_simple_test(self):
        self.assertEqual('a', 'a')

    """
    test _create_facade_lazily()
    """
    # The _create_facade_lazily() function calls the function:
    # db_session.EngineFacade.from_config(CONF).
    # Notice that db_session is imported from oslo_db.sqlalchemy.
    # We usually will mock imported modules.
    # Here is an article that gives good explanation and examples:
    # https://www.toptal.com/python/an-introduction-to-mocking-in-python

    # So in our case, we need to mock db_session with @mock.patch()
    # and set db_session.EngineFacade.from_config(CONF) return value.

    # And what we are testing is that if _FACADE is None, the Mock function
    # will be called. And after calling _create_facade_lazily(), _FACADE is not
    # None
    @mock.patch('gluon.db.sqlalchemy.api.db_session')
    def test_create_facade_lazily(self, mock_db_session):
        mock_return = mock.Mock()
        mock_db_session.EngineFacade.from_config.return_value = mock_return
        api._FACADE = None

        api._create_facade_lazily()

        # test that the mock db_session.EngineFacade.from_config(CONF)
        # is call once
        mock_db_session.EngineFacade.from_config.assert_called_with(api.CONF)
        # _FACADE should not be None anymore because it is assigned with the
        # value return from mock_db_session.EngineFacade.from_config()
        self.assertIsNotNone(api._FACADE)
        # _FACADE should equal to what is return from
        # db_session.EngineFacade.from_config(CONF)
        self.assertEqual(api._FACADE, mock_return)

    """
    test get_engine
    """
    # The get_engine() function calls _create_facade_lazily() which has been
    # tested aboved so we can mocked it and controll its return value
    @mock.patch('gluon.db.sqlalchemy.api._create_facade_lazily')
    def test_get_engine(self, mock_create_facade_lazily):
        re = mock.Mock()
        mock_create_facade_lazily.return_value.get_engine.return_value = re

        observed = api.get_engine()

        # _create_facade_lazily should have call one
        mock_create_facade_lazily.assert_called_once()
        # api.get_engine() should return the value we set in
        # mock_create_facade_lazily.return_value.get_engine.return_value
        self.assertEqual(re, observed)
