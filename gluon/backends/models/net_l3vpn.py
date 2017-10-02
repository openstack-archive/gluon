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
from gluon.particleGenerator import generator


LOG = logging.getLogger(__name__)
logger = LOG


class MyData(object):
    pass


def createDriverData():
    service_list = generator.get_service_list()
    drivers = dict()
    for service in service_list:
        model = generator.load_model_for_service(service)
        generator.verify_model(model)
        driverData = MyData()
        driverData.service = str(model['info']['name'])
        driverData.version = 'v' + str(model['info']['version'])
        driverData.proton_base = 'proton'
        # need a way to dynamically generate binding_name from yaml as well
        driverData.ports_name = 'ports'
        # need a way to dynamically generate binding_name from yaml as well
        driverData.binding_name = 'vpnbindings'
        drivers[service] = driverData
    return drivers


DriverData = createDriverData()


class Provider(backend_base.ProviderBase):

    def driver_for(self, backend, dummy_net, dummy_subnet):
        service = backend['service']
        if service in DriverData:
            driverData = DriverData[service]
            return Driver(backend, dummy_net, dummy_subnet, driverData)
        else:
            return None


class Driver(backend_base.Driver):

    def __init__(self, backend, dummy_net, dummy_subnet, driverData):
        super(Driver, self).__init__(backend, dummy_net, dummy_subnet)
        self._port_url = \
            "{0:s}/{1:s}/{2:s}/{3:s}/{4:s}".format(backend["url"],
                                                   driverData.proton_base,
                                                   driverData.service,
                                                   driverData.version,
                                                   driverData.ports_name)
        self._binding_url = \
            "{0:s}/{1:s}/{2:s}/{3:s}/{4:s}".format(backend["url"],
                                                   driverData.proton_base,
                                                   driverData.service,
                                                   driverData.version,
                                                   driverData.binding_name)

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
