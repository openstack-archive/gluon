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

import json
import os
import sys
import time
from Queue import Queue
from threading import Thread

import etcd

from oslo_config import cfg
from oslo_log import log as logging

from gluon.shim_example.api_models.net_l3vpn import ApiNetL3VPN
from gluon.shim_example.backends.dummy_net_l3vpn import DummyNetL3VPN


class MyData:
    pass

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

ShimData = MyData()
ShimData.etcd_port = 2379
ShimData.etcd_host = "localhost"
ShimData.client = None
ShimData.proton_etcd_dir = '/proton'
ShimData.name = "SampleShim"
ShimData.api_handlers = dict()
ShimData.host_list = list()


def initialize_worker_thread(messages_queue):
    worker = Thread(target=process_queue, args=(messages_queue,))
    worker.setDaemon(True)
    worker.start()
    return worker


def process_queue(messages_queue):
    LOG.info("processing queue")
    while True:
        item = messages_queue.get()
        process_message(item)
        messages_queue.task_done()


def process_message(message):

    LOG.info("msg =  %s" % message)
    # LOG.info("msg.key =  %s" % message.key)
    # LOG.info("msg.value =  %s" % message.value)
    # LOG.info("msg.action =  %s" % message.action)

    # /proton/<api_name>/<object>/<key>
    path = message.key.split('/')
    if len(path) < 5:
        LOG.error("unknown message %s, ignoring" % message)
        return
    api_name = path[2]
    object = path[3]
    key = path[4]
    handler = ShimData.api_handlers.get(api_name, None)
    if handler is None:
        LOG.error('Unhandled API %s' % api_name)
        return
    action = message.action
    if action == 'set' or action == 'update':
        attributes = json.loads(message.value)
        handler.handle_object_change(object,
                                     key,
                                     attributes,
                                     ShimData)
    elif action == 'delete':
        handler.handle_object_delete(object,
                                     key,
                                     ShimData)
    else:
        LOG.error('unknown action %s' % action)


def setup_app():
    #
    # This should be config file driven to define the
    # APIs that are handled and the backend to handle each API
    #
    backend = DummyNetL3VPN()
    handler = ApiNetL3VPN(backend)
    ShimData.api_handlers[handler.name] = handler
    handler.load_model(ShimData)


def prepare_service(argv=()):
    cfg.CONF(argv[1:], project='shim')
    logging.setup(cfg.CONF, 'shim')


def main():
    SHIM_OPTS = [
        cfg.StrOpt('etcd_host',
                   default='127.0.0.1',
                   help='etcd host'),
        cfg.IntOpt('etcd_port',
                   default=2379,
                   help='etcd port'),
        cfg.StrOpt('host_list',
                   default='compute1, compute2, lubuntu-VirtualBox',
                   help='Comma separated list of hostnames managed by '
                        'this server'),
    ]
    opt_group = cfg.OptGroup(name='shim',
                             title='Options for the sample shim service')
    CONF.register_group(opt_group)
    CONF.register_opts(SHIM_OPTS, opt_group)
    logging.register_options(CONF)
    prepare_service(sys.argv)

    CONF.log_opt_values(LOG, logging.DEBUG)

    ShimData.etcd_host = CONF.shim.etcd_host
    ShimData.etcd_port = int(CONF.shim.etcd_port)
    host_list = CONF.shim.host_list.split(',')
    for host in host_list:
        ShimData.host_list.append(host.strip())

    LOG.info('Starting server in PID %s' % os.getpid())
    LOG.info("etcd_host: %s" % ShimData.etcd_host)
    LOG.info("etcd_port: %s" % ShimData.etcd_port)
    LOG.info('Host List: %s' % ShimData.host_list)

    ShimData.client = etcd.Client(host=ShimData.etcd_host,
                                  port=ShimData.etcd_port, read_timeout=3600)
    setup_app()
    messages_queue = Queue()
    initialize_worker_thread(messages_queue)
    wait_index = 0
    while True:

        try:
            LOG.info("watching %s" % ShimData.proton_etcd_dir)

            if wait_index:
                message = ShimData.client.read(ShimData.proton_etcd_dir,
                                               recursive=True, wait=True,
                                               waitIndex=wait_index)

            else:
                message = ShimData.client.read(ShimData.proton_etcd_dir,
                                               recursive=True, wait=True)

            messages_queue.put(message)

            if (message.modifiedIndex - wait_index) > 1000:
                wait_index = 0

            else:
                wait_index = message.modifiedIndex + 1

        except etcd.EtcdWatchTimedOut:
            LOG.info("timeout")
            pass

        except etcd.EtcdException:
            LOG.error("Cannot connect to etcd, make sure that etcd is running"
                      "...Trying in 5 seconds")
            time.sleep(5)

        except KeyboardInterrupt:
            LOG.info("exiting on interrupt")
            exit(1)

        except:
            pass

if __name__ == '__main__':
    main()
