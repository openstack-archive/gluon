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
import sys

import click
import json
import pkg_resources
from requests import delete
from requests import get
from requests import post
from requests import put
import yaml

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
    test load_model
    """
    def test_load_model(self):
        observed = cli.load_model("gluon.tests.particleGenerator",
                                  "",
                                  "models")
        expected = {'GluonInternalPort':
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
                       'type': 'string'
                       }
                      }
                     }
                    }
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
        self.assertRaises(exc.GluonClientException,
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
        rsp.content = "abc"
        mock_post.return_value = rsp
        jsonValue = {"foo": "bar"}
        self.assertRaises(exc.MalformedResponseBody,
                          cli.do_post,
                          'www.gluonURL.net',
                          jsonValue)
        self.assertEqual("a", "b")

    # sunny day
    @mock.patch.object(cli, "post")
    def test_do_post(self, mock_post):
        rsp = mock.Mock()
        rsp.status_code = 200
        rsp.content = '{"result":"successful"}'
        mock_post.return_value = rsp
        jsonValue = {"foo":"bar"}
        observed = cli.do_post('www.gluonURL.net', jsonValue)
        expected = {"result": "successful"}
        self.assertEqual(expected, observed)
