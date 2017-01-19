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

import etcd
import json
import os
import sys
import time

from Queue import Queue
from threading import Thread

from oslo_config import cfg
from oslo_log import log as logging

from stevedore import extension

from gluon.shim.utils import pretty_print_message


class MyData(object):
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
    LOG.info("msg =  %s" % pretty_print_message(message))
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
    api_models = extension.ExtensionManager(
        namespace='gluon.shim.models',
        invoke_on_load=True
    )

    backends = extension.ExtensionManager(
        namespace='gluon.shim.backends',
        invoke_on_load=True
    )

    def init_model(model, backends):
        if model.obj.name in CONF.shim.handlers:
            backend_name = CONF.shim.handlers[model.obj.name]
            if backend_name in backends:
                backend = backends[backend_name]
                model.obj.init(backend.obj)
                LOG.info('Loaded handler "%s" with backend "%s"' %
                         (model.obj.name, backend_name))
                return model.obj
            else:
                LOG.error('Cannot load backend for handler "%s": '
                          'Selected backend "%s" not found.' %
                          (model.obj.name, backend_name))
        else:
            LOG.info('Handler "%s" not selected in config file. '
                     'Skipping initialization.' %
                     model.obj.name)

    handlers = api_models.map(init_model, backends)

    for handler in handlers:
        if handler is not None:
            ShimData.api_handlers[handler.name] = handler
            handler.load_model(ShimData)


def prepare_service(argv=()):
    cfg.CONF(argv[1:])
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
                   default='*',
                   help='Comma separated list of hostnames managed by '
                        'this server'),
        cfg.DictOpt('handlers',
                    default={'net-l3vpn': 'net-l3vpn-dummy'},
                    help='Dict for selecting the handlers '
                         'and their corresponding backend.')
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

        except Exception:
            pass

if __name__ == '__main__':
    main()
