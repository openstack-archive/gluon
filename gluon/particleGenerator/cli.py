# Copyright (c) 2016 Nokia, Inc.
# All Rights Reserved
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

from gluon.common import exception as exc
from gluon.particleGenerator.generator import load_model


def print_basic_usage(argv, model_list):
    print("Usage: %s --api <api_name> [OPTIONS] COMMAND[ARGS]..." %
          os.path.basename(argv[0]))
    print("\nOptions:")
    print("--api TEXT      Name of API, one of %s" % model_list)
    print("--port INTEGER  Port of endpoint (OS_PROTON_PORT)")
    print("--host TEXT     Host of endpoint (OS_PROTON_HOST)")
    print("--help          Show this message and exit.")


def get_api_model(argv, model_list):

    try:
        arg_idx = argv.index("--api")
        val_idx = arg_idx + 1
    except ValueError:
        # If there is only one API model, --api is not needed
        if len(model_list) == 1:
            return model_list[0]
        print("--api is not specified!\n")
        print_basic_usage(argv, model_list)
        sys.exit(-1)
    try:
        api_name = argv[val_idx]
    except IndexError:
        print("API name is not specified!\n")
        print_basic_usage(argv, model_list)
        sys.exit(-1)
    if api_name not in model_list:
        print("Invalid API name!\n")
        print_basic_usage(argv, model_list)
        sys.exit(-1)
    del argv[arg_idx]
    del argv[arg_idx]
    return api_name


def get_model_list(package_name, model_dir):
    model_list = list()
    for f in pkg_resources.resource_listdir(package_name, model_dir):
        if f == 'base':
            continue
        model_list.append(f)
    return model_list


def get_token():
    auth_url = os.environ.get('OS_AUTH_URL')
    tenant = os.environ.get('OS_TENANT_NAME')
    user = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')

    if not auth_url or not tenant or not user or not password:
        return None

    auth_info = {'auth': {
        'tenantName': tenant,
        'passwordCredentials':
            {'username': user, 'password': password}
    }}

    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json'}

    resp = post(auth_url + '/v2.0/tokens', json=auth_info, headers=headers)

    if resp.status_code != 200 and resp.status_code != 201:
        raise exc.GluonClientException('Bad return status %d'
                                       % resp.status_code,
                                       status_code=resp.status_code)

    json_resp = resp.json()

    return json_resp.get('access').get('token').get('id')


def json_get(url):
    headers = {'X-Auth-Token': get_token()}
    resp = get(url, headers=headers)

    if resp.status_code != 200:
        raise exc.GluonClientException('Bad return status %d'
                                       % resp.status_code,
                                       status_code=resp.status_code)
    try:
        rv = json.loads(resp.content)
    except Exception as e:
        raise exc.MalformedResponseBody(reason="JSON unreadable: %s on %s"
                                               % (e.args[0], resp.content))
    return rv


def do_delete(url):
    headers = {'X-Auth-Token': get_token()}
    resp = delete(url, headers=headers)

    if resp.status_code != 200 and resp.status_code != 204:
        raise exc.GluonClientException('Bad return status %d'
                                       % resp.status_code,
                                       status_code=resp.status_code)


def do_post(url, values):
    headers = {'X-Auth-Token': get_token()}
    resp = post(url, json=values, headers=headers)

    if resp.status_code != 200 and resp.status_code != 201:
        raise exc.GluonClientException('Bad return status %d'
                                       % resp.status_code,
                                       status_code=resp.status_code)
    try:
        rv = json.loads(resp.content)
    except Exception as e:
        raise exc.MalformedResponseBody(reason="JSON unreadable: %s on %s"
                                               % (e.args[0], resp.content))
    return rv


