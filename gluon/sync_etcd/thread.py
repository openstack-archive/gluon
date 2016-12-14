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
import six
from six.moves import queue
import threading

import etcd

from gluon.db import api as dbapi
from oslo_log._i18n import _LE
from oslo_log._i18n import _LI
from oslo_log._i18n import _LW
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class MyData(object):
    pass

SyncData = MyData()
SyncData.sync_thread_running = False
SyncData.sync_queue = queue.Queue()
SyncData.etcd_port = 2379
SyncData.etcd_host = '127.0.0.1'
SyncData.source = "proton"


class SyncThread(threading.Thread):
    """Worker thread that takes commands to update etcd with table changes."""

    def __init__(self, input_q):
        super(SyncThread, self).__init__()
        self.input_q = input_q
        self.db_instance = dbapi.get_instance()
        self.etcd_client = etcd.Client(host=SyncData.etcd_host,
                                       port=SyncData.etcd_port)
        LOG.info("SyncThread starting")

    def proc_sync_msg(self, msg):
        from gluon.particleGenerator import generator as particle_generator
        try:
            if msg["operation"] == "update":
                obj_key = "_".join(msg["key"].split())  # Get rid of spaces
                etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format(
                    SyncData.source, msg["service"], msg["table"], obj_key)
                db_gen = particle_generator.get_db_gen()
                table_class = db_gen.get_table_class(msg["service"],
                                                     msg["table"])
                data = self.db_instance.get_by_primary_key(
                    table_class, msg["key"])
                values = data.as_dict()
                d = {}
                for key in six.iterkeys(values):
                    if values[key] is None:
                        d[key] = values[key]
                    else:
                        d[key] = str(values[key])
                json_str = json.dumps(d)
                self.etcd_client.write(etcd_key, json_str)
            elif msg["operation"] == "delete":
                obj_key = "_".join(msg["key"].split())  # Get rid of spaces
                etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format(
                    SyncData.source, msg["service"], msg["table"], obj_key)
                self.etcd_client.delete(etcd_key)
            elif msg["operation"] == "register":
                obj_key = "_".join(msg["port_id"].split())  # Get rid of spaces
                port_key = "/gluon/port/{0:s}".format(obj_key)
                d = {"tenant_id": msg["tenant_id"],
                     "service": msg["service"],
                     "url": msg["url"]}
                json_str = json.dumps(d)
                self.etcd_client.write(port_key, json_str)
            elif msg["operation"] == "deregister":
                obj_key = "_".join(msg["port_id"].split())  # Get rid of spaces
                port_key = "/gluon/port/{0:s}".format(obj_key)
                self.etcd_client.delete(port_key)
            else:
                LOG.error(_LE("Unkown operation in msg %s") %
                          (msg["operation"]))
        except etcd.EtcdKeyNotFound:
            LOG.warn(_LW("Unknown key %s") % obj_key)
        except Exception as e:
            print(e.__doc__)
            print(e.args[0])
            LOG.error(
                _LE("Error writing to etcd {doc}, {msg}").format(
                    doc=e.__doc__, msg=e.args[0]))
            raise ValueError

    def run(self):
        while 1:
            try:
                msg = self.input_q.get(True, 10.0)
                LOG.info(_LI("SyncThread: received message %s ") % msg)
                self.proc_sync_msg(msg)
            except queue.Empty:
                LOG.debug("SyncThread: Queue timeout")
            except ValueError:
                LOG.error(_LE("Error processing sync message"))
                break
        LOG.error(_LE("SyncThread exiting"))
        SyncData.sync_thread_running = False


def start_sync_thread(**kwargs):
    """Start the SyncThread.  This should be called in the main function."""

    if not SyncData.sync_thread_running:
        for key, value in six.iteritems(kwargs):
            if key == "etcd_host":
                SyncData.etcd_host = value
            elif key == "etcd_port":
                SyncData.etcd_port = value
        SyncData.sync_thread = SyncThread(SyncData.sync_queue)
        SyncData.sync_thread.start()
        SyncData.sync_thread_running = True
