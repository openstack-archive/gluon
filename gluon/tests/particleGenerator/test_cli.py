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
import os
import six
from subprocess import call
import sys
import types

import click
from click.testing import CliRunner
import json
import pkg_resources
from requests import delete
from requests import get
from requests import post
from requests import put
import yaml

from gluon.cmd.cli import dummy
from gluon.common import exception as exc
from gluon.particleGenerator import cli
from gluon.tests.particleGenerator import base as partgen_base


class CliTestCase(partgen_base.ParticleGeneratorTestCase):

    def setUp(self):
        super(CliTestCase, self).setUp()

    # print_basic_usage contains just calls the print function
    def test_print_basic_usage(self):
        pass

    """
    test cli.get_api_model
    """
    # If there is only one API model, --api is not needed
    @patch('gluon.particleGenerator.cli.print_basic_usage')
    def test_get_api_model_oneAPI(self, mock_print_basic_usage):
        argv = []
        model_list = ["model_1"]
        expected = "model_1"
        observed = cli.get_api_model(argv, model_list)
        self.assertEqual(expected, observed)

    # API name is not specified
    @patch('gluon.particleGenerator.cli.print_basic_usage')
    def test_get_api_model_noAPIName(self, mock_print_basic_usage):
        argv = ["--api"]
        model_list = ["model_1"]
        self.assertRaises(SystemExit, cli.get_api_model, argv, model_list)
        mock_print_basic_usage.assert_called_once()

    # Invalid API name
    @patch('gluon.particleGenerator.cli.print_basic_usage')
    def test_get_api_model_InvalidAPIName(self, mock_print_basic_usage):
        argv = ["--api", "invalid_api_name"]
        model_list = ["model_1"]
        self.assertRaises(SystemExit, cli.get_api_model, argv, model_list)
        mock_print_basic_usage.assert_called_once()

    # sunny day
    @patch('gluon.particleGenerator.cli.print_basic_usage')
    def test_get_api_model(self, mock_print_basic_usage):
        argv = ["--api", "model_1"]
        model_list = ["model_1"]
        expected = "model_1"
        observed = cli.get_api_model(argv, model_list)
        self.assertEqual(expected, observed)

    """
    test get_model_list
    """
    def test_get_model_list(self):
        observed = cli.get_model_list("gluon.tests.particleGenerator",
                                      "models")
        expected = ['test_model.yaml']
        self.assertEqual(expected, observed)

    """
    test json_get
    """
    # Bad return status
    @mock.patch.object(cli, "get")
    def test_json_get_badStatus(self, mock_get):
        rsp = mock.Mock()
        rsp.status_code = 404
        mock_get.return_value = rsp
        self.assertRaises(exc.GluonClientException,
                          cli.json_get,
                          'www.gluonURL.net')

    # json unreadable
    @mock.patch.object(cli, "get")
    def test_json_get_badJson(self, mock_get):
        rsp = mock.Mock()
        rsp.status_code = 200
        rsp.content = '{"foo"="bar"}'
        mock_get.return_value = rsp
        self.assertRaises(exc.MalformedResponseBody,
                          cli.json_get,
                          'www.gluonURL.net')

    # sunny day
    @mock.patch.object(cli, "get")
    def test_json_get(self, mock_get):
        rsp = mock.Mock()
        rsp.status_code = 200
        rsp.content = '{"foo": "bar"}'
        mock_get.return_value = rsp
        observed = cli.json_get('www.gluonURL.net')
        expected = {"foo": "bar"}
        self.assertEqual(expected, observed)

    """
    test do_delete
    """
    # bad return status
    @mock.patch.object(cli, "delete")
    def test_do_delete_badStatus(self, mock_del):
        rsp = mock.Mock()
        rsp.status_code = 404
        mock_del.return_value = rsp
        self.assertRaises(exc.GluonClientException,
                          cli.do_delete,
                          'www.gluonURL.net')

    """
    test do_post
    """
    # bad retrun status
    @mock.patch.object(cli, "post")
    def test_do_post_badStatus(self, mock_post):
        rsp = mock.Mock()
        rsp.status_code = 404
        mock_post.return_value = rsp
        jsonValue = {"foo": "bar"}
        self.assertRaises(exc.GluonClientException,
                          cli.do_post,
                          'www.gluonURL.net',
                          jsonValue)

    # bad response body
    @mock.patch.object(cli, "post")
    def test_do_post_badRspBody(self, mock_post):
        rsp = mock.Mock()
        rsp.status_code = 200
        rsp.content = "response in wrong json format"
        mock_post.return_value = rsp
        jsonValue = {"foo": "bar"}
        self.assertRaises(exc.MalformedResponseBody,
                          cli.do_post,
                          'www.gluonURL.net',
                          jsonValue)

    # sunny day
    @mock.patch.object(cli, "post")
    def test_do_post(self, mock_post):
        rsp = mock.Mock()
        rsp.status_code = 200
        rsp.content = '{"result":"successful"}'
        mock_post.return_value = rsp
        jsonValue = {"foo": "bar"}
        observed = cli.do_post('www.gluonURL.net', jsonValue)
        expected = {"result": "successful"}
        self.assertEqual(expected, observed)

    """
    test do_put
    """
    # bad return status
    @mock.patch.object(cli, "put")
    def test_do_put_badStatus(self, mock_put):
        rsp = mock.Mock()
        rsp.status_code = 404
        mock_put.return_value = rsp
        jsonValue = {"foo": "bar"}
        self.assertRaises(exc.GluonClientException,
                          cli.do_put,
                          'www.gluonURL.net',
                          jsonValue)

    # json unreadable
    @mock.patch.object(cli, "put")
    def test_do_put_badJason(self, mock_put):
        rsp = mock.Mock()
        rsp.status_code = 200
        rsp.content = "response in wrong json format"
        mock_put.return_value = rsp
        jsonValue = {"foo": "bar"}
        self.assertRaises(exc.MalformedResponseBody,
                          cli.do_put,
                          'www.gluonURL.net',
                          jsonValue)

    # sunny day
    @mock.patch.object(cli, "put")
    def test_do_put(self, mock_put):
        rsp = mock.Mock
        rsp.status_code = 200
        rsp.content = '{"result": "successful"}'
        mock_put.return_value = rsp
        jsonValue = {"foo": "bar"}
        observed = cli.do_put('www.gluonURL.net', jsonValue)
        expected = {"result": "successful"}
        self.assertEqual(expected, observed)

    """
    test make_url
    """
    def test_make_url(self):
        host = 'gluonURL.net'
        port = 8080
        args = ['foo', 'bar', 'baz']
        expected = "http://gluonURL.net:8080/proton/foo/bar/baz"
        observed = cli.make_url(host, port, *args)
        self.assertEqual(expected, observed)

    """
    test make_list_func
    """
    @mock.patch.object(cli, "json_get")
    def test_make_list_func(self, mock_json_get):
        kwargs = {"host": "gluonURL.net", "port": 8080}
        api_model = "apimodel"
        tablename = "tablename"
        mock_json_get.return_value = {"result": "successful"}
        list_func = cli.make_list_func(api_model, tablename)
        observed = list_func(**kwargs)
        # self.assertIsNone(observed)
        expected = {"result": "successful"}
        self.assertEqual(expected, observed)

    """
    test make_show_func
    """
    @mock.patch.object(cli, "json_get")
    def test_make_show_func(self, mock_json_get):
        kwargs = {"host": "gluonURL.net", "port": 8080, "id": 1}
        api_model = "apimodel"
        tablename = "tablename"
        primary_key = "id"
        mock_json_get.return_value = {"result": "successful"}
        show_func = cli.make_show_func(api_model, tablename, primary_key)
        observed = show_func(**kwargs)
        # self.assertIsNone(observed)
        expected = {"result": "successful"}
        self.assertEqual(expected, observed)

    """
    test make_create_func
    """
    # pretend adding a new user
    @mock.patch.object(cli, "do_post")
    def test_make_create_func(self, mock_do_post):
        kwargs = {"host": "gluonURL.net", "port": 8080, "id": 1,
                  "firstname": "Jane", "lastName": "Doe"}
        api_model = "apiModel"
        tablename = "user"
        mock_do_post.return_value = '{"result": "successful"}'
        create_func = cli.make_create_func(api_model, tablename)
        observed = create_func(**kwargs)
        self.assertIsNone(observed)

    """
    test make_update_func
    """
    # pretend updating an user
    @mock.patch.object(cli, "do_put")
    def test_make_update_func(self, mock_do_put):
        kwargs = {"host": "gluonURL.net", "port": 8080, "id": 1,
                  "firstname": "Jane", "lastName": "Doe"}
        api_model = "apiModel"
        tablename = "user"
        primary_key = "id"
        mock_do_put.return_value = '{"result": "successful"}'
        update_func = cli.make_update_func(api_model, tablename, primary_key)
        observed = update_func(**kwargs)
        self.assertIsNone(observed)

    """
    test make_delete_func
    """
    # pretend deleting an user
    @mock.patch.object(cli, "do_delete")
    def test_make_delete_func(self, mock_do_delete):
        kwargs = {"host": "gluonURL.net", "port": 8080, "id": 1}
        api_model = "apiModel"
        tablename = "user"
        primary_key = "id"
        mock_do_delete.return_value = '{"result": "successful"}'
        delete_func = cli.make_delete_func(api_model, tablename, primary_key)
        observed = delete_func(**kwargs)
        self.assertIsNone(observed)

    """
    test get_primary_key
    """
    def test_get_primary_key(self):
        model = self.load_testing_model()
        table_data = model['api_objects']['Port']
        observed = cli.get_primary_key(table_data)
        expected = 'id'
        self.assertEqual(expected, observed)

    """
    test set_type
    """
    # string
    def test_set_type_string(self):
        kwargs = dict()
        col_desc = {"type": "string"}
        cli.set_type(kwargs, col_desc)
        self.assertNotIn("type", kwargs)

    # integer
    def test_set_type_integer(self):
        kwargs = dict()
        col_desc = {"type": "integer"}
        cli.set_type(kwargs, col_desc)
        observed = kwargs['type']
        expected = int
        self.assertEqual(expected, observed)

    # enum
    @mock.patch.object(cli.click, "Choice")
    def test_set_type_enum(self, mock_choice):
        kwargs = dict()
        col_desc = {"type": "enum", "values": ["a", "b", "c"]}
        mock_choice.return_value = mock.Mock()
        cli.set_type(kwargs, col_desc)
        observed = kwargs['type']
        expected = mock_choice.return_value
        self.assertEqual(expected, observed)

    # boolean
    def test_set_type_boolean(self):
        kwargs = dict()
        col_desc = {"type": "boolean"}
        cli.set_type(kwargs, col_desc)
        observed = kwargs['type']
        expected = bool
        self.assertEqual(expected, observed)

    """
    test proc_model
    """
    # FIXME need to create test case for the poc_model function. It iterates
    # through the yaml file of each model and dynamically generates CRUD
    # command line operations using the click library.

    # The code below is an example copied from internet for testing click
    # using the CliRunner. But it requires the function being tested to be
    # decorated inside the testcase function.

    # For our example, these two lines calling click decorators
    # hello = click.argument('name')(hello)
    # hello = click.command()(hello)
    # need to be inside of test_proc_model_simpleExample(self).
    # otherwise, running this line
    # result = runner.invoke(hello, ['JimLi'])
    # will throw error complaining "hello not defined"

    # For proc_model(), it calls click libary decorators inside itself.
    """
    def test_proc_model_simpleExample(self):
        # version 1
        # @click.command()
        # @click.argument('name')
        # def hello( name ):
        #     click.echo('Hello {0} !'.format(name))

        # version 2
        def hello(name):
            click.echo('Hello {0} !'.format(name))
        hello = click.argument('name')(hello)
        hello = click.command()(hello)

        runner = CliRunner()
        result = runner.invoke(hello, ['JimLi'])
        assert result.exit_code == 0
        print("*******************************************")
        print(result.output)
        print("*******************************************")
        # self.assertEqual('a', 'b')
    """
