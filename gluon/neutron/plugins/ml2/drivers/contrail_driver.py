#    Copyright 2016, Juniper Networks, Inc.
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
from enum import Enum
import netaddr
import sys
import time
import traceback

from requests import requests
from vnc_api import vnc_api

from cfgm_common import exceptions as vnc_exc
from neutron.common.config import cfg
from neutron.common import constants as n_const
from neutron.extensions import portbindings
from neutron.plugins.ml2 import driver_api as api
from neutron_plugin_contrail.plugins.opencontrail.vnc_client import (
    sg_res_handler
)
from neutron_plugin_contrail.plugins.opencontrail.vnc_client import (
    sgrule_res_handler as sgrule_handler
)
from neutron_plugin_contrail.plugins.opencontrail.vnc_client import (
    subnet_res_handler
)
from neutron_plugin_contrail.plugins.opencontrail.vnc_client import (
    vmi_res_handler
)
from neutron_plugin_contrail.plugins.opencontrail.vnc_client import (
    vn_res_handler
)
from oslo_log import log

vnc_extra_opts = [
    cfg.BoolOpt('apply_subnet_host_routes', default=False),
    cfg.BoolOpt('multi_tenancy', default=False)
]

logger = log.getLogger(__name__)


def dump(obj):
    """Helper for logging objects."""
    objstr = ""
    for attr in dir(obj):
        objstr += ("@.%s = %s; " % (attr, getattr(obj, attr)))
    return objstr


def clear_null_keys(dic):
    """Remove all keys with None value from dict."""
    for key in dic.keys():
        if dic[key] is None:
            del dic[key]


def get_dict_diff(base, update):
    """Return only dict with keys that differs from base."""
    diff = dict(update)
    for key in base.keys():
        if diff.get(key) == base[key]:
            del diff[key]
    return diff


class Hndl(Enum):
    """Enum for Contrail object handlers."""

    VirtualNetwork = 1
    Subnet = 2
    VMInterface = 3
    SecurityGroup = 4
    SGRule = 5


