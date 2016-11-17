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


from oslo_log import log as logging

from gluon.managers.manager_base import ApiManager
from gluon.managers.manager_base import ProviderBase


LOG = logging.getLogger(__name__)
logger = LOG


class Provider(ProviderBase):

    def driver_for(self, api_name, host, port, etcd_host, etcd_port):
        if api_name == u'net-l3vpn':
            return ProtonManager(api_name, host, port, etcd_host, etcd_port)
        else:
            return None


#
# It is possible to add model specific functionality here if needed.
# Otherwise, just use base class.
#
class ProtonManager(ApiManager):
    def __init__(self, api_name, host, port, etcd_host, etcd_port):
        super(ProtonManager, self).__init__(api_name, host, port,
                                            etcd_host, etcd_port)
