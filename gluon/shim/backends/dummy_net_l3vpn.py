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

from oslo_log import log as logging

from gluon.shim.base import HandlerBase

LOG = logging.getLogger(__name__)


class DummyNetL3VPN(HandlerBase):
    def __init__(self):
        pass

    def bind_port(self, uuid, model, changes):
        """Called to bind port to VM.

        :param uuid: UUID of Port
        :param model: Model object
        :returns: dict of vif parameters (vif_type, vif_details)
        """
        LOG.info("bind_port: %s" % uuid)
        port = model.ports.get(uuid, None)
        if not port:
            LOG.error("Cannot find port")
            return dict()
        service_binding = model.vpnbindings.get(uuid, None)
        if not service_binding:
            LOG.error("Cannot bind port, not bound to a servcie")
            return dict()
        vpn_instance = model.vpn_instances.get(service_binding["service_id"],
                                               None)
        if not vpn_instance:
            LOG.error("VPN instance not available!")
            return dict()
        LOG.info("port: %s" % port)
        LOG.info("service: %s" % vpn_instance)
        rd_list = list()
        rd_string = vpn_instance.get("route_distinguishers")
        if rd_string:
            tmp_list = rd_string.split(',')
            for rd_name in tmp_list:
                rd_list.append(rd_name.strip())
        afconfig_list = list()
        afconfig_name_list = list()
        afconfig_string = vpn_instance.get("ipv4_family")
        if afconfig_string:
            tmp_list = afconfig_string.split(',')
            for afconfig_name in tmp_list:
                afconfig_name_list.append(afconfig_name.strip())

        for afconfig_name in afconfig_name_list:
            afconfig = model.vpn_afconfigs.get(afconfig_name, None)
            if afconfig:
                afconfig_list.append(afconfig)
                LOG.info("  afconfig(%s): %s" % (afconfig_name, afconfig))
        LOG.info(changes)
        retval = {'vif_type': 'ovs',
                  'vif_details': {'port_filter': False,
                                  'bridge_name': 'br-gluon'}}
        return retval

    def unbind_port(self, uuid, model, changes):
        """Called to unbind port from VM.

        :param uuid: UUID of Port
        :param model: Model object
        :returns: None
        """
        port = model.ports.get(uuid, None)
        if not port:
            LOG.error("Cannot find port")
            return
        LOG.info("unbind_port: %s" % uuid)
        LOG.info(changes)
        return

    def modify_port(self, uuid, model, changes):
        """Called when attributes change on a bound port.

        :param uuid: UUID of Port
        :param model: Model object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("modify_port: %s" % uuid)
        LOG.info(changes)
        pass

    def delete_port(self, uuid, model):
        """Called when a bound port is deleted

        :param uuid: UUID of Port
        :param model: Model object
        :returns: None
        """
        pass

    def modify_interface(self, uuid, model, changes):
        """Called when attributes on an interface

        :param uuid: UUID of Interface
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("modify_interface: %s" % uuid)
        LOG.info(changes)
        pass

    def delete_interface(self, uuid, model, changes):
        """Called when an interface is deleted

        :param uuid: UUID of Interface
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        pass

    def modify_service(self, uuid, model, changes):
        """Called when attributes change on a bound port's service

        :param uuid: UUID of Service
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("modify_service: %s" % uuid)
        LOG.info(changes)
        pass

    def delete_service(self, uuid, model, changes):
        """Called when a service associated with a bound port is deleted

        :param uuid: UUID of Service
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        pass

    def modify_service_binding(self, uuid, model, prev_binding):
        """Called when a service is associated with a bound port.

        :param uuid: UUID of Port
        :param model: Model Object
        :param prev_binding: dictionary of previous binding
        :returns: None
        """
        LOG.info("modify_service_binding: %s" % uuid)
        LOG.info(prev_binding)
        pass

    def delete_service_binding(self, model, prev_binding):
        """Called when a service is disassociated with a bound port.

        :param model: Model Object
        :param prev_binding: dictionary of previous binding
        :returns: None
        """
        pass

    def modify_subport_parent(self, uuid, model, prev_parent,
                              prev_parent_type):
        """Called when a subport's parent relationship changes.

        :param uuid: UUID of Subport
        :param model: Model object
        :param prev_parent: UUID of previous parent
        :param prev_parent_type: name of previous parent (Port or Subport)
        :returns: None
        """
        pass
