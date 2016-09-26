# Copyright (c) 2015 Cisco Systems, Inc.
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

from gluon.backends import backend_base
from gluon.backends.backends.proton_client import Client
from oslo_config import cfg


API_SERVICE_OPTS = [
    cfg.StrOpt('ports_name',
               default='baseports',
               help='URL to get ports'),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gluon',
                         title='Options for the gluon')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)


class Provider(backend_base.Provider):

    def __init__(self, logger):
        self._drivers = {}
        self._logger = logger

    def driver_for(self, backend, dummy_net, dummy_subnet):
        if backend['service'] == u'net-l3vpn':
            return Driver(backend, self._logger, dummy_net, dummy_subnet)
        else:
            return None


class Driver(backend_base.Driver):

    def __init__(self, backend, logger, dummy_net, dummy_subnet):
        self._logger = logger
        self._client = Client(backend)
        self._port_url = backend["url"] + "/v1/" + cfg.CONF.gluon.ports_name
        self._dummy_net = dummy_net
        self._dummy_subnet = dummy_subnet

    def bind(self, port_id, device_owner, zone, device_id, host_id, binding_profile):
        args = {}
        args["device_owner"] = device_owner
        args["device_id"] = device_id
        args["host_id"] = host_id
        if binding_profile is not None:
            args["profile"] = json.dumps(binding_profile, indent=0)
        args["zone"] = zone
        url = self._port_url + "/"+ port_id + "/update"
        return self._convert_port_data(self._client.do_put(url, args))

    def unbind(self, port_id):
        args = {}
        args["device_owner"] = ''
        args["device_id"] = ''
        args["host_id"] = ''
        args["profile"] = ''
        args["zone"] = ''
        url = self._port_url + "/"+ port_id + "/update"
        return self._convert_port_data(self._client.do_put(url, args))

    def port(self, port_id):
        url = self._port_url + "/"+ port_id
        return self._convert_port_data(self._client.json_get(url))

    def ports(self):
        port_list = self._client.json_get(self._port_url)
        ret_port_list = []
        for port in port_list:
            ret_port_list.append(self._convert_port_data(port))
        return ret_port_list

    def _convert_port_data(self, port_data):
        ret_port_data = {}
        ret_port_data["id"] = port_data["id"]
        ret_port_data["devname"] = 'tap%s' % port_data['id'][:11]
        ret_port_data["name"] = port_data.get("name")
        ret_port_data["status"] = port_data["status"]
        ret_port_data["admin_state_up"] = port_data["admin_state_up"]
        ret_port_data["network_id"] = self._dummy_net
        ret_port_data["tenant_id"] = port_data.get("tenant_id", '')
        ret_port_data["device_owner"] = port_data.get("device_owner",'')
        ret_port_data["device_id"] = port_data.get("device_id",'')
        ret_port_data["mac_address"] = port_data["mac_address"]
        ret_port_data["extra_dhcp_opts"] = []
        ret_port_data["allowed_address_pairs"] = []
        ret_port_data["fixed_ips"] = [{"ip_address": port_data["ipaddress"], "subnet_id": self._dummy_subnet}]
        ret_port_data["security_groups"] = []
        ret_port_data["binding:host_id"] = port_data.get("host_id",'')
        ret_port_data["binding:vif_details"] = json.loads(port_data.get("vif_details",'{}'))
        ret_port_data["binding:vif_type"] = port_data.get("vif_type", 'ovs')
        ret_port_data["binding:vnic_type"] = port_data.get("vnic_type", 'normal')
        if port_data.get("profile", '') != '':
            ret_port_data["binding:profile"] = json.loads(port_data.get("profile", '{}'))
        return ret_port_data
