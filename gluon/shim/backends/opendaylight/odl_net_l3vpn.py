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
from gluon.shim import utils
from odlc import RestConfClient
from oslo_log import log as logging
import uuid as UUID

LOG = logging.getLogger(__name__)


class OdlNetL3VPN(HandlerBase):
    def __init__(self):
        self.odlclient = RestConfClient()
        self.l3vpn_network_id = None
        self.l3vpn_subnets = dict()
        self.l3vpn_ports = dict()

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

        retval = {'vif_type': 'ovs',
                  'vif_details': {'port_filter': False,
                                  'bridge_name': 'br-int'}}
        return retval

    def unbind_port(self, uuid, model, changes):
        """Called to unbind port from VM.

        :param uuid: UUID of Port
        :param model: Model object
        :returns: None
        """
        LOG.info("unbind_port: %s" % uuid)
        LOG.info(changes)

    def modify_port(self, uuid, model, changes):
        """Called when attributes change on a bound port.

        :param uuid: UUID of Port
        :param model: Model object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("modify_port: %s" % uuid)
        LOG.info(changes)

    def delete_port(self, uuid, model, port):
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

        LOG.info("Updating IETF interface")
        parent_interface = 'tap%s' % uuid[:11]
        self.odlclient.update_ietf_interface(uuid, parent_interface)

    def delete_interface(self, uuid, model, changes):
        """Called when an interface is deleted

        :param uuid: UUID of Interface
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        LOG.info("delete_interface: %s" % uuid)
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

        vpn_binding = model.vpnbindings[uuid]
        vpn_instance_id = vpn_binding.service_id
        vpn_instance = model.vpn_instances[vpn_instance_id]
        interface = model.interfaces.get(uuid)
        port = model.ports.get(uuid)

        subnet_name = self._create_l3vpn_port(
            model,
            port,
            interface,
            vpn_binding)

        adjacency = [{"ip_address": vpn_binding.ipaddress,
                      "mac_address": port.mac_address,
                      "primary-adjacency": "true",
                      "subnet_id": self.l3vpn_subnets[subnet_name]
                      }]

        LOG.info("Creating or updating VPN Interface")
        self.odlclient.update_vpn_interface(
            interface.id,
            vpn_instance,
            adjacency)

    def delete_service_binding(self, model, prev_binding):
        """Called when a service is disassociated with a bound port.

        :param model: Model Object
        :param prev_binding: dictionary of previous binding
        :returns: None
        """
        LOG.info("Deleting L3VPN port")
        self._delete_l3vpn_port(model, prev_binding)

        LOG.info("Deleting VPN Interface")
        self.odlclient.delete_vpn_interface(prev_binding.interface_id)

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

    def _create_l3vpn_port(self, model, port, interface, vpn_binding):
        # create network for port if needed
        self._create_l3vpn_network(model)

        # create subnet for port if needed
        subnet_name = self._create_l3vpn_subnet(
            model,
            port,
            interface,
            vpn_binding)

        # create a L3VPN port if needed
        if interface.id not in self.l3vpn_ports:
            p = self.odlclient.get_l3vpn_port(interface.id)
            if not p:
                # port does not exist yet -> create it
                self.odlclient.update_l3vpn_port(
                    self.l3vpn_network_id,
                    self.l3vpn_subnets[subnet_name],
                    port,
                    vpn_binding)

            # add to port cache
            self.l3vpn_ports[interface.id] = interface
        return subnet_name

    def _create_l3vpn_network(self, model):
        """create a L3VPN network if needed """
        if self.l3vpn_network_id is None:
            networks = self.odlclient.get_l3vpn_networks()
            for network in networks['networks']['network']:
                if network['name'] == 'GluonL3VPNNetwork':
                    LOG.info('Caching UUID %s of Gluon L3VPN network %s' %
                             (network['uuid'], network['name']))
                    self.l3vpn_network_id = network['uuid']

            # no existing L3VPN network found -> create one
            if self.l3vpn_network_id is None:
                id = UUID.uuid4()
                # TODO(egeokun): support multi-tenancy
                tenant_id = model.ports[model.ports.keys()[0]]['tenant_id']
                self.odlclient.update_l3vpn_network(id, UUID.UUID(tenant_id))
                self.l3vpn_network_id = id

    def _create_l3vpn_subnet(self, model, port, interface, vpn_binding):
        """create a L3VPN subnet if needed """
        ip_address = vpn_binding.ipaddress
        prefix = int(vpn_binding.subnet_prefix)

        network = utils.compute_network_addr(ip_address, prefix)
        subnet_name = "GluonL3VPNSubnet_" + network

        if subnet_name not in self.l3vpn_subnets:
            # try to refresh cache
            subnets = self.odlclient.get_l3vpn_subnets()
            for subnet in subnets['subnets']['subnet']:
                if subnet['name'] == subnet_name:
                    LOG.info('Caching Gluon L3VPN subnet %s (%s)' %
                             (subnet_name, subnet['uuid']))
                    self.l3vpn_subnets[subnet_name] = subnet['uuid']

            # no subnet exists yet -> create one
            if subnet_name not in self.l3vpn_subnets:
                id = UUID.uuid4()
                self.odlclient.update_l3vpn_subnet(
                    id,
                    self.l3vpn_network_id,
                    UUID.UUID(port.tenant_id),
                    network,
                    prefix)
                self.l3vpn_subnets[subnet_name] = id
        return subnet_name

    def _delete_l3vpn_port(self, model, vpn_binding):
        uuid = vpn_binding.interface_id

        # clean up L3VPN port
        if uuid not in self.l3vpn_ports:
            # check if port exists in ODL
            l3vpn_ports = self.odlclient.get_l3vpn_ports()
            for l3vpn_port in l3vpn_ports['ports']['port']:
                if l3vpn_port['uuid'] == uuid:
                    LOG.info('Found L3VPN port %s on ODL. Deleting.' % uuid)
                    self.odlclient.delete_l3vpn_port(uuid)
        else:
            del self.l3vpn_ports[uuid]
            LOG.info('Deleting L3VPN port %s.' % uuid)
            self.odlclient.delete_l3vpn_port(uuid)

        subnet = utils.compute_network_addr(
            vpn_binding.ipaddress,
            int(vpn_binding.subnet_prefix))

        # clean up L3VPN subnet
        found_another_port = False
        for k in model.vpnbindings:
            this_vpn_binding = model.vpnbindings[k]
            sn = utils.compute_network_addr(
                this_vpn_binding.ipaddress,
                this_vpn_binding.subnet_prefix)
            if subnet == sn:
                found_another_port = True
                LOG.info("Found another port on the subnet. Keeping subnet.")
                break

        if not found_another_port:
            subnet_name = "GluonL3VPNSubnet_" + subnet
            if subnet_name not in self.l3vpn_subnets:
                subnets = self.odlclient.get_l3vpn_subnets()
                for snet in subnets['subnets']['subnet']:
                    if snet.name == subnet_name:
                        LOG.info('Deleting Gluon L3VPN subnet %s (%s)' %
                                 (subnet_name, snet.uuid))
                        self.odlclient.delete_l3vpn_subnet(snet.uuid)
                        del self.l3vpn_subnets[snet.uuid]
                        break
            else:
                LOG.info('Found L3VPN subnet %s (%s) in cache. Deleting.' %
                         (subnet_name, self.l3vpn_subnets[subnet_name]))
                self.odlclient.delete_l3vpn_subnet(
                    self.l3vpn_subnets[subnet_name])
                del self.l3vpn_subnets[subnet_name]

        # clean up L3VPN network
        if not self.l3vpn_ports:
            if self.l3vpn_network_id is None:
                l3vpn_networks = self.odlclient.get_l3vpn_networks()
                for l3vpn_network in l3vpn_networks['networks']['network']:
                    if l3vpn_network['name'] == 'GluonL3VPNNetwork':
                        LOG.info("Deleting L3VPN network %s."
                                 % self.l3vpn_network_id)
                        self.odlclient.delete_l3vpn_network(
                            l3vpn_network['uuid'])
            else:
                LOG.info("L3VPN network %s found in cache. Deleting."
                         % self.l3vpn_network_id)
                self.odlclient.delete_l3vpn_network(self.l3vpn_network_id)
                self.l3vpn_network_id = None
        else:
            LOG.info('Still L3VPN ports present. '
                     'Not deleting L3VPN network: %s' % self.l3vpn_ports)
