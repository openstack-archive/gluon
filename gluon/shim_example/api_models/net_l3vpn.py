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

import etcd
from oslo_log import log as logging

from gluon.shim_example.base import ApiModelBase
from gluon.shim_example import model as Model

LOG = logging.getLogger(__name__)


class ApiNetL3VPN(ApiModelBase):

    def __init__(self, backend):
        super(self.__class__, self).__init__("net-l3vpn", backend)
        self.resync_mode = False
        self.model.vpn_instances = dict()
        self.model.vpn_ports = dict()
        self.model.vpn_afconfigs = dict()

    def load_model(self, shim_data):
        self.resync_mode = True
        objects = ["ProtonBasePort", "VpnInstance", "VpnAfConfig", "VPNPort"]
        for obj_name in objects:
            etcd_path = "{0:s}/{1:s}/{2:s}".format("proton", self.name,
                                                   obj_name)
            try:
                statuses = shim_data.client.read(etcd_path)
                if statuses:
                    for status in statuses.children:
                        attributes = json.loads(status.value)
                        self.handle_object_change(obj_name,
                                                  os.path.basename(status.key),
                                                  attributes, shim_data)
            except Exception as e:
                LOG.error("reading %s keys failed: %s" % (obj_name, str(e)))
                pass
        self.resync_mode = False

    def bind_attributes_changed(self, attributes):
        return ("host_id" in attributes and "device_id" in attributes)

    def is_bind_request(self, attributes):
        host_id = attributes.get("host_id", None)
        if host_id == "":
            host_id = None
        device_id = attributes.get("device_id", None)
        if device_id == "":
            device_id = None
        return (host_id is not None and device_id is not None)

    def get_etcd_bound_data(self, shim_data, key):
        etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller", self.name,
                                                    "ProtonBasePort", key)
        try:
            vif_dict = json.loads(shim_data.client.get(etcd_key).value)
            if not vif_dict:
                LOG.debug("Empty value read for: %s" % etcd_key)
                return {}
            else:
                return vif_dict
        except etcd.EtcdKeyNotFound:
            return {}
        return {}

    def update_etcd_unbound(self, shim_data, key):
        etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller", self.name,
                                                    "ProtonBasePort", key)
        try:
            data = {}
            shim_data.client.write(etcd_key, json.dumps(data))
        except Exception as e:
            LOG.error("Update etcd to unbound failed: %s" % str(e))

    def update_etcd_bound(self, shim_data, key, vif_dict):
        vif_dict["controller"] = shim_data.name
        etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller", self.name,
                                                    "ProtonBasePort", key)
        try:
            shim_data.client.write(etcd_key, json.dumps(vif_dict))
        except Exception as e:
            LOG.error("Update etcd to bound failed: %s" % str(e))

    def handle_port_change(self, key, attributes, shim_data):
        if key in self.model.ports:
            prev_port = self.model.ports[key]
            changes = self.model.ports[key].update_attrs(attributes)
            if self.bind_attributes_changed(changes.new):
                if self.model.ports[key]["__state"] == "Bound":
                    if self.is_bind_request(changes.new):  # already bound?
                        LOG.error("Bind request on bound port?")
                    else:  # Unbind
                        self.backend.unbind_port(key, self.model, changes)
                        vif_dict = self.get_etcd_bound_data(shim_data, key)
                        for vif_key in vif_dict:
                            self.model.ports[key][vif_key] = ""
                        self.update_etcd_unbound(shim_data, key)
                        self.model.ports[key]["__state"] = "Unbound"
                elif self.model.ports[key]["__state"] == "Unbound":
                    if self.is_bind_request(changes.new):
                        if changes.new["host_id"] in \
                                shim_data.host_list:  # On one of my hosts
                            vif_dict = self.backend.bind_port(key,
                                                              self.model,
                                                              changes)
                            if len(vif_dict) > 0:  # Bind success
                                self.model.ports[key].update_attrs(vif_dict)
                                self.model.ports[key]["__state"] = "Bound"
                                self.update_etcd_bound(shim_data, key,
                                                       vif_dict)
                            else:
                                LOG.info("Bind request rejected")
                        else:
                            self.model.ports[key]["__state"] = \
                                "InUse"  # Bound by another controller
                    else:
                        pass
                elif self.model.ports[key]["__state"] == "InUse":
                    if self.is_bind_request(changes.new):  # already bound?
                        LOG.error("Bind request on InUse port: %s" % key)
                    else:
                        self.model.ports[key]["__state"] = "Unbound"
            else:
                if self.model.ports[key]["__state"] == "Bound":
                    self.backend.modify_port(key, self.model, changes)
        else:
            port = Model.Port(key, attributes)
            self.model.ports[key] = port
            vif_dict = self.get_etcd_bound_data(shim_data, key)
            if len(vif_dict) > 0:  # Bound
                if vif_dict.get("controller") == \
                        shim_data.name:  # Bound by me
                    self.model.ports[key]["__state"] = "Bound"
                else:
                    self.model.ports[key]["__state"] = "InUse"

    def handle_vpn_instance_change(self, key, attributes, shim_data):
        if key in self.model.vpn_instances:
            port = None
            for vpn_port in self.model.vpn_ports.itervalues():
                if vpn_port["vpn_instance"] == key:
                    port = self.model.ports.get(vpn_port["id"])
            changes = self.model.vpn_instances[key].update_attrs(attributes)
            if port and port["__state"] == "Bound":
                self.backend.modify_service(key, self.model, changes)
        else:
            obj = Model.DataObj(key, attributes)
            self.model.vpn_instances[key] = obj

    def handle_vpn_port_change(self, key, attributes, shim_data):
        port = self.model.ports.get(key)
        if key in self.model.vpn_ports:
            prev_binding = \
                {"id": self.model.vpn_ports[key].id,
                 "vpn_instance": self.model.vpn_ports[key].vpn_instance}
            self.model.vpn_ports[key].update_attrs(attributes)
            if not self.resync_mode and port["__state"] == "Bound":
                self.backend.modify_service_binding(key, self.model,
                                                    prev_binding)
        else:
            obj = Model.DataObj(key, attributes)
            self.model.vpn_ports[key] = obj
            if not self.resync_mode and port["__state"] == "Bound":
                self.backend.modify_service_binding(key, self.model, {})

    def handle_vpnafconfig_change(self, key, attributes, shim_data):
        if key in self.model.vpn_afconfigs:
            self.model.vpn_afconfigs[key].update_attrs(attributes)
            for vpn_instance in self.model.vpn_instances.itervalues():
                changes = Model.ChangeData()
                if vpn_instance["ipv4_family"].find(key) != -1:
                    changes.new["ipv4_family"] = vpn_instance["ipv4_family"]
                if vpn_instance["ipv6_family"].find(key) != -1:
                    changes.new["ipv6_family"] = vpn_instance["ipv6_family"]
                if len(changes.new) > 0:
                    port = None
                    for vpn_port in self.model.vpn_ports.itervalues():
                        if vpn_port["vpn_instance"] == vpn_instance["id"]:
                            port = self.model.ports.get(vpn_port["id"])
                    if port and port["__state"] == "Bound":
                        self.backend.modify_service(vpn_instance["id"],
                                                    self.model, changes)
        else:
            obj = Model.DataObj(key, attributes)
            self.model.vpn_afconfigs[key] = obj

    def handle_object_change(self, object_type, key, attributes, shim_data):
        if object_type == "ProtonBasePort":
            self.handle_port_change(key, attributes, shim_data)
        elif object_type == "VpnInstance":
            self.handle_vpn_instance_change(key, attributes, shim_data)
        elif object_type == "VPNPort":
            self.handle_vpn_port_change(key, attributes, shim_data)
        elif object_type == "VpnAfConfig":
            self.handle_vpnafconfig_change(key, attributes, shim_data)
        else:
            LOG.error("Unknown object: %s" % object_type)

    def handle_port_delete(self, key, shim_data):
        if key in self.model.ports:
            deleted_obj = self.model.ports[key]
            del self.model.ports[key]
            self.backend.delete_port(key, self.model, deleted_obj)

    def handle_vpn_instance_delete(self, key, shim_data):
        if key in self.model.vpn_instances:
            deleted_obj = self.model.vpn_instances[key]
            port = None
            for vpn_port in self.model.vpn_ports.itervalues():
                if vpn_port["vpn_instance"] == key:
                    port = self.model.ports.get(vpn_port["id"])
            del self.model.vpn_instances[key]
            if port and port["__state"] == "Bound":
                self.backend.delete_service(key, self.model, deleted_obj)

    def handle_vpn_port_delete(self, key, shim_data):
        if key in self.model.vpn_ports:
            port = self.model.ports.get(key)
            deleted_obj = self.model.vpn_ports[key]
            del self.model.vpn_ports[key]
            if port and port["__state"] == "Bound":
                self.backend.delete_service_binding(self.model, deleted_obj)

    def handle_vpnafconfig_delete(self, key, shim_data):
        if key in self.model.vpn_afconfigs:
            del self.model.vpn_afconfigs[key]
            for vpn_instance in self.model.vpn_instances.itervalues():
                changes = Model.ChangeData()
                if vpn_instance["ipv4_family"].find(key) != -1:
                    l = vpn_instance["ipv4_family"].split(',')
                    l.remove(key)
                    changes.new["ipv4_family"] = ','.join(l)
                if vpn_instance["ipv6_family"].find(key) != -1:
                    l = vpn_instance["ipv6_family"].split(',')
                    l.remove(key)
                    changes.new["ipv6_family"] = ','.join(l)
                if len(changes.new) > 0:
                    port = None
                    for vpn_port in self.model.vpn_ports.itervalues():
                        if vpn_port["vpn_instance"] == vpn_instance["id"]:
                            port = self.model.ports.get(vpn_port["id"])
                    if port and port["__state"] == "Bound":
                        self.backend.modify_service(vpn_instance["id"],
                                                    self.model, changes)

    def handle_object_delete(self, object_type, key, shim_data):
        if object_type == "ProtonBasePort":
            self.handle_port_delete(key, shim_data)
        elif object_type == "VpnInstance":
            self.handle_vpn_instance_delete(key, shim_data)
        elif object_type == "VPNPort":
            self.handle_vpn_port_delete(key, shim_data)
        elif object_type == "VpnAfConfig":
            self.handle_vpnafconfig_delete(key, shim_data)
        else:
            LOG.error("Unknown object: %s" % object_type)