def do_put(url, values):
    headers = {'X-Auth-Token': get_token()}
    resp = put(url, json=values, headers=headers)

    if resp.status_code != 200:
        raise exc.GluonClientException('Bad return status %d'
                                       % resp.status_code,
                                       status_code=resp.status_code)
    try:
        rv = json.loads(resp.content)
    except Exception as e:
        raise exc.MalformedResponseBody(reason="JSON unreadable: %s on %s"
                                               % (e.args[0], resp.content))
    return rv


def make_url(host, port, *args):
    url = "http://%s:%d/proton" % (host, port)
    for arg in args:
        url = "%s/%s" % (url, arg)
    return url


def make_list_func(api_model, tablename):
    def list_func(**kwargs):
        url = make_url(kwargs["host"], kwargs["port"], api_model, tablename)
        result = json_get(url)
        print(json.dumps(result, indent=4))
        return result

    return list_func


def make_show_func(api_model, tablename, primary_key):
    def show_func(**kwargs):
        url = make_url(kwargs["host"], kwargs["port"], api_model, tablename,
                       kwargs[primary_key])
        result = json_get(url)
        print(json.dumps(result, indent=4))
        return result

    return show_func


def make_create_func(api_model, tablename):
    def create_func(**kwargs):
        url = make_url(kwargs["host"], kwargs["port"], api_model, tablename)
        del kwargs["host"]
        del kwargs["port"]
        data = {}
        for key, val in six.iteritems(kwargs):
            if val is not None:
                data[key] = val
        result = do_post(url, data)
        print(json.dumps(result, indent=4))

    return create_func


def make_update_func(api_model, tablename, primary_key):
    def update_func(**kwargs):
        url = make_url(kwargs["host"], kwargs["port"], api_model, tablename,
                       kwargs[primary_key])
        del kwargs["host"]
        del kwargs["port"]
        del kwargs[primary_key]
        data = {}
        for key, val in six.iteritems(kwargs):
            if val is not None:
                data[key] = val
        result = do_put(url, data)
        print(json.dumps(result, indent=4))

    return update_func


def make_delete_func(api_model, tablename, primary_key):
    def delete_func(**kwargs):
        url = make_url(kwargs["host"], kwargs["port"], api_model, tablename,
                       kwargs[primary_key])
        do_delete(url)

    return delete_func


def get_primary_key(table_data):
    primary = []
    for k, v in six.iteritems(table_data['attributes']):
        if 'primary' in v:
            primary = k
            break
    # If not specified, a UUID is used as the PK
    if not primary:
        table_data['attributes']['uuid'] = \
            dict(type='string', length=36, primary=True, required=True)
        primary = 'uuid'
    table_data['primary'] = primary
    return primary


def set_type(kwargs, col_desc):
    if col_desc['type'] == 'string':
        pass
    elif col_desc['type'] == 'integer':
        kwargs["type"] = int
    elif col_desc['type'] == 'number':
        kwargs["type"] = float
    elif col_desc['type'] == 'boolean':
        kwargs["type"] = bool
    elif col_desc['type'] == 'enum':
        kwargs["type"] = click.Choice(col_desc['values'])
    else:
        raise Exception('Unknown column type %s' % col_desc['type'])


