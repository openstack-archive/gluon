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

import abc
import six
import stevedore
import json
import time

import etcd

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils.uuidutils import generate_uuid

from gluon.api import types
from gluon.sync_etcd.thread import SyncData


LOG = logging.getLogger(__name__)
logger = LOG


class MyData:
    pass

ManagerData = MyData()
ManagerData.managers = dict()


@six.add_metaclass(abc.ABCMeta)
class ProviderBase(object):

    def __init__(self):
        self._drivers = {}

    @abc.abstractmethod
    def driver_for(self, api_name, host, port, etcd_host, etcd_port):
        return None


#
# Base class for ApiManager
#
class ApiManager(object):

    def __init__(self, api_name, host, port, etcd_host, etcd_port):
        self.url = "http://%s:%d" % (host, port)
        self.service = api_name
        self.wait_index = 0
        self.etcd_client = etcd.Client(host=etcd_host,
                                       port=etcd_port,
                                       read_timeout=2)

    def setup_bind_key(self, key):
        etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller", self.service,
                                                    "ProtonBasePort", key)
        #
        # If key does not exists, create it so we can wait on it to change.
        #
        try:
            message = self.etcd_client.read(etcd_key)
            self.wait_index = message.modifiedIndex + 1
        except etcd.EtcdKeyNotFound:
            LOG.info("Key Not Found, creating it: %s" % etcd_key)
            data = dict()
            value = json.dumps(data)
            self.etcd_client.write(etcd_key, value)
        except:
            pass

    def wait_for_bind(self, key):
        etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller", self.service,
                                                    "ProtonBasePort", key)
        retry = 4
        ret_val = dict()
        while retry > 0:
            try:
                LOG.info("watching %s" % etcd_key)
                message = self.etcd_client.read(etcd_key, wait=True,
                                                waitIndex=self.wait_index)
                ret_val = json.loads(message.value)
                break
            except etcd.EtcdKeyNotFound:
                LOG.info("Key Not Found %s" % etcd_key)
                retry -= 1
                time.sleep(1)
            except etcd.EtcdWatchTimedOut:
                LOG.info("timeout")
                retry -= 1
            except etcd.EtcdException:
                LOG.error("Cannot connect to etcd, make sure it is running")
                retry = 0
            except Exception, e:
                LOG.error("Unknown error: %s" % str(e))
                retry -= 1
        return ret_val

    def create_baseports(self, api_class, values):
        ret_obj = api_class.create_in_db(values)
        #
        # Register port in Gluon
        #
        msg = {"port_id": values.get('id', ''),
               "tenant_id": values.get('tenant_id', ''),
               "service": self.service,
               "url": self.url,
               "operation": "register"}
        SyncData.sync_queue.put(msg)
        return ret_obj

    def update_baseports(self, api_class, key, new_values):
        has_bind_attrs = (new_values.get("host_id") is not None and
                          new_values.get("device_id") is not None)
        is_bind_request = (has_bind_attrs and
                           new_values.get("host_id", "") != "" and
                           new_values.get("device_id", "") != "")
        if is_bind_request:
            self.setup_bind_key(key)
        ret_obj = api_class.update_in_db(key, new_values)
        if is_bind_request:
            # bind
            vif_dict = self.wait_for_bind(key)
            if len(vif_dict) == 0:
                LOG.error("No binding information available")
            else:
                LOG.info(vif_dict)
                vif_values = dict()
                if "vif_type" in vif_dict:
                    vif_values["vif_type"] = vif_dict["vif_type"]
                if "vif_details" in vif_dict:
                    vif_values["vif_details"] = \
                        json.dumps(vif_dict["vif_details"])
                if len(vif_values) > 0:
                    ret_obj = api_class.update_in_db(key, vif_values)
        elif has_bind_attrs:  # unbind request
            vif_dict = dict()
            vif_dict["vif_type"] = None
            vif_dict["vif_details"] = json.dumps({})
            ret_obj = api_class.update_in_db(key, vif_dict)
        return ret_obj

    def delete_baseports(self, api_class, key):
        #
        # Remove port from Gluon
        #
        msg = {"port_id": key,
               "service": self.service,
               "operation": "deregister"}
        SyncData.sync_queue.put(msg)
        return api_class.delete_from_db(key)

    def handle_create(self, root_class, values):
        api_class = root_class.api_object_class
        #
        # If the primary key is a UUID and it is not set, we generate
        # one and set it here.
        #
        if isinstance(root_class.primary_key_type, types.UuidType):
            primary_key = api_class.db_model.get_primary_key()
            key_value = values.get(primary_key)
            if not key_value or (key_value and key_value == ""):
                values[primary_key] = generate_uuid()
        if root_class.__name__ == 'baseports':
            return self.create_baseports(root_class.api_object_class, values)
        else:
            return api_class.create_in_db(values)

    def handle_update(self, root_class, key, new_values):
        api_class = root_class.api_object_class
        if root_class.__name__ == 'baseports':
            return self.update_baseports(api_class, key, new_values)
        else:
            return api_class.update_in_db(key, new_values)

    def handle_delete(self, root_class, key):
        api_class = root_class.api_object_class
        if root_class.__name__ == 'baseports':
            return self.delete_baseports(api_class, key)
        else:
            return api_class.delete_from_db(key)


def load_api_manager(api_name):
    """Register a given API manager
    :param api_name:
    """
    loader = ManagerLoader()
    ManagerData.managers[api_name] = loader.get_manager_driver(api_name)
    return ManagerData.managers.get(api_name)


def get_api_manager(api_name):
    """Return registered API Manager instance

    :return:
    """
    mgr = ManagerData.managers.get(api_name)
    if mgr is None:
        mgr = load_api_manager(api_name)
    return mgr


class ManagerLoader(object):
    """Class used to load manager drivers.
    """
    def __init__(self):

        def upset(manager, entrypoint, exception):
            logger.error('Failed to load %s: %s' % (entrypoint, exception))

        # Sort out the client drivers
        self._mgr = stevedore.ExtensionManager(
            namespace='gluon.managers',
            on_load_failure_callback=upset,
            invoke_on_load=True
        )
        for f in self._mgr:
            logger.info('Found manager %s' % f.name)

    def get_manager_driver(self, api_name):

        for f in self._mgr:
            x = f.obj.driver_for(api_name,
                                 cfg.CONF.api.host,
                                 cfg.CONF.api.port,
                                 cfg.CONF.api.etcd_host,
                                 cfg.CONF.api.etcd_port)
            if x is not None:
                logger.info("Using manager: %s" % api_name)
                return x

        logger.warn('No manager driver for service, using default %s',
                    api_name)
        return ApiManager(api_name,
                          cfg.CONF.api.host,
                          cfg.CONF.api.port,
                          cfg.CONF.api.etcd_host,
                          cfg.CONF.api.etcd_port)
