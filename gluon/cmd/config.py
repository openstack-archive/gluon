#    Copyright 2015, Ericsson AB
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

from oslo_config import cfg

API_SERVICE_OPTS = [
    cfg.IntOpt('port',
               default=2705,
               help='The port for the proton API server'),
    cfg.StrOpt('host',
               default='127.0.0.1',
               help='The listen IP for the proton API server'),
    cfg.StrOpt('service_list',
               default='net-l3vpn',
               help='Comma separated list of service models'),
    cfg.StrOpt('etcd_host',
               default='127.0.0.1',
               help='etcd host'),
    cfg.IntOpt('etcd_port',
               default=2379,
               help='etcd port'),
    cfg.StrOpt('auth_strategy',
               default='noauth',
               help='the type of authentication to use')
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='api',
                         title='Options for the proton-api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)

BASE_URI_OPTS = [
    cfg.StrOpt('root_name',
               default='Gluon API',
               help='value for root.name'),

    cfg.StrOpt('root_description',
               default=("OpenStack Gluon is a port arbiter that maintains "
                        "a list of ports and bindings of different "
                        "network backends. A Proton Server is the API "
                        "server that hosts multiple Protons, i.e. "
                        "multiple sets of APIs."),
               help='value for root.default')
]

baseuri_group = cfg.OptGroup(name='baseuri',
                             title='values return by base uri in root.py')
CONF.register_group(baseuri_group)
CONF.register_opts(BASE_URI_OPTS, baseuri_group)

APP_OPTS = [
    cfg.StrOpt('root_controller',
               default='gluon.api.root.RootController',
               help='root controller for app'),

    cfg.ListOpt('modules',
                default=['gluon.api'],
                help='list of directories containing modules'),

    cfg.BoolOpt('debug',
                default=True,
                help='debug')
]
app_group = cfg.OptGroup(name='app',
                         title='constants used in app.py')
CONF.register_group(app_group)
CONF.register_opts(APP_OPTS, app_group)
