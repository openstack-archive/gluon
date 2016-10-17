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


import abc
import six

from gluon.shim_example.model import Model


class ApiModelBase(object):

    def __init__(self, _name, _backend):
        """Init Method.

        :param _name: name of the API Servce (e.g. net-l3vpn)
        :param _backend: instance of ControllerBase
        :returns: None
        """
        self.model = Model()      # Internal Model for the API Service
        self.backend = _backend   # ControllerModelBase
        self.name = _name

    def handle_object_change(self, object, key, attributes, shim_data):
        """ Called to update model based on changes to etcd database.

        Based on the changes to the model.  This method will call
        event methods on the registered backend object.  The
        event methods are defined in the ControllerBase class.

        :param object: name of the etcd object that changed
        :param key: key of the object
        :param attributes: dictionary of attributes for the object
        :param shim_data: Shim public data (name, client, host_list, etc)
        :returns: None
        """
        pass


    def handle_object_delete(self, object, key, shim_data):
        """ Called to update model based on changes to etcd database.

        Based on the changes to the model.  This method will call
        event methods on the registered backend object.  The
        event methods are defined in the ControllerBase class.

        :param object: name of the etcd object that changed
        :param key: key of the object
        :param host_list: list of hosts managed by this shim layer server
        :param shim_data: Shim public data (name, client, host_list, etc)
        :returns: None
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class HandlerBase(object):

    @abc.abstractmethod
    def bind_port(self, uuid, model, changes):
        """ Called to bind port to VM.

        :param uuid: UUID of Port
        :param model: Model object
        :returns: dict of vif parameters (vif_type, vif_details)
                  {} if bind is rejected
        """
        pass

    @abc.abstractmethod
    def unbind_port(self, uuid, model, changes):
        """ Called to unbind port from VM.

        :param uuid: UUID of Port
        :param model: Model object
        :returns: None
        """
        pass

    @abc.abstractmethod
    def modify_port(self, uuid, model, changes):
        """ Called when attributes change on a bound port.

        :param uuid: UUID of Port
        :param model: Model object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        pass

    @abc.abstractmethod
    def delete_port(self, uuid, model):
        """ Called when a bound port is deleted

        :param uuid: UUID of Port
        :param model: Model object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        pass



    @abc.abstractmethod
    def modify_service(self, uuid, model, changes):
        """ Called when attributes change on a service associated
            with a bound port.

        :param uuid: UUID of Service
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        pass

    @abc.abstractmethod
    def delete_service(self, uuid, model, changes):
        """ Called when a service associated with a bound port is deleted

        :param uuid: UUID of Service
        :param model: Model Object
        :param changes: dictionary of changed attributes
        :returns: None
        """
        pass

    @abc.abstractmethod
    def modify_service_binding(self, uuid, model, prev_binding):
        """ Called when a service is associated with a bound port.

        :param uuid: UUID of Port to locate servcie binding
        :param model: Model Object
        :param prev_binding: dictionary of previous binding
        :returns: None
        """
        pass

    @abc.abstractmethod
    def delete_service_binding(self, model, prev_binding):
        """ Called when a service is disassociated with a bound port.

        :param model: Model Object
        :param prev_binding: dictionary of previous binding
        :returns: None
        """
        pass

    @abc.abstractmethod
    def modify_subport_parent(self, uuid, model, prev_parent,
                              prev_parent_type):
        """ Called when a subport's parent relationship changes.

        :param uuid: UUID of Subport
        :param model: Model object
        :param prev_parent: UUID of previous parent
        :param prev_parent_type: name of previous parent (Port or Subport)
        :returns: None
        """
        pass