class ContrailMechanismDriver(api.MechanismDriver):

    def initialize(self):
        logger.info("Initializing ConGl (Contrail Gluon) mechanism driver ...")

        cfg.CONF.register_opts(vnc_extra_opts, 'APISERVER')
        admin_user = cfg.CONF.keystone_authtoken.admin_user
        admin_password = cfg.CONF.keystone_authtoken.admin_password
        admin_tenant_name = cfg.CONF.keystone_authtoken.admin_tenant_name
        # api_srvr_ip = cfg.CONF.APISERVER.api_server_ip
        # api_srvr_port = cfg.CONF.APISERVER.api_server_port
        # Does IP address and Port number should be taken from neutron (?)
        api_srvr_ip = "127.0.0.1"
        api_srvr_port = 8082
        try:
            auth_host = cfg.CONF.keystone_authtoken.auth_host
        except cfg.NoSuchOptError:
            auth_host = "127.0.0.1"

        try:
            auth_protocol = cfg.CONF.keystone_authtoken.auth_protocol
        except cfg.NoSuchOptError:
            auth_protocol = "http"

        try:
            auth_port = cfg.CONF.keystone_authtoken.auth_port
        except cfg.NoSuchOptError:
            auth_port = "35357"

        try:
            auth_url = cfg.CONF.keystone_authtoken.auth_url
        except cfg.NoSuchOptError:
            auth_url = "/v2.0/tokens"

        try:
            auth_type = cfg.CONF.auth_strategy
        except cfg.NoSuchOptError:
            auth_type = "keystone"

        try:
            api_server_url = cfg.CONF.APISERVER.api_server_url
        except cfg.NoSuchOptError:
            api_server_url = "/"

        connected = False
        while not connected:
            try:
                self._vnc_lib = vnc_api.VncApi(
                    admin_user,
                    admin_password,
                    admin_tenant_name,
                    api_srvr_ip,
                    api_srvr_port,
                    api_server_url,
                    auth_host=auth_host,
                    auth_port=auth_port,
                    auth_protocol=auth_protocol,
                    auth_url=auth_url,
                    auth_type=auth_type)
                connected = True
            except requests.exceptions.RequestException:
                time.sleep(3)
        logger.info("Contrail connection is %s" % (dump(self._vnc_lib)))

        self.handlers = {
            Hndl.VirtualNetwork: vn_res_handler.VNetworkHandler(self._vnc_lib),
            Hndl.Subnet: subnet_res_handler.SubnetHandler(self._vnc_lib),
            Hndl.VMInterface:
            vmi_res_handler.VMInterfaceHandler(self._vnc_lib),
            Hndl.SecurityGroup:
            sg_res_handler.SecurityGroupHandler(self._vnc_lib),
            Hndl.SGRule: sgrule_handler.SecurityGroupRuleHandler(self._vnc_lib)
        }

    def create_network_precommit(self, context):
        """Allocate resources for a new network.

        :param context: NetworkContext instance describing the new
        network.

        Create a new network, allocating resources as necessary in the
        database. Called inside transaction context on session. Call
        cannot block.  Raising an exception will result in a rollback
        of the current transaction.
        """
        vnh = self.handlers[Hndl.VirtualNetwork]
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        vn_obj = vnh.neutron_dict_to_vn(vnh.create_vn_obj(context.current),
                                        context.current)
        # Force contrail to use same uuid as neutron (easier update/delete)
        vn_obj.uuid = context.current['id']
        net = self._vnc_lib.virtual_network_create(vn_obj)
        if vn_obj.router_external:
            fip_pool_obj = vnc_api.FloatingIpPool('floating-ip-pool', vn_obj)
            self._vnc_lib.floating_ip_pool_create(fip_pool_obj)
        logger.info("New network returned by contrail: %s" % dump(net))
        logger.info("Net object (%s) ((current is: %s)) is: %s" %
                    (type(vn_obj), type(context.current), dump(vn_obj)))

    def create_network_postcommit(self, context):
        """Create a network.

        :param context: NetworkContext instance describing the new
        network.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        pass

    def update_network_precommit(self, context):
        """Update resources of a network.

        :param context: NetworkContext instance describing the new
        state of the network, as well as the original state prior
        to the update_network call.

        Update values of a network, updating the associated resources
        in the database. Called inside transaction context on session.
        Raising an exception will result in rollback of the
        transaction.

        update_network_precommit is called for all changes to the
        network state. It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))

        vnh = self.handlers[Hndl.VirtualNetwork]
        vn_obj = vnh.neutron_dict_to_vn(
            vnh._get_vn_obj_from_net_q(context.current), context.current)
        vnh._resource_update(vn_obj)

    def update_network_postcommit(self, context):
        """Update a network.

        :param context: NetworkContext instance describing the new
        state of the network, as well as the original state prior
        to the update_network call.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.

        update_network_postcommit is called for all changes to the
        network state.  It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        pass

    def delete_network_precommit(self, context):
        """Delete resources for a network.

        :param context: NetworkContext instance describing the current
        state of the network, prior to the call to delete it.

        Delete network resources previously allocated by this
        mechanism driver for a network. Called inside transaction
        context on session. Runtime errors are not expected, but
        raising an exception will result in rollback of the
        transaction.

        This code is literally resource_delete method from
        VNetworkDeleteHandler class of contrail neutron plugin
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        vnh = self.handlers[Hndl.VirtualNetwork]
        net_id = context.current['id']
        try:
            vn_obj = vn_res_handler.VNetworkGetHandler._resource_get(vnh,
                                                                     id=net_id)
        except vnc_api.NoIdError:
            return

        try:
            fip_pools = vn_obj.get_floating_ip_pools()
            for fip_pool in fip_pools or []:
                vnh._vnc_lib.floating_ip_pool_delete(id=fip_pool['uuid'])
            vn_res_handler.VNetworkDeleteHandler._resource_delete(vnh,
                                                                  id=net_id)
        except vnc_api.RefsExistError:
            vnh._raise_contrail_exception('NetworkInUse',
                                          net_id=net_id, resource='network')

    def delete_network_postcommit(self, context):
        """Delete a network.

        :param context: NetworkContext instance describing the current
        state of the network, prior to the call to delete it.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        pass

    def subnet_resource_create(self, subnet_q):
        """Modified copy of SubnetCreateHandler.resource_create method.

        This modified version preserves subnet_uuid given from neutron
        """
        net_id = subnet_q['network_id']
        vn_obj = self.handlers[Hndl.Subnet]._resource_get(id=net_id)
        ipam_fq_name = subnet_q.get('contrail:ipam_fq_name')
        netipam_obj = self.handlers[Hndl.Subnet]._get_netipam_obj(ipam_fq_name,
                                                                  vn_obj)
        if not ipam_fq_name:
            ipam_fq_name = netipam_obj.get_fq_name()

        subnet_vnc = (
            subnet_res_handler.SubnetCreateHandler
            ._subnet_neutron_to_vnc(subnet_q)
        )
        logger.info("Changing subnet id from %s ==to==> %s" %
                    (subnet_vnc.subnet_uuid, subnet_q['id']))
        subnet_vnc.subnet_uuid = subnet_q['id']
        subnet_key = (
            subnet_res_handler.SubnetCreateHandler
            ._subnet_vnc_get_key(subnet_vnc, net_id)
        )

        # Locate list of subnets to which this subnet has to be appended
        net_ipam_ref = None
        ipam_refs = vn_obj.get_network_ipam_refs()
        for ipam_ref in ipam_refs or []:
            if ipam_ref['to'] == ipam_fq_name:
                net_ipam_ref = ipam_ref
                break

        if not net_ipam_ref:
            # First link from net to this ipam
            vnsn_data = vnc_api.VnSubnetsType([subnet_vnc])
            vn_obj.add_network_ipam(netipam_obj, vnsn_data)
        else:  # virtual-network already linked to this ipam
            for subnet in net_ipam_ref['attr'].get_ipam_subnets():
                if self.handlers[Hndl.Subnet].subnet_cidr_overlaps(subnet_vnc,
                                                                   subnet):
                    existing_sn_id = (
                        self.handlers[Hndl.Subnet]
                        ._subnet_vnc_read_mapping(
                            key=self.handlers[Hndl.Subnet]
                            ._subnet_vnc_get_key(subnet, net_id))
                    )
                    # duplicate !!
                    msg = (
                        ("Cidr %s overlaps with another subnet of subnet %s")
                        % (subnet_q['cidr'], existing_sn_id)
                    )
                    self._raise_contrail_exception('BadRequest',
                                                   resource='subnet', msg=msg)
            vnsn_data = net_ipam_ref['attr']
            vnsn_data.ipam_subnets.append(subnet_vnc)
            # TODO(): Add 'ref_update' API that will set this field
            vn_obj._pending_field_updates.add('network_ipam_refs')
        self.handlers[Hndl.Subnet]._resource_update(vn_obj)

        # Read in subnet from server to get updated values for gw etc.
        subnet_vnc = self.handlers[Hndl.Subnet]._subnet_read(subnet_key)
        subnet_info = self.handlers[Hndl.Subnet]._subnet_vnc_to_neutron(
            subnet_vnc, vn_obj, ipam_fq_name)
        return subnet_info

    def create_subnet_precommit(self, context):
        """Allocate resources for a new subnet.

        :param context: SubnetContext instance describing the new
        subnet.

        Create a new subnet, allocating resources as necessary in the
        database. Called inside transaction context on session. Call
        cannot block.  Raising an exception will result in a rollback
        of the current transaction.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        data = context.current
        # This is required because Contrail does not check if value for given
        # key is None, it checks only if key exists (eg. ipv6_address_mode key
        # exists when creating subnet)
        clear_null_keys(data)
        self.subnet_resource_create(data)

    def create_subnet_postcommit(self, context):
        """Create a subnet.

        :param context: SubnetContext instance describing the new
        subnet.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        pass

    def update_subnet_precommit(self, context):
        """Update resources of a subnet.

        :param context: SubnetContext instance describing the new
        state of the subnet, as well as the original state prior
        to the update_subnet call.

        Update values of a subnet, updating the associated resources
        in the database. Called inside transaction context on session.
        Raising an exception will result in rollback of the
        transaction.

        update_subnet_precommit is called for all changes to the
        subnet state. It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        self.handlers[Hndl.Subnet].resource_update(
            None, context.current['id'],
            get_dict_diff(context.original, context.current))
        pass

    def update_subnet_postcommit(self, context):
        """Update a subnet.

        :param context: SubnetContext instance describing the new
        state of the subnet, as well as the original state prior
        to the update_subnet call.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.

        update_subnet_postcommit is called for all changes to the
        subnet state.  It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        pass

    def delete_subnet_precommit(self, context):
        """Delete resources for a subnet.

        :param context: SubnetContext instance describing the current
        state of the subnet, prior to the call to delete it.

        Delete subnet resources previously allocated by this
        mechanism driver for a subnet. Called inside transaction
        context on session. Runtime errors are not expected, but
        raising an exception will result in rollback of the
        transaction.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))

        self.handlers[Hndl.Subnet].resource_delete(None, context.current['id'])

    def delete_subnet_postcommit(self, context):
        """Delete a subnet.

        :param context: SubnetContext instance describing the current
        state of the subnet, prior to the call to delete it.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        logger.info("Function '%s' context is: %s" %
                    (sys._getframe().f_code.co_name, dump(context)))
        pass

    def security_group_resource_create(self, context, sg_q):
        self.handlers[Hndl.SecurityGroup]._kwargs.get(
            'contrail_extensions_enabled', False)

        uuid = sg_q['id']
        sg_obj = None
        try:
            logger.info("SecGr get for uuid %s" % (uuid))
            sg_obj = self.handlers[Hndl.SecurityGroup].resource_get(None, uuid)
            logger.info("SecGr get: %s" % (dump(sg_obj)))
        except Exception as e:
            logger.info("Exception %s" % (dump(e)))
            pass

        if sg_obj is None:
            sg_obj = (
                self.handlers[Hndl.SecurityGroup]
                ._security_group_neutron_to_vnc(
                    sg_q,
                    self.handlers[Hndl.SecurityGroup]._create_security_group(
                        sg_q))
            )
            sg_obj.uuid = uuid
            sg_uuid = self.handlers[Hndl.SecurityGroup]._resource_create(
                sg_obj)
            if sg_uuid != uuid:
                raise ReferenceError(
                    "SG _resource create returned object withd different uuid:"
                    " %s (expected was %s" % (sg_uuid, uuid))
        else:
            sg_uuid = uuid

        # allow all egress traffic
        def_rule = {}
        def_rule['port_range_min'] = 0
        def_rule['port_range_max'] = 65535
        def_rule['direction'] = 'egress'
        def_rule['remote_ip_prefix'] = '0.0.0.0/0'
        def_rule['remote_group_id'] = None
        def_rule['protocol'] = 'any'
        def_rule['ethertype'] = 'IPv4'
        def_rule['security_group_id'] = sg_uuid
        def_rule['tenant_id'] = sg_q['tenant_id']
        self.handlers[Hndl.SGRule].resource_create(context, def_rule)

        # allow all ingress traffic
        def_rule = {}
        def_rule['port_range_min'] = 0
        def_rule['port_range_max'] = 65535
        def_rule['direction'] = 'ingress'
        def_rule['remote_ip_prefix'] = '0.0.0.0/0'
        def_rule['remote_group_id'] = None
        def_rule['protocol'] = 'any'
        def_rule['ethertype'] = 'IPv4'
        def_rule['security_group_id'] = sg_uuid
        def_rule['tenant_id'] = sg_q['tenant_id']
        self.handlers[Hndl.SGRule].resource_create(context, def_rule)

    def create_dummy_security_group(self, sg_id, port_q):
        sg_q = {'id': sg_id, 'tenant_id': port_q['tenant_id'],
                'name': ('dummy' + sg_id)}
        self.security_group_resource_create(None, sg_q)

    def clean_port_dict(self, port_q):
        keys = ['binding:profile', 'binding:vif_details']
        for key in keys:
            if key in port_q:
                if not port_q[key]:
                    del port_q[key]
        return port_q

    def port_resource_create(self, port_q):
        port_q = self.clean_port_dict(port_q)
        if 'network_id' not in port_q or 'tenant_id' not in port_q:
            raise self._raise_contrail_exception(
                'BadRequest', resource='port',
                msg="'tenant_id' and 'network_id' are mandatory")

        net_id = port_q['network_id']
        try:
            vn_obj = self.handlers[Hndl.VirtualNetwork].get_vn_obj(id=net_id)
        except vnc_exc.NoIdError:
            self._raise_contrail_exception('NetworkNotFound', net_id=net_id,
                                           resource='port')

        vmih = self.handlers[Hndl.VMInterface]

        # DIRTY TEMPORARY HACKS - XXX
        # DIRTY TEMPORARY HACKS - XXX
        neutron_context = {'is_admin': False, 'tenant': port_q['tenant_id']}
        # DIRTY TEMPORARY HACKS - XXX
        # DIRTY TEMPORARY HACKS - XXX
        tenant_id = vmih._get_tenant_id_for_create(neutron_context, port_q)
        proj_id = vmih._project_id_neutron_to_vnc(tenant_id)

        # if mac-address is specified, check against the exisitng ports
        # to see if there exists a port with the same mac-address
        if 'mac_address' in port_q:
            vmih._validate_mac_address(proj_id, net_id, port_q['mac_address'])

        # Check and possibly create a dummy security group
        sec_group_list = []
        if 'security_groups' in port_q:
            sec_group_list = port_q.get('security_groups')
        logger.info("All needed SG %s" % sec_group_list)
        for sg_id in sec_group_list or []:
            logger.info("Checking SG: %s" % (sg_id))
            try:
                self.handlers[Hndl.SecurityGroup].resource_get(None, sg_id)
                logger.info("SG: %s checked" % (sg_id))
            except Exception as e:
                logger.info("Exception caught during SG (%s) read: %s" %
                            (sg_id, e))
                self.create_dummy_security_group(sg_id, port_q)

        logger.info("All SG: OK")

        # initialize port object
        vmi_obj = vmih._create_vmi_obj(port_q, vn_obj)
        vmi_obj = vmih._neutron_port_to_vmi(port_q, vmi_obj=vmi_obj)
        vmi_obj.uuid = port_q['id']

        # determine creation of v4 and v6 ip object
        ip_obj_v4_create = False
        ip_obj_v6_create = False
        fixed_ips = []
        ipam_refs = vn_obj.get_network_ipam_refs() or []
        for ipam_ref in ipam_refs:
            subnet_vncs = ipam_ref['attr'].get_ipam_subnets()
            for subnet_vnc in subnet_vncs:
                cidr = '%s/%s' % (subnet_vnc.subnet.get_ip_prefix(),
                                  subnet_vnc.subnet.get_ip_prefix_len())
                if not ip_obj_v4_create and (
                        netaddr.IPNetwork(cidr).version == 4):
                    ip_obj_v4_create = True
                    fixed_ips.append(
                        {'subnet_id': subnet_vnc.subnet_uuid,
                         'ip_family': 'v4'})
                if not ip_obj_v6_create and (
                        netaddr.IPNetwork(cidr).version == 6):
                    ip_obj_v6_create = True
                    fixed_ips.append({'subnet_id': subnet_vnc.subnet_uuid,
                                      'ip_family': 'v6'})

        # create the object
        port_id = self.handlers[Hndl.VMInterface]._resource_create(vmi_obj)
        try:
            if 'fixed_ips' in port_q:
                self.handlers[Hndl.VMInterface]._create_instance_ips(
                    vn_obj, vmi_obj, port_q['fixed_ips'])
            elif vn_obj.get_network_ipam_refs():
                self.handlers[Hndl.VMInterface]._create_instance_ips(
                    vn_obj, vmi_obj, fixed_ips)
        except Exception as e:
            logger.error(
                "Got exception from contrail: %s  ---> %s" %
                (e, traceback.format_exception(*sys.exc_info())))
            # failure in creating the instance ip. Roll back
            self.handlers[Hndl.VMInterface]._resource_delete(id=port_id)
            raise e

        # TODO() below reads back default parent name, fix it
        vmi_obj = self.handlers[Hndl.VMInterface]._resource_get(
            id=port_id, fields=['instance_ip_back_refs'])
        self.handlers[Hndl.VMInterface]._vmi_to_neutron_port(vmi_obj)

    def create_port_precommit(self, context):
        """Allocate resources for a new port.

        :param context: PortContext instance describing the port.

        Create a new port, allocating resources as necessary in the
        database. Called inside transaction context on session. Call
        cannot block.  Raising an exception will result in a rollback
        of the current transaction.
        """
        logger.info(
            "Function '%s' context is: %s" %
            (sys._getframe().f_code.co_name, dump(context)))
        self.port_resource_create(context.current)
        pass

    def create_port_postcommit(self, context):
        """Create a port.

        :param context: PortContext instance describing the port.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Raising an exception will
        result in the deletion of the resource.
        """
        logger.info(
            "Function '%s' context is: %s" %
            (sys._getframe().f_code.co_name, dump(context)))
        pass

    def update_port_precommit(self, context):
        """Update resources of a port.

        :param context: PortContext instance describing the new
        state of the port, as well as the original state prior
        to the update_port call.

        Called inside transaction context on session to complete a
        port update as defined by this mechanism driver. Raising an
        exception will result in rollback of the transaction.

        update_port_precommit is called for all changes to the port
        state. It is up to the mechanism driver to ignore state or
        state changes that it does not know or care about.
        """
        logger.info(
            "Function '%s' context is: %s" %
            (sys._getframe().f_code.co_name, dump(context)))
        vmih = self.handlers[Hndl.VMInterface]
        vmih.resource_update(
            None,
            context.current['id'],
            get_dict_diff(context.original,
                          context.current))
        pass

    def update_port_postcommit(self, context):
        """Update a port.

        :param context: PortContext instance describing the new
        state of the port, as well as the original state prior
        to the update_port call.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Raising an exception will
        result in the deletion of the resource.

        update_port_postcommit is called for all changes to the port
        state. It is up to the mechanism driver to ignore state or
        state changes that it does not know or care about.
        """
        logger.info(
            "Function '%s' context is: %s" %
            (sys._getframe().f_code.co_name, dump(context)))
        pass

    def delete_port_precommit(self, context):
        """Delete resources of a port.

        :param context: PortContext instance describing the current
        state of the port, prior to the call to delete it.

        Called inside transaction context on session. Runtime errors
        are not expected, but raising an exception will result in
        rollback of the transaction.
        """
        logger.info(
            "Function '%s' context is: %s" %
            (sys._getframe().f_code.co_name, dump(context)))
        self.handlers[Hndl.VMInterface].resource_delete(
            None, context.current['id'])
        pass

    def delete_port_postcommit(self, context):
        """Delete a port.

        :param context: PortContext instance describing the current
        state of the port, prior to the call to delete it.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        logger.info(
            "Function '%s' context is: %s" %
            (sys._getframe().f_code.co_name, dump(context)))
        pass

    def bind_port(self, context):
        """Attempt to bind a port.

        :param context: PortContext instance describing the port

        Called inside transaction context on session, prior to
        create_port_precommit or update_port_precommit, to
        attempt to establish a port binding. If the driver is able to
        bind the port, it calls context.set_binding with the binding
        details.
        """
        logger.info(
            "Function '%s' context [%s] is: %s" %
            (sys._getframe().f_code.co_name, context.__class__.__name__,
             dump(context)))
        logger.info("Network is: %s" % (dump(context.network)))
        port_id = context.current['id']
        vmih = self.handlers[Hndl.VMInterface]
        vmi_obj = vmih._resource_get(id=port_id)
        vmih._set_vm_instance_for_vmi(vmi_obj, context.current['device_id'])

        vif_details = {portbindings.CAP_PORT_FILTER: True}

        for segment in context.segments_to_bind:
            context.set_binding(
                segment['id'],
                'vrouter',
                vif_details,
                n_const.PORT_STATUS_ACTIVE)
        pass
