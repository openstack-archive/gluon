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

import abc
import json
import six
import stevedore

from gluon.backends.proton_client import Client
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
logger = LOG


@six.add_metaclass(abc.ABCMeta)
class ProviderBase(object):
    def __init__(self):
        self._drivers = {}

    @abc.abstractmethod
    def driver_for(self, backend, dummy_net, dummy_subnet):
        return None


@six.add_metaclass(abc.ABCMeta)
class Driver(object):
    def __init__(self, backend, dummy_net, dummy_subnet):
        self._client = Client(backend)
        self._dummy_net = dummy_net
        self._dummy_subnet = dummy_subnet

    def bind(self, port_id, device_owner, zone, device_id, host_id,
             binding_profile):
        args = {"device_owner": device_owner, "device_id": device_id,
                "host_id": host_id}
        if binding_profile is not None:
            args["profile"] = json.dumps(binding_profile, indent=0)
        # args["zone"] = zone  # Do we need this?
        url = self._port_url + "/" + port_id
        return self._convert_port_data(self._client.do_put(url, args))

    def unbind(self, port_id):
        args = {"device_owner": '', "device_id": '', "host_id": '',
                "profile": ''}
        # args["zone"] = ''  # Do we need this?
        url = self._port_url + "/" + port_id
        return self._convert_port_data(self._client.do_put(url, args))

    def port(self, port_id):
        url = self._port_url + "/" + port_id
        return self._convert_port_data(self._client.json_get(url))

    def ports(self):
        port_list = self._client.json_get(self._port_url)
        ret_port_list = []
        for port in port_list:
            ret_port_list.append(self._convert_port_data(port))
        return ret_port_list

    def _convert_port_data(self, port_data):
        #
        # This assumes ipaddress information is in the port object
        #
        LOG.debug("proton port_data = %s" % port_data)
        ret_port_data = {"created_at": port_data["created_at"],
                         "updated_at": port_data["updated_at"],
                         "id": port_data["id"],
                         "devname": 'tap%s' % port_data['id'][:11],
                         "name": port_data.get("name"),
                         "status": port_data["status"],
                         "admin_state_up": port_data["admin_state_up"],
                         "network_id": self._dummy_net,
                         "tenant_id": port_data.get("tenant_id", ''),
                         "device_owner": port_data.get("device_owner", ''),
                         "device_id": port_data.get("device_id", ''),
                         "mac_address": port_data["mac_address"],
                         "extra_dhcp_opts": [], "allowed_address_pairs": []}
        if 'ipaddress' in port_data:
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


class BackendLoader(object):
    """Class used to manage backend drivers in Gluon.

    Drivers know how to talk to particular network services.  It
    doesn't have to be a 1:1 mapping; the service registers with
    Neutron and can declare which comms driver to use.

    """

    def __init__(self):

        def upset(manager, entrypoint, exception):
            logger.error('Failed to load %s: %s' % (entrypoint, exception))

        # Sort out the client drivers
        # TODO(name) should probably be NamedExtensionManager
        self._mgr = stevedore.ExtensionManager(
            namespace='gluon.backends',
            on_load_failure_callback=upset,
            invoke_on_load=True
        )
        for f in self._mgr:
            logger.info('Got backend %s' % f.name)
        logger.info('Backend management enabled')

    def get_backend_driver(self, backend, dummy_net, dummy_subnet):

        for f in self._mgr:
            x = f.obj.driver_for(backend, dummy_net, dummy_subnet)
            if x is not None:
                return x

        logger.error('No backend driver for service %s', backend["service"])
        return None
