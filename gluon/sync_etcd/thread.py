import six
import threading
from six.moves import queue
import json
from gluon.common.particleGenerator.generator import getDataBaseGeneratorInstance as getDBGen
from gluon.db import api as dbapi
from oslo_log import log as logging
from oslo_log._i18n import _LE
from oslo_log._i18n import _LW
from oslo_log._i18n import _LI


import etcd

LOG = logging.getLogger(__name__)


class MyData:
    pass

SyncData = MyData()
SyncData.sync_thread_running = False
SyncData.sync_queue = queue.Queue()
SyncData.etcd_port = 2379
SyncData.etcd_host = '127.0.0.1'
SyncData.source = "proton"
SyncData.service = "net-l3vpn"


class SyncThread(threading.Thread):
    """ A worker thread that takes takes commands to
        update etcd with table changes.
    """
    def __init__(self, input_q):
        super(SyncThread, self).__init__()
        self.input_q = input_q
        self.db_instance = dbapi.get_instance()
        self.etcd_client = etcd.Client(host=SyncData.etcd_host, port=SyncData.etcd_port)
        LOG.info("SyncThread starting")

    def proc_sync_msg(self, msg):
        try:
            if msg["operation"] == "update":
                obj_key = "_".join(msg["key"].split())  # Get rid of spaces
                etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format(SyncData.service, SyncData.source, msg["table"], obj_key)
                table_class = getDBGen().get_table_class(msg["table"])
                data = self.db_instance.get_by_primary_key(table_class, msg["key"])
                values = data.as_dict()
                d = {}
                for key in values.iterkeys():
                    d[key] = str(values[key])
                json_str = json.dumps(d)
                self.etcd_client.write(etcd_key, json_str)
            elif msg["operation"] == "delete":
                obj_key = "_".join(msg["key"].split())  # Get rid of spaces
                etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format(SyncData.service, SyncData.source, msg["table"], obj_key)
                self.etcd_client.delete(etcd_key)
            elif msg["operation"] == "register":
                obj_key = "_".join(msg["port_id"].split())  # Get rid of spaces
                port_key = "/gluon/port/{0:s}".format(obj_key)
                d = {"tenant_id":msg["tenant_id"], "service":msg["service"], "url":msg["url"]}
                json_str = json.dumps(d)
                self.etcd_client.write(port_key, json_str)
            elif msg["operation"] == "deregister":
                obj_key = "_".join(msg["port_id"].split()) # Get rid of spaces
                port_key = "/gluon/port/{0:s}".format(obj_key)
                self.etcd_client.delete(port_key)
            else:
                LOG.error(_LE("Unkown operation in msg %s") % (msg["operation"]))
        except etcd.EtcdKeyNotFound:
            LOG.warn(_LW("Unknown key %s") % obj_key)
        except Exception as e:
            print(e.__doc__)
            print(e.message)
            LOG.error(_LE("Error writing to etcd %s, %s") % (e.__doc__, e.message))
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
    """
    Start the SyncThread.  This should be called in the main function.
    """
    if SyncData.sync_thread_running == False:
        for key, value in kwargs.iteritems():
            if (key == "service_name"):
                SyncData.service = value
            elif (key == "etcd_host"):
                SyncData.etcd_host = value
            elif (key == "etcd_port"):
                SyncData.etcd_port = value
        SyncData.sync_thread = SyncThread(SyncData.sync_queue)
        SyncData.sync_thread.start()
        SyncData.sync_thread_running = True
