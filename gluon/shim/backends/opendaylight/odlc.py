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

from gluon.shim import utils
import json
from oslo_config import cfg
import requests
try:
    from neutron.openstack.common import jsonutils
except ImportError:
    from oslo_serialization import jsonutils
from log import for_all_methods
from log import LOG
from log import log_enter_exit

ODL_SHIM_OPTS = [
    cfg.StrOpt('odl_host',
               default='127.0.0.1',
               help='IP or hostname of OpenDaylight'),
    cfg.IntOpt('odl_port',
               default=8181,
               help='Port of ODL REST API'),
    cfg.StrOpt('odl_user',
               default='admin',
               help='Username for accessing the REST API'),
    cfg.StrOpt('odl_passwd',
               default='admin',
               help='Password for accessing the REST API'),
]
opt_group = cfg.OptGroup(name='shim_odl',
                         title='Options for the ODL shim service')
CONF = cfg.CONF
CONF.register_group(opt_group)
CONF.register_opts(ODL_SHIM_OPTS, opt_group)


@for_all_methods(log_enter_exit)
class ODL_Client(object):

    def __init__(self, backend='neutron'):

        odl_ip = CONF.shim_odl.odl_host
        odl_port = CONF.shim_odl.odl_port
        user = CONF.shim_odl.odl_user
        passwd = CONF.shim_odl.odl_passwd

        LOG.info("odl_host: %s" % odl_ip)
        LOG.info("odl_port: %s" % odl_port)
        LOG.info('odl_user: %s' % user)
        LOG.info('odl_passwd: %s' % passwd)

        if backend == 'neutron':
            self.url = ("http://%(ip)s:%(port)s/controller/nb/v2/neutron" %
                        {'ip': odl_ip,
                         'port': odl_port})
        if backend == 'restconf':
            self.url = ("http://%(ip)s:%(port)s/restconf/config" %
                        {'ip': odl_ip,
                         'port': odl_port})
        self.auth = (user, passwd)
        self.timeout = 10

    def get(self, obj_typ):
        return self.sendjson('get', obj_typ).get(obj_typ)

    def cleanup_type(self, obj_typ):
        for obj in self.get(obj_typ):
            self.delete(obj_typ, id=obj['id'])

    def cleanup(self):
        self.cleanup_type('ports')
        self.cleanup_type('subnets')
        self.cleanup_type('networks')

    def delete(self, obj_typ, id=None, obj=None):
        if not (id or obj):
            LOG.error('Give either net_id or net_obj')
        if obj:
            id = obj.get('id')
        return self.sendjson('delete', '%(obj_typ)s/%(id)s' %
                             {'obj_typ': obj_typ,
                              'id': id})

    def delete_all(self, obj_typ, key, value):
        objs = self.get(obj_typ)
        for obj in objs:
            if obj.get(key) and value in obj.get(key):
                self.delete(obj_typ, obj=obj)

    def sendjson(self, method, urlpath, obj=None):
        """Send json to the OpenDaylight controller."""
        headers = {'Content-Type': 'application/json'}
        data = jsonutils.dumps(obj, indent=2) if obj else None
        url = '/'.join([self.url, urlpath])
        LOG.debug("Sending METHOD (%(method)s) URL (%(url)s) JSON (%(obj)s)" %
                  {'method': method, 'url': url, 'obj': obj})
        r = requests.request(method, url=url,
                             headers=headers, data=data,
                             auth=self.auth, timeout=self.timeout)
        try:
            r.raise_for_status()
        except Exception as ex:
            LOG.error("Error Sending METHOD (%(method)s) URL (%(url)s)"
                      "JSON (%(obj)s) return: %(r)s ex: %(ex)s rtext: "
                      "%(rtext)s" %
                      {'method': method, 'url': url, 'obj': obj, 'r': r,
                       'ex': ex, 'rtext': r.text})
            return r
        try:
            return json.loads(r.content)
        except Exception:
            LOG.debug("%s" % r)
            return


