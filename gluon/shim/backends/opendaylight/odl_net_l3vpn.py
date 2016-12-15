# Copyright (c) 2016 Ericsson, Inc.
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

from gluon.shim.base import HandlerBase
from odlc import RestConfClient
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class OdlNetL3VPN(HandlerBase):
    def __init__(self):
        self.odlclient = RestConfClient()

    def bind_port(self, uuid, model, changes):
        """Called to bind port to VM.

        :param uuid: UUID of Port
        :param model: Model object
        :returns: dict of vif parameters (vif_type, vif_details)
        """
        LOG.info("bind_port: %s" % uuid)
        LOG.info(changes)

        port = model.ports.get(uuid, None)
        if not port:
            LOG.error("Cannot find port")
            return dict()

        # binding tap device on compute host by creating an IETF interface
        LOG.info("Updating IETF interface")
        parent_interface = 'tap%s' % uuid[:11]
        self.odlclient.update_ietf_interface(uuid, parent_interface)

        # check if a valid service binding exists already in the model
        # if so, create or update it on the SDN controller
        service_binding = model.vpn_ports.get(uuid, None)
        if not service_binding:
            LOG.info("Port not bound to a service yet.")
        else:
            vpn_instance = model.vpn_instances.get(
                service_binding["vpn_instance"],
                None)
            if not vpn_instance:
                LOG.warn("VPN instance not defined yet.")
            else:
                LOG.info("port: %s" % port)
                LOG.info("service: %s" % vpn_instance)

                LOG.info("Creating or updating VPN instance")
                self._create_or_update_service(vpn_instance)

                LOG.info("Creating or updating VPN Interface")
                adjacency = [{"ip_address": port.ipaddress,
                              "mac_address": port.mac_address}]
                self.odlclient.update_vpn_interface(port.id,
                                                    vpn_instance.id,
                                                    adjacency)
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
        LOG.info("unbind_port: %s" % uuid)
        LOG.info(changes)

        # we keep the service binding untouched for now
        LOG.info("Deleting IETF Interface")
        self.odlclient.delete_ietf_interface(uuid)

    def modify_port(self, uuid, model, changes):
        """Called when attributes change on a bound port.

        :param uuid: UUID of Port
        :param model: Model object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("modify_port: %s" % uuid)
        LOG.info(changes)

        LOG.info("Updating IETF interface")
        parent_interface = 'tap%s' % uuid[:11]
        self.odlclient.update_ietf_interface(uuid, parent_interface)

    def delete_port(self, uuid, model, port):
        """Called when a bound port is deleted

        :param uuid: UUID of Port
        :param model: Model object
        :returns: None
        """
        LOG.info("Deleting IETF Interface")
        self.odlclient.delete_ietf_interface(uuid)

    def modify_service(self, uuid, model, changes):
        """Called when attributes change on a bound port's service

        :param uuid: UUID of Service
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("modify_service: %s" % uuid)
        LOG.info(changes)

        LOG.info("Creating or updating VPN instance")
        vpn_instance = model.vpn_instances.get(uuid)
        if vpn_instance:
            self._create_or_update_service(vpn_instance)
        else:
            LOG.error("VPN instance %s not found" % uuid)

    def delete_service(self, uuid, model, changes):
        """Called when a service associated with a bound port is deleted

        :param uuid: UUID of Service
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("Deleting VPN Instance")
        self.odlclient.delete_l3_vpn_instance(uuid)

    def modify_service_binding(self, uuid, model, prev_binding):
        """Called when a service is associated with a bound port.

        :param uuid: UUID of Port
        :param model: Model Object
        :param prev_binding: dictionary of previous binding
        :returns: None
        """
        LOG.info("modify_service_binding: %s" % uuid)
        LOG.info(prev_binding)

        vpn_instance = model.vpn_ports[uuid].vpn_instance
        port = model.ports.get(uuid)
        adjacency = [{"ip_address": port.ipaddress,
                      "mac_address": port.mac_address}]

        LOG.info("Creating or updating VPN Interface")
        self.odlclient.update_vpn_interface(port.id, vpn_instance, adjacency)

    def delete_service_binding(self, model, prev_binding):
        """Called when a service is disassociated with a bound port.

        :param model: Model Object
        :param prev_binding: dictionary of previous binding
        :returns: None
        """
        LOG.info("Deleting VPN Interface")
        self.odlclient.delete_vpn_interface(prev_binding.id)

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

    def _create_or_update_service(self, vpn_instance):
        """Called when creating or updating a VPN instance

        :param vpn_instance: the VPN instance to create or update
        :return: None
        """
        ipv4_vpnTargets = {'vrfRTType': 'both',
                           'vrfRTValue': vpn_instance.get("ipv4_family")}
        self.odlclient.update_l3_vpn_instance(
            vpn_instance.id,
            vpn_instance.get("route_distinguishers"),
            ipv4_vpnTargets)
