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

from oslo_log import log as logging

from gluon.backends import backend_base
from gluon.common import exception as exc


LOG = logging.getLogger(__name__)
logger = LOG


class MyData(object):
    pass

DriverData = MyData()
DriverData.service = u'net-l3vpn'
DriverData.proton_base = 'proton'
DriverData.ports_name = 'ports'
DriverData.binding_name = 'vpnbindings'


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
        self._binding_url = \
            "{0:s}/{1:s}/{2:s}/{3:s}".format(backend["url"],
                                             DriverData.proton_base,
                                             DriverData.service,
                                             DriverData.binding_name)

    def port(self, port_id):
        url = self._port_url + "/" + port_id
        port_data = self._client.json_get(url)
        #
        # The untagged interface has the same UUID as the port
        # First we get the service binding to retrive the ipaddress
        #
        url = self._binding_url + "/" + port_id
        try:
            svc_bind_data = self._client.json_get(url)
        except exc.GluonClientException:
            svc_bind_data = None
        if svc_bind_data:
            port_data['ipaddress'] = svc_bind_data.get("ipaddress")
        return self._convert_port_data(port_data)

    def ports(self):
        port_list = self._client.json_get(self._port_url)
        ret_port_list = []
        for port in port_list:
            url = self._binding_url + "/" + port.id
            try:
                svc_bind_data = self._client.json_get(url)
            except exc.GluonClientException:
                svc_bind_data = None
            if svc_bind_data:
                port['ipaddress'] = svc_bind_data.get("ipaddress")
            ret_port_list.append(self._convert_port_data(port))
        return ret_port_list
