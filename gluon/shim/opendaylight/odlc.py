'''
Created on Sep 11, 2015

@author: enikher
'''
import requests
import pprint
try:
    from neutron.openstack.common import jsonutils
except ImportError:
    from oslo_serialization import jsonutils
import json
import ConfigParser
from utils.log import LOG, log_enter_exit, for_all_methods

ODL_IP = '192.168.0.21'
ODL_PORT = '8080'
ODL_PASSWORD = 'admin'
ODL_USERNAME = 'admin'


@for_all_methods(log_enter_exit)
class ODL_CLient(object):

    def __init__(self, odl_ip=ODL_IP, odl_port=ODL_PORT, user=ODL_USERNAME,
                 passw=ODL_PASSWORD, backend='neutron'):
        if backend == 'neutron':
            self.url = ("http://%(ip)s:%(port)s/controller/nb/v2/neutron" %
                        {'ip': odl_ip,
                         'port': odl_port})
        if backend == 'restconf':
            self.url = ("http://%(ip)s:%(port)s/restconf/config" %
                        {'ip': odl_ip,
                         'port': odl_port})
        self.auth = (user, passw)
        self.timeout = 10

    def nets(self):
        return self.get('networks')

    def get(self, obj_typ):
        return self.sendjson('get', obj_typ).get(obj_typ)

    def cleanup_typ(self, obj_typ):
        for obj in self.get(obj_typ):
            self.delete(obj_typ, id=obj['id'])

    def cleanup(self):
        self.cleanup_typ('ports')
        self.cleanup_typ('subnets')
        self.cleanup_typ('networks')

    def get_f(self, obj_typ, value):
        objs = self.get(obj_typ)
        filtered = []
        for obj in objs:
            if value in str(obj):
                filtered.append(obj)
        return filtered

        if isinstance(obj, list):
            for entry in obj:
                if type(entry) is type(value) and entry == value:
                    return entry

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
            import pdb;pdb.set_trace()
            return r
        try:
            return json.loads(r.content)
        except Exception:
            LOG.debug("%s" % r)
            return

    def o(self):
        nets = self.get('networks')
        subnets = self.get('networks')
        ports = self.get('ports')
        pp = pprint.PrettyPrinter(indent=2)
        print("-------------Networks-----------------")
        pp.pprint(nets)
        print("-------------Subnets-----------------")
        pp.pprint(subnets)
        print("-------------Ports-----------------")
        pp.pprint(ports)


@for_all_methods(log_enter_exit)
class RestConfClient(ODL_CLient):

    def __init__(self):
        super(RestConfClient, self).__init__(backend='restconf')

    def get(self, urlpath):
        output = self.sendjson('get', urlpath)
        return output

    def o(self):
        pp = pprint.PrettyPrinter(indent=2)
        print("-------------l3_vpn_instance-----------------")
        pp.pprint(self.get_l3_vpn_instances())
        print("-------------vpn_interfaces-----------------")
        pp.pprint(self.get_vpn_interfaces())
        print("-------------ietf_interface-----------------")
        pp.pprint(self.get_ietf_interface())

    def get_transport_zones(self):
        print("transport_zones")
        self.get('itm:transport-zones')

    def get_tunnel_status(self):
        print("itm-state:dpn-endpoints")
        self.get('itm-state:dpn-endpoints')

    def get_l3_vpn_instances(self):
        return self.get('l3vpn:vpn-instances')

    def update_l3_vpn_instance(self, name, ipv4_route_distinguisher,
                               ipv4_vpnTargets):
        instance_object = \
            {'vpn-instance-name': name,
             'ipv4-family': {'route-distinguisher': ipv4_route_distinguisher,
                             "vpnTargets": {"vpnTarget": ipv4_vpnTargets}}}
        self._update(instance_object, 'l3vpn:vpn-instances',
                     'vpn-instance-name', 'vpn-instance')

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
        self._update(ietf_interface, 'ietf-interfaces:interfaces', 'name',
                     'interface')

    def delete_ietf_interface(self, name):
        self.delete('ietf-interfaces:interfaces/interface', id=name)

    def get_vpn_interfaces(self):
        return self.get('l3vpn:vpn-interfaces')

    def update_vpn_interface(self, name, vpn_instance_name, adjacency):
        vpn_interface = {'name': name,
                         'vpn-instance-name': vpn_instance_name,
                         "odl-l3vpn:adjacency": adjacency}
        self._update(vpn_interface, 'l3vpn:vpn-interfaces', 'name',
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
            obj_full_struct=obj_full_struct[path_plural]
        self.sendjson(method, url,
                      obj=obj_full_struct)

    def key_value_is_in_dicts(self, dicts, key, value):
        index = 0
        for dict in dicts:
            if dict.get(key) == value:
                return index
            index = index + 1
        return False


def main():
    # parse args
    pass

if __name__ == '__main__':
    main()

global odlc
odlc = ODL_CLient()
global restconf
restconf = RestConfClient()

