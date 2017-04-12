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

import os

from oslo_config import cfg

API_OPTS = [
    cfg.IntOpt('port',
               default=2705,
               help='The port for the proton API server'),
    cfg.StrOpt('host',
               default='127.0.0.1',
               help='The listen IP for the proton API server'),
    cfg.StrOpt('service_list',
               default='*',
               help='Comma separated list of service models'),
    cfg.StrOpt('etcd_host',
               default='127.0.0.1',
               help='etcd host'),
    cfg.IntOpt('etcd_port',
               default=2379,
               help='etcd port'),
    cfg.StrOpt('auth_strategy',
               default='noauth',
               help='the type of authentication to use'),
    cfg.BoolOpt('debug',
                default=True,
                help='debug')
]

PATH_OPTS = [
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '../')),
               help='Directory where gluon python module is installed.'),
    cfg.StrOpt('bindir',
               default='$pybasedir/bin',
               help='Directory where gluon binaries are installed.'),
    cfg.StrOpt('state_path',
               default='$pybasedir',
               help="Top-level directory for maintaining gluon's state."),
]

SQL_OPTS = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine to use.'),
]

CONF = cfg.CONF

CONF.register_opts(API_OPTS, 'api')

CONF.register_opts(PATH_OPTS, 'path')

CONF.register_opts(SQL_OPTS, 'database')


def list_opts():
    return {'api': API_OPTS,
            'path': PATH_OPTS,
            'database': SQL_OPTS}