@for_all_methods(log_enter_exit)
class RestConfClient(ODL_Client):

    def __init__(self):
        super(RestConfClient, self).__init__(backend='restconf')

    def get(self, urlpath):
        output = self.sendjson('get', urlpath)
        return output

    def get_l3vpn_networks(self):
        return self.get('neutron:neutron/networks')

    def update_l3vpn_network(self, id, tenant_id):
        network = \
            {
                'uuid': id,
                'name': 'GluonL3VPNNetwork',
                'neutron-L3-ext:external': 'false',
                'neutron-provider-ext:segmentation-id': '42',
                'neutron-provider-ext:network-type':
                    'neutron-networks:network-type-vxlan',
                'admin-state-up': 'true',
                'shared': 'true',
                'status': 'ACTIVE',
                'tenant-id': tenant_id
            }
        self._update(network,
                     'neutron:neutron/networks',
                     'uuid',
                     'network')

    def delete_l3vpn_network(self, uuid):
        self.delete('neutron:neutron/networks/network', id=uuid)

    def get_l3vpn_subnets(self):
        return self.get('neutron:neutron/subnets/')

    def update_l3vpn_subnet(self, id, network_id, tenant_id, network, prefix):
        gateway = utils.compute_gateway(network, prefix)
        (first_ip, last_ip) = utils.compute_hostip_range(network, prefix)

        allocation_pool = \
            {
                'start': first_ip,
                'end': last_ip
            }

        subnet = \
            {
                'uuid': id,
                'ip-version': 'neutron-constants:ip-version-v4',
                'gateway-ip': gateway,
                'name': 'GluonL3VPNSubnet_' + network,
                'network-id': network_id,
                'cidr': network + "/" + str(prefix),
                'enable-dhcp': 'true',
                'tenant-id': tenant_id,
                'allocation-pools': allocation_pool
            }
        self._update(subnet,
                     'neutron:neutron/subnets/',
                     'uuid',
                     'subnet')

    def delete_l3vpn_subnet(self, uuid):
        self.delete('neutron:neutron/subnets/subnet', id=uuid)

    def get_l3_vpn_instances(self):
        return self.get('l3vpn:vpn-instances')

    def update_l3_vpn_instance(self, name, ipv4_route_distinguisher,
                               ipv4_vpnTargets):
        instance_object = \
            {'vpn-instance-name': name,
             'ipv4-family': {'route-distinguisher': ipv4_route_distinguisher,
                             "vpnTargets": {"vpnTarget": ipv4_vpnTargets}}}
        self._update(instance_object,
                     'l3vpn:vpn-instances',
                     'vpn-instance-name',
                     'vpn-instance')

    def delete_l3_vpn_instance(self, name):
        self.delete('l3vpn:vpn-instances/vpn-instance', id=name)

    def get_ietf_interface(self):
        return self.get('ietf-interfaces:interfaces')

    def update_ietf_interface(self, name, parent_interface):
        ietf_interface = {'name': name,
                          'enabled': True,
                          'odl-interface:l2vlan-mode': 'trunk',
                          'type': "iana-if-type:l2vlan",
                          "odl-interface:parent-interface": parent_interface}
        self._update(ietf_interface,
                     'ietf-interfaces:interfaces',
                     'name',
                     'interface')

    def delete_ietf_interface(self, name):
        self.delete('ietf-interfaces:interfaces/interface', id=name)

    def get_vpn_interfaces(self):
        return self.get('l3vpn:vpn-interfaces')

    def update_vpn_interface(self, name, vpn_instance_name, adjacency):
        vpn_interface = {'name': name,
                         'vpn-instance-name': vpn_instance_name,
                         "odl-l3vpn:adjacency": adjacency}
        self._update(vpn_interface,
                     'l3vpn:vpn-interfaces',
                     'name',
                     'vpn-interface')

    def delete_vpn_interface(self, name):
        self.delete('l3vpn:vpn-interfaces/vpn-interface', id=name)

    def _update(self, obj, url, key, path):
        path_plural = path + 's'
        obj_full_struct = None
        try:
            obj_full_struct = self.get(url)
        except Exception:
            pass
        method = 'put'
        if not obj_full_struct or not obj_full_struct[path_plural].get(path):
            method = 'post'
            obj_full_struct = {path_plural: {path: []}}
        objects = obj_full_struct[path_plural][path]
        index = self.key_value_is_in_dicts(objects, key, obj[key])
        if index:
            objects[index] = obj
        else:
            objects.append(obj)
        if method == 'post':
            obj_full_struct = obj_full_struct[path_plural]
        self.sendjson(method, url, obj=obj_full_struct)

    def key_value_is_in_dicts(self, dicts, key, value):
        index = 0
        for dict in dicts:
            if dict.get(key) == value:
                return index
            index = index + 1
        return False
