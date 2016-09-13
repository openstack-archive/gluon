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
from gluon.sync_etcd.thread import SyncData
from gluon.common import exception
from gluon.core.manager import ApiManager
from oslo_log import log as logging
from oslo_config import cfg

# This has to be dne to get the Database Models
# build before the API is build.
# It should be done in a better way.

LOG = logging.getLogger(__name__)
logger = LOG



class ProtonManager(ApiManager):
    def __init__(self):
        self.gluon_objects = {}
        host, port = cfg.CONF.api.host, cfg.CONF.api.port
        self.url = "http://%s:%d" % (host, port)
        self.service = cfg.CONF.api.service_name
        super(ProtonManager, self).__init__()

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
        # Register port in gluon
        #
        msg = {"port_id": port.id, "tenant_id": port.tenant_id, "service": self.service, "url":self.url, "operation": "register"}
        SyncData.sync_queue.put(msg)
        return api_class.build(port)

    def update_baseports(self, api_class, obj_class, key, new_values):
        return api_class.build(obj_class.update(key, new_values))

    def delete_baseports(self, api_class, obj_class, key):
        #
        # Remove port from gluon
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