def proc_model(cli, package_name="unknown",
               model_dir="unknown",
               api_model="unknown",
               hostenv="unknown",
               portenv="unknown",
               hostdefault="unknown",
               portdefault=0):
    # print("loading model")
    model = load_model(package_name, model_dir, api_model)
    for table_name, table_data in six.iteritems(model['api_objects']):
        get_primary_key(table_data)
    for table_name, table_data in six.iteritems(model['api_objects']):
        try:
            attrs = {}
            for col_name, col_desc in six.iteritems(table_data['attributes']):
                try:
                    # Step 1: deal with object xrefs
                    if col_desc['type'] in model['api_objects']:
                        # If referencing another object,
                        # get the type of its primary key
                        tgt_name = col_desc['type']
                        tgt_data = model['api_objects'][tgt_name]
                        primary_col = tgt_data['primary']
                        table_data["attributes"][col_name]['type'] = \
                            tgt_data["attributes"][primary_col]["type"]
                    # Step 2: convert our special types to ones a CLI likes
                    if col_desc['type'] == 'uuid':
                        # UUIDs, from a CLI perspective,  are a form of
                        # string
                        table_data["attributes"][col_name]['type'] = 'string'
                        table_data["attributes"][col_name]['length'] = 64
                    if col_desc.get('primary', False):
                        attrs['_primary_key'] = col_name
                except Exception:
                    print('During processing of attribute ', col_name)
                    raise
            if '_primary_key' not in attrs:
                raise Exception("One and only one primary key has to "
                                "be given to each column")
            attrs['__tablename__'] = table_data['api']['plural_name']

            # chop off training 's'
            attrs['__objname__'] = table_data['api']['name']
            #
            # Create CRUD commands for the table
            #
            hosthelp = "Host of endpoint (%s) " % hostenv
            porthelp = "Port of endpoint (%s) " % portenv
            list = make_list_func(api_model, attrs['__tablename__'])
            list.func_name = "%s-list" % (attrs['__objname__'])
            list = click.option("--host", envvar=hostenv,
                                default=hostdefault, help=hosthelp)(list)
            list = click.option("--port", envvar=portenv,
                                default=portdefault, help=porthelp)(list)
            cli.command()(list)

            show = make_show_func(api_model, attrs['__tablename__'],
                                  attrs['_primary_key'])
            show.func_name = "%s-show" % (attrs['__objname__'])
            show = click.option("--host", envvar=hostenv,
                                default=hostdefault, help=hosthelp)(show)
            show = click.option("--port", envvar=portenv,
                                default=portdefault, help=porthelp)(show)
            show = click.argument(attrs['_primary_key'])(show)
            cli.command()(show)

            create = make_create_func(api_model, attrs['__tablename__'])
            create.func_name = "%s-create" % (attrs['__objname__'])
            create = click.option("--host", envvar=hostenv,
                                  default=hostdefault, help=hosthelp)(create)
            create = click.option("--port", envvar=portenv,
                                  default=portdefault, help=porthelp)(create)
            for col_name, col_desc in six.iteritems(table_data['attributes']):
                kwargs = {}
                option_name = "--" + col_name
                kwargs["default"] = None
                required = col_desc.get('required', False)
                kwargs["help"] = col_desc.get('description', "no description")
                if required:
                    kwargs["required"] = True
                set_type(kwargs, col_desc)
                create = click.option(option_name, **kwargs)(create)
            cli.command()(create)

            update = make_update_func(api_model, attrs['__tablename__'],
                                      attrs['_primary_key'])
            update.func_name = "%s-update" % (attrs['__objname__'])
            update = click.option("--host", envvar=hostenv,
                                  default=hostdefault, help=hosthelp)(update)
            update = click.option("--port", envvar=portenv,
                                  default=portdefault, help=porthelp)(update)
            for col_name, col_desc in six.iteritems(table_data['attributes']):
                if col_name == attrs['_primary_key']:
                    continue
                kwargs = {}
                option_name = "--" + col_name
                kwargs["default"] = None
                kwargs["help"] = col_desc.get('description', "no description")
                set_type(kwargs, col_desc)
                update = click.option(option_name, **kwargs)(update)
            update = click.argument(attrs['_primary_key'])(update)
            cli.command()(update)

            del_func = make_delete_func(api_model, attrs['__tablename__'],
                                        attrs['_primary_key'])
            del_func.func_name = "%s-delete" % (attrs['__objname__'])
            del_func = click.option("--host", envvar=hostenv,
                                    default=hostdefault,
                                    help=hosthelp)(del_func)
            del_func = click.option("--port", envvar=portenv,
                                    default=portdefault,
                                    help=porthelp)(del_func)
            del_func = click.argument(attrs['_primary_key'])(del_func)
            cli.command()(del_func)

        except Exception:
            print('During processing of table ', table_name)
            raise
