#    Copyright 2016, Ericsson AB
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

import webob.exc as exc
import etcd
import time
import json

from gluon.common import exception
from gluon.core.manager import ApiManager
from gluon.sync_etcd.thread import SyncData
from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)
logger = LOG


class MyData:
    pass

ManagerData = MyData()
ManagerData.etcd_port = 2379
ManagerData.etcd_host = '127.0.0.1'


class ProtonManager(ApiManager):
    def __init__(self):
        self.gluon_objects = {}
        host, port = cfg.CONF.api.host, cfg.CONF.api.port
        self.url = "http://%s:%d" % (host, port)
        self.service = cfg.CONF.api.service_name
        self.wait_index = 0
        self.etcd_client = etcd.Client(host=ManagerData.etcd_host,
                                       port=ManagerData.etcd_port,
                                       read_timeout=2)
        super(ProtonManager, self).__init__()

    def setup_bind_key(self, key):
        etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller", self.service,
                                                    "ProtonBasePort", key)
        #
        # If key does not exists, create it so we can wait on it to change.
        #
        try:
            message = self.etcd_client.read(etcd_key)
            self.wait_index = message.modifiedIndex + 1
        except etcd.EtcdKeyNotFound:
            self.wait_index = 0
            LOG.info("Key Not Found, creating it: %s" % etcd_key)
            data = dict()
            value = json.dumps(data)
            self.etcd_client.write(etcd_key, value)
        except:
            pass

    def wait_for_bind(self, key):
        etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller", self.service,
                                                    "ProtonBasePort", key)
        retry = 4
        ret_val = dict()
        while retry > 0:
            try:
                LOG.info("watching %s" % etcd_key)
                message = self.etcd_client.read(etcd_key, wait=True,
                                                waitIndex=self.wait_index)
                ret_val = json.loads(message.value)
                break
            except etcd.EtcdKeyNotFound:
                LOG.info("Key Not Found %s" % etcd_key)
                retry -= 1
                time.sleep(1)
            except etcd.EtcdWatchTimedOut:
                LOG.info("timeout")
                retry -= 1
            except etcd.EtcdException:
                LOG.error("Cannot connect to etcd, make sure it is running")
                retry = 0
            except Exception, e:
                LOG.error("Unknown error: %s" % str(e))
                retry -= 1
            except:
                retry -= 1
        return ret_val

    def get_all_vpnports(self, api_class, obj_class):
        return obj_class.as_list(obj_class.list())

    def get_one_vpnports(self, api_class, obj_class, key):
        try:
            obj = obj_class.get_by_primary_key(key)
        except Exception as e:
            raise exc.HTTPNotFound()
        return obj.as_dict()

    def create_vpnports(self, api_class, port):
        #
        # Validate that the BasePort and VPN objects exists
        #
        baseport_id = port.id
        vpn_id = port.vpn_instance
        baseport_class = self.get_gluon_object('ProtonBasePort')
        baseport = baseport_class.get_by_id(baseport_id)
        if not baseport:
            raise exception.NotFound(cls="ProtonBasePort", key=baseport_id)
        vpn_class = self.get_gluon_object('VpnInstance')
        vpn = vpn_class.get_by_id(vpn_id)
        if not vpn:
            raise exception.NotFound(cls="VpnInstance", key=vpn_id)
        port.create()
        return api_class.build(port)

    def update_vpnports(self, api_class, obj_class, key, new_values):
        return api_class.build(obj_class.update(key, new_values))

    def delete_vpnports(self, api_class, obj_class, key):
        return obj_class.delete(key)

    def get_all_baseports(self, api_class, obj_class):
        return obj_class.as_list(obj_class.list())

    def get_one_baseports(self, api_class, obj_class, key):
        try:
            obj = obj_class.get_by_primary_key(key)
        except Exception as e:
            raise exc.HTTPNotFound()
        return obj.as_dict()

    def create_baseports(self, api_class, port):
        port.create()
        #
        # Register port in Gluon
        #
        msg = {"port_id": port.id, "tenant_id": port.tenant_id,
               "service": self.service, "url": self.url,
               "operation": "register"}
        SyncData.sync_queue.put(msg)
        return api_class.build(port)

    def update_baseports(self, api_class, obj_class, key, new_values):
        has_bind_attrs = ("host_id" in new_values and
                          "device_id" in new_values)
        is_bind_request = (has_bind_attrs and new_values["host_id"] != "" and
                           new_values["device_id"] != "")
        if is_bind_request:
            self.setup_bind_key(key)
        ret_obj = api_class.build(obj_class.update(key, new_values))
        if is_bind_request:
            # bind
            vif_dict = self.wait_for_bind(key)
            if len(vif_dict) == 0:
                LOG.error("No binding information available")
            else:
                LOG.info(vif_dict)
                new_values = dict()
                if "vif_type" in vif_dict:
                    new_values["vif_type"] = vif_dict["vif_type"]
                if "vif_details" in vif_dict:
                    new_values["vif_details"] = \
                        json.dumps(vif_dict["vif_details"])
                if len(new_values) > 0:
                    ret_obj = api_class.build(obj_class.update(key,
                                                               new_values))
        elif has_bind_attrs:  # unbind request
            new_values["vif_type"] = ""
            new_values["vif_details"] = json.dumps({})
            ret_obj = api_class.build(obj_class.update(key, new_values))
        return ret_obj

    def delete_baseports(self, api_class, obj_class, key):
        #
        # Remove port from Gluon
        #
        msg = {"port_id": key, "operation": "deregister"}
        SyncData.sync_queue.put(msg)
        return obj_class.delete(key)

    def get_all_vpns(self, api_class, obj_class):
        return obj_class.as_list(obj_class.list())

    def get_one_vpns(self, api_class, obj_class, key):
        try:
            obj = obj_class.get_by_primary_key(key)
        except Exception as e:
            raise exc.HTTPNotFound()
        return obj.as_dict()

    def create_vpns(self, api_class, vpn):
        vpn.create()
        return api_class.build(vpn)

    def update_vpns(self, api_class, obj_class, key, new_values):
        return api_class.build(obj_class.update(key, new_values))

    def delete_vpns(self, api_class, obj_class, key):
        return obj_class.delete(key)

    def get_all_vpnafconfigs(self, api_class, obj_class):
        return obj_class.as_list(obj_class.list())

    def get_one_vpnafconfigs(self, api_class, obj_class, key):
        try:
            obj = obj_class.get_by_primary_key(key)
        except Exception as e:
            raise exc.HTTPNotFound()
        return obj.as_dict()

    def create_vpnafconfigs(self, api_class, vpnafconfig):
        vpnafconfig.create()
        return api_class.build(vpnafconfig)

    def update_vpnafconfigs(self, api_class, obj_class, key, new_values):
        return api_class.build(obj_class.update(key, new_values))

    def delete_vpnafconfigs(self, api_class, obj_class, key):
        return obj_class.delete(key)





