# Copyright (c) 2016 Nokia, Inc.
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

import etcd
import json
import os

from oslo_log import helpers as log_helpers
from oslo_log import log

from gluon.backends.backend_base import BackendLoader
from neutron.plugins.ml2.plugin import Ml2Plugin


class MyData(object):
    pass

PluginData = MyData()
PluginData.etcd_port = 2379
PluginData.etcd_host = '127.0.0.1'
PluginData.gluon_base = "/gluon/port"
PluginData.proton_port = 2704
PluginData.proton_host = '127.0.0.1'

LOG = log.getLogger(__name__)


class GluonPlugin(Ml2Plugin):

    def __init__(self):
        super(GluonPlugin, self).__init__()
        self.backend_manager = BackendLoader()
        self.gluon_network = None
        self.gluon_subnet = None
        self.etcd_client = etcd.Client(host=PluginData.etcd_host,
                                       port=PluginData.etcd_port)

    @log_helpers.log_method_call
    def check_gluon_port(self, id):
        """Get Gluon Port Info

        Check to see if port is a Gluon port. If so, return service,
        url, and tenant_id. Otherwise, it is a Neutron port.  Return None

        :param id: UUID of Port
        """
        try:
            return json.loads(
                self.etcd_client.get(PluginData.gluon_base + '/' + id).value)
        except etcd.EtcdKeyNotFound:
            LOG.debug("Not a Gluon port: %s" % id)
        except etcd.EtcdException:
            LOG.error(
                "Cannot connect to etcd, make sure that etcd is running.")
        except Exception as e:
            LOG.error("Unkown exception:", str(e))
        return None

    @log_helpers.log_method_call
    def get_gluon_port(self, backend, id, fields):
        result = dict()
        try:
            driver = self.backend_manager.get_backend_driver(
                backend, self.gluon_network, self.gluon_subnet)
            port = driver.port(id)
            if fields is None or len(fields) == 0:
                result = port
            else:
                result["id"] = id
                for field in fields:
                    result[field] = port.get(field, "")
        except Exception:
            LOG.debug("Port not found")
        return result

    @log_helpers.log_method_call
    def append_gluon_ports(self, context, filters, result):
        LOG.debug("Context.tenant_id = %s" % context.tenant_id)
        try:
            directory = self.etcd_client.read(PluginData.gluon_base)
            current_service = None
            driver = None
            for keydata in directory.children:
                if keydata.dir:
                    LOG.debug("Skipping directory")
                    continue
                id = os.path.basename(keydata.key)
                LOG.debug("id = %s" % id)
                meta = json.loads(keydata.value)
                if current_service != meta['service']:
                    current_service = meta['service']
                    driver = self.backend_manager.get_backend_driver(
                        meta, self.gluon_network, self.gluon_subnet)
                port = driver.port(id)
                LOG.debug("port = %s" % port)
                if filters is not None:
                    found = True
                    for field, values in filters.items():
                        testval = port.get(field, '')
                        LOG.debug("field = %s" % field)
                        LOG.debug("testval = %s" % testval)
                        LOG.debug("values = %s" % values)
                        found = testval in values
                        if not found:
                            break
                    if found:
                        result.append(port)
                else:
                    result.append(port)
        except etcd.EtcdKeyNotFound:
            LOG.info("Cannot read /gluon directory, not created yet?")
        except etcd.EtcdException:
            LOG.error(
                "Cannot connect to etcd, make sure that etcd is running.")

    @log_helpers.log_method_call
    def update_gluon_port(self, backend, id, port):
        result = dict()
        try:
            driver = self.backend_manager.get_backend_driver(
                backend, self.gluon_network, self.gluon_subnet)
            port_data = port["port"]
            host_id = port_data.get('binding:host_id', None)
            LOG.debug("host_id = %s" % host_id)
            if host_id is None:
                LOG.debug("Performing unbind")
                result = driver.unbind(id)
            else:
                LOG.debug("Performing bind")
                device_owner = port_data.get('device_owner', '')
                zone = 'nova'  # ??
                device_id = port_data.get('device_id', '')
                binding_profile = port_data.get('binding:profile', None)
                result = driver.bind(id, device_owner, zone,
                                     device_id, host_id, binding_profile)
        except Exception as e:
            LOG.debug("Port bind/unbind failed")
            raise e
        return result

    # @log_helpers.log_method_call
    def update_gluon_objects(self, context):
        if self.gluon_network is None:
            nets = super(GluonPlugin, self).get_networks(context)
            for net in nets:
                if net["name"] == 'GluonNetwork':
                    self.gluon_network = net["id"]
                    LOG.debug("Found Gluon network %s" % self.gluon_network)
                    break
        if self.gluon_subnet is None:
            subnets = super(GluonPlugin, self).get_subnets(context)
            for subnet in subnets:
                if subnet["name"] == 'GluonSubnet':
                    self.gluon_subnet = subnet["id"]
                    LOG.debug("Found gluon subnet %s" % self.gluon_subnet)
                    break

    @log_helpers.log_method_call
    def create_subnet(self, context, subnet):
        """Create a subnet.

        Create a subnet, which represents a range of IP addresses
        that can be allocated to devices

        :param context: Neutron API request context
        :param subnet: dictionary describing the subnet, with keys
                       as listed in the  :obj:`RESOURCE_ATTRIBUTE_MAP` object
                       in :file:`neutron/api/v2/attributes.py`.  All keys will
                       be populated.
        """
        result = super(GluonPlugin, self).create_subnet(context, subnet)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def update_subnet(self, context, id, subnet):
        """Update values of a subnet.

        :param context: Neutron API request context
        :param id: UUID representing the subnet to update.
        :param subnet: dictionary with keys indicating fields to update.
                       valid keys are those that have a value of True for
                       'allow_put' as listed in the
                       :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                       :file:`neutron/api/v2/attributes.py`.
        """
        result = super(GluonPlugin, self).update_subnet(context, id, subnet)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_subnet(self, context, id, fields=None):
        """Retrieve a subnet.

        :param context: Neutron API request context
        :param id: UUID representing the subnet to fetch.
        :param fields: a list of strings that are valid keys in a
                       subnet dictionary as listed in the
                       :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                       :file:`neutron/api/v2/attributes.py`. Only these fields
                       will be returned.
        """
        result = super(GluonPlugin, self).get_subnet(context, id, fields)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_subnets(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None, page_reverse=False):
        """Retrieve a list of subnets.

        The contents of the list depends on
        the identity of the user making the request (as indicated by the
        context) as well as any filters.

        :param context: Neutron API request context
        :param filters: a dictionary with keys that are valid keys for
                        a subnet as listed in the :obj:`RESOURCE_ATTRIBUTE_MAP`
                        object in :file:`neutron/api/v2/attributes.py`.
                        Values in this dictionary are an iterable containing
                        values that will be used for an exact match comparison
                        for that value.  Each result returned by this
                        function will have matched one of the values for each
                        key in filters.
        :param fields: a list of strings that are valid keys in a
                       subnet dictionary as listed in the
                       :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                       :file:`neutron/api/v2/attributes.py`. Only these fields
                       will be returned.
        """
        self.update_gluon_objects(context)
        result = super(GluonPlugin, self).get_subnets(
            context, filters, fields, sorts, limit, marker, page_reverse)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_subnets_count(self, context, filters=None):
        """Return the number of subnets.

        The result depends on the identity of
        the user making the request (as indicated by the context) as well as
        any filters.

        :param context: Neutron API request context
        :param filters: a dictionary with keys that are valid keys for
                        a network as listed in the
                        :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                        :file:`neutron/api/v2/attributes.py`.  Values in this
                        dictionary are an iterable containing values that
                        will be used for an exact match comparison for that
                        value.  Each result returned by this function will
                        have matched one of the values for each key in filters.

        .. note:: this method is optional, as it was not part of the originally
                  defined plugin API.
        """
        result = super(GluonPlugin, self).get_subnets_count(context, filters)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def delete_subnet(self, context, id):
        """Delete a subnet.

        :param context: Neutron API request context
        :param id: UUID representing the subnet to delete.
        """
        result = super(GluonPlugin, self).delete_subnet(context, id)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def create_subnetpool(self, context, subnetpool):
        """Create a subnet pool.

        :param context: Neutron API request context
        :param subnetpool: Dictionary representing the subnetpool to create.
        """
        result = super(GluonPlugin, self).create_subnetpool(
            context, subnetpool)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def update_subnetpool(self, context, id, subnetpool):
        """Update a subnet pool.

        :param context: Neutron API request context
        :param subnetpool: Dictionary representing the subnetpool attributes
                           to update.
        """
        result = super(GluonPlugin, self).update_subnetpool(
            context, id, subnetpool)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_subnetpool(self, context, id, fields=None):
        """Show a subnet pool.

        :param context: Neutron API request context
        :param id: The UUID of the subnetpool to show.
        """
        result = super(GluonPlugin, self).get_subnetpool(
            context, id, fields)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_subnetpools(self, context, filters=None, fields=None,
                        sorts=None, limit=None, marker=None,
                        page_reverse=False):
        """Retrieve list of subnet pools."""
        result = super(GluonPlugin, self).get_subnetpools(
            context, filters, fields, sorts, limit, marker, page_reverse)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def delete_subnetpool(self, context, id):
        """Delete a subnet pool.

        :param context: Neutron API request context
        :param id: The UUID of the subnet pool to delete.
        """
        result = super(GluonPlugin, self).delete_subnetpool(context, id)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def create_network(self, context, network):
        """Create a network.

        Create a network, which represents an L2 network segment which
        can have a set of subnets and ports associated with it.

        :param context: Neutron API request context
        :param network: dictionary describing the network, with keys
                        as listed in the  :obj:`RESOURCE_ATTRIBUTE_MAP` object
                        in :file:`neutron/api/v2/attributes.py`.  All keys will
                        be populated.

        """
        result = super(GluonPlugin, self).create_network(context, network)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def update_network(self, context, id, network):
        """Update values of a network.

        :param context: Neutron API request context
        :param id: UUID representing the network to update.
        :param network: dictionary with keys indicating fields to update.
                        valid keys are those that have a value of True for
                        'allow_put' as listed in the
                        :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                        :file:`neutron/api/v2/attributes.py`.
        """
        result = super(GluonPlugin, self).update_network(
            context, id, network)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_network(self, context, id, fields=None):
        """Retrieve a network.

        :param context: Neutron API request context
        :param id: UUID representing the network to fetch.
        :param fields: a list of strings that are valid keys in a
                       network dictionary as listed in the
                       :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                       :file:`neutron/api/v2/attributes.py`. Only these fields
                       will be returned.
        """
        result = super(GluonPlugin, self).get_network(context, id, fields)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_networks(self, context, filters=None, fields=None,
                     sorts=None, limit=None, marker=None, page_reverse=False):
        """Retrieve a list of networks.

        The contents of the list depends on
        the identity of the user making the request (as indicated by the
        context) as well as any filters.

        :param context: Neutron API request context
        :param filters: a dictionary with keys that are valid keys for
                        a network as listed in the
                        :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                        :file:`neutron/api/v2/attributes.py`.  Values in this
                        dictionary are an iterable containing values that will
                        be used for an exact match comparison for that value.
                        Each result returned by this function will have matched
                        one of the values for each key in filters.
        :param fields: a list of strings that are valid keys in a
                       network dictionary as listed in the
                       :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                       :file:`neutron/api/v2/attributes.py`. Only these fields
                       will be returned.
        """
        self.update_gluon_objects(context)
        result = super(GluonPlugin, self).get_networks(
            context, filters, fields, sorts, limit, marker, page_reverse)
        return result

    @log_helpers.log_method_call
    def get_networks_count(self, context, filters=None):
        """Return the number of networks.

        The result depends on the identity
        of the user making the request (as indicated by the context) as well
        as any filters.

        :param context: Neutron API request context
        :param filters: a dictionary with keys that are valid keys for
                        a network as listed in the
                        :obj:`RESOURCE_ATTRIBUTE_MAP` object
                        in :file:`neutron/api/v2/attributes.py`. Values in
                        this dictionary are an iterable containing values that
                        will be used for an exact match comparison for that
                        value.  Each result returned by this function will have
                        matched one of the values for each key in filters.

        NOTE: this method is optional, as it was not part of the originally
              defined plugin API.
        """
        result = super(GluonPlugin, self).get_networks_count(context, filters)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def delete_network(self, context, id):
        """Delete a network.

        :param context: Neutron API request context
        :param id: UUID representing the network to delete.
        """
        result = super(GluonPlugin, self).delete_network(context, id)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def create_port(self, context, port):
        """Create a port.

        Create a port, which is a connection point of a device (e.g., a VM
        NIC) to attach to a L2 neutron network.

        :param context: Neutron API request context
        :param port: dictionary describing the port, with keys as listed in the
                     :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                     :file:`neutron/api/v2/attributes.py`.  All keys will be
                     populated.
        """
        self.update_gluon_objects(context)
        result = super(GluonPlugin, self).create_port(context, port)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def update_port(self, context, id, port):
        """Update values of a port.

        :param context: Neutron API request context
        :param id: UUID representing the port to update.
        :param port: dictionary with keys indicating fields to update.
                     valid keys are those that have a value of True for
                     'allow_put' as listed in the :obj:`RESOURCE_ATTRIBUTE_MAP`
                     object in :file:`neutron/api/v2/attributes.py`.
        """
        backend = self.check_gluon_port(id)
        if backend is None:
            result = super(GluonPlugin, self).update_port(context, id, port)
        else:
            result = self.update_gluon_port(backend, id, port)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_port(self, context, id, fields=None):
        """Retrieve a port.

        :param context: Neutron API request context
        :param id: UUID representing the port to fetch.
        :param fields: a list of strings that are valid keys in a port
                       dictionary as listed in the
                       :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                       :file:`neutron/api/v2/attributes.py`. Only these fields
                       will be returned.
        """
        backend = self.check_gluon_port(id)
        if backend is None:
            result = super(GluonPlugin, self).get_port(context, id, fields)
        else:
            result = self.get_gluon_port(backend, id, fields)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_ports(self, context, filters=None, fields=None,
                  sorts=None, limit=None, marker=None, page_reverse=False):
        """Retrieve a list of ports.

        The contents of the list depends on the identity of the user making
        the request (as indicated by the context) as well as any filters.

        :param context: Neutron API request context
        :param filters: a dictionary with keys that are valid keys for
                        a port as listed in the  :obj:`RESOURCE_ATTRIBUTE_MAP`
                        object in :file:`neutron/api/v2/attributes.py`. Values
                        in this dictionary are an iterable containing values
                        that will be used for an exact match comparison for
                        that value.  Each result returned by this function will
                        have matched one of the values for each key in filters.
        :param fields: a list of strings that are valid keys in a
                       port dictionary as listed in the
                       :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                       :file:`neutron/api/v2/attributes.py`. Only these fields
                       will be returned.
        """
        self.update_gluon_objects(context)
        result = super(GluonPlugin, self).get_ports(
            context, filters, fields, sorts, limit, marker, page_reverse)
        self.append_gluon_ports(context, filters, result)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def get_ports_count(self, context, filters=None):
        """Return the number of ports.

        The result depends on the identity of the user making the request
        (as indicated by the context) as well as any filters.

        :param context: Neutron API request context
        :param filters: a dictionary with keys that are valid keys for
                        a network as listed in the
                        :obj:`RESOURCE_ATTRIBUTE_MAP` object in
                        :file:`neutron/api/v2/attributes.py`.  Values in this
                        dictionary are an iterable containing values that will
                        be used for an exact match comparison for that value.
                        Each result returned by this function will have matched
                        one of the values for each key in filters.

        .. note:: this method is optional, as it was not part of the originally
                  defined plugin API.
        """
        result = super(GluonPlugin, self).get_ports_count(context, filters)
        LOG.debug(result)
        return result

    @log_helpers.log_method_call
    def delete_port(self, context, id, l3_port_check=True):
        """Delete a port.

        :param context: Neutron API request context
        :param id: UUID representing the port to delete.
        """
        result = super(GluonPlugin, self).delete_port(
            context, id, l3_port_check)
        LOG.debug(result)
        return result
