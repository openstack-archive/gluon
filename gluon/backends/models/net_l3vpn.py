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

from oslo_log import log as logging

LOG = logging.getLogger(__name__)
logger = LOG


class MyData(object):
    pass

DriverData = MyData()
DriverData.service = u'net-l3vpn'
DriverData.proton_base = 'proton'
DriverData.ports_name = 'baseports'


class Provider(backend_base.ProviderBase):

    def driver_for(self, backend, dummy_net, dummy_subnet):
        if backend['service'] == DriverData.service:
            return Driver(backend, dummy_net, dummy_subnet)
        else:
            return None


class Driver(backend_base.Driver):

    def __init__(self, backend, dummy_net, dummy_subnet):
        super(Driver, self).__init__(backend, dummy_net, dummy_subnet)
        self._port_url = \
            "{0:s}/{1:s}/{2:s}/{3:s}".format(backend["url"],
                                             DriverData.proton_base,
                                             DriverData.service,
                                             DriverData.ports_name)

    def _convert_port_data(self, port_data):
        LOG.debug("proton port_data = %s" % port_data)
        ret_port_data = {}
        ret_port_data["created_at"] = port_data["created_at"]
        ret_port_data["updated_at"] = port_data["updated_at"]
        ret_port_data["id"] = port_data["id"]
        ret_port_data["devname"] = 'tap%s' % port_data['id'][:11]
        ret_port_data["name"] = port_data.get("name")
        ret_port_data["status"] = port_data["status"]
        ret_port_data["admin_state_up"] = port_data["admin_state_up"]
        ret_port_data["network_id"] = self._dummy_net
        ret_port_data["tenant_id"] = port_data.get("tenant_id", '')
        ret_port_data["device_owner"] = port_data.get("device_owner", '')
        ret_port_data["device_id"] = port_data.get("device_id", '')
        ret_port_data["mac_address"] = port_data["mac_address"]
        ret_port_data["extra_dhcp_opts"] = []
        ret_port_data["allowed_address_pairs"] = []
        ret_port_data["fixed_ips"] = \
            [{"ip_address": port_data.get("ipaddress", "0.0.0.0"),
              "subnet_id": self._dummy_subnet}]
        ret_port_data["security_groups"] = []
        ret_port_data["binding:host_id"] = port_data.get("host_id", '')
        vif_details = port_data.get("vif_details")
        if vif_details is None:
            vif_details = '{}'
        ret_port_data["binding:vif_details"] = json.loads(vif_details)
        ret_port_data["binding:vif_type"] = port_data.get("vif_type", '')
        ret_port_data["binding:vnic_type"] = \
            port_data.get("vnic_type", 'normal')
        profile = port_data.get("profile", '{}')
        if profile is None or profile == '':
            profile = '{}'
        ret_port_data["binding:profile"] = json.loads(profile)
        for k in ret_port_data:
            if ret_port_data[k] is None:
                ret_port_data[k] = ''
        return ret_port_data
