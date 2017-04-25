#    Copyright 2015, Ericsson AB
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

import pecan
from pecan import rest
import six
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from gluon.api.baseObject import APIBase
from gluon.api.baseObject import APIBaseObject
from gluon.api.baseObject import RootObjectController
from gluon.api.baseObject import SubObjectController
from gluon.api import link
from gluon.api import types
from gluon.particleGenerator.DataBaseModelGenerator \
    import DataBaseModelProcessor


class MyData(object):
    pass


ApiGenData = MyData()
ApiGenData.svc_controllers = {}


class ProtonVersion(APIBase):
    """The root of proton service URL"""

    proton_service = wtypes.text
    """name of proton service"""

    version_id = wtypes.text
    """version id of proton service, e.g. v1, v2..."""

    status = types.create_enum_type('CURRENT', 'STABLE', 'DEPRECATED')
    """Status of the API, which can be CURRENT, STABLE, DEPRECATED"""

    links = [link.Link]
    """A Link that point to a specific version of the API"""

    @staticmethod
    def convert(service, version_id, status='CURRENT'):
        version = ProtonVersion()
        version.proton_service = service
        version.version_id = version_id
        version.status = status
        resource_args = service + '/' + version_id
        version.links = [link.Link.make_link('self',
                                             pecan.request.host_url,
                                             'proton',
                                             resource_args,
                                             bookmark=True)]
        return version


class Resource(ProtonVersion):
    """resource under a specific version of proton service"""

    resource_name = wtypes.text
    """the resource name"""

    @staticmethod
    def convert(service, version_id, resource_name, status='CURRENT'):
        resource = Resource()
        resource.proton_service = service
        resource.verson_id = version_id
        resource.status = status
        resource.resource_name = resource_name
        resource_args = service + '/' + version_id + '/' + resource_name
        resource.links = [link.Link.make_link('self',
                                             pecan.request.host_url,
                                             'proton',
                                             resource_args,
                                             bookmark=True)]
        return resource


class ServiceRoot(APIBase):
    """The root service URL of a proton"""

    default_version = ProtonVersion
    """default version of a service"""

    versions = [ProtonVersion]
    """supported versions of a service"""

    # TODO need to handle multiple versions of a proton service.
    # for now we only have one version, so we put it in
    # both default_version and versions.
    @staticmethod
    def convert(service, version_id):
        version = ProtonVersion.convert(service, version_id)
        root = ServiceRoot()
        root.default_version = version
        root.versions = [version]
        return root


class ServiceVersionRoot(APIBase):
    """The root service URL of a specific version of a proton"""

    resources = [Resource]
    """Resources available for a specific version of a proton service"""

    @staticmethod
    def convert(service_name, version_id):
        from gluon.particleGenerator.generator import load_model_for_service
        model = load_model_for_service(service_name)
        root = ServiceVersionRoot()
        root.resources = list()
        for table_name, table_data in six.iteritems(model['api_objects']):
            resource_name = table_data['api']['plural_name']
            resource = Resource.convert(service_name,
                                        version_id,
                                        resource_name)
            root.resources.append(resource)
        return root


class ServiceController(rest.RestController):
    """Version 1 API controller root."""

    def __init__(self, api_name, version_id):
        self.api_name = api_name
        self.version_id = version_id

    @wsme_pecan.wsexpose(ServiceRoot)
    def get(self):
        return ServiceRoot.convert(self.api_name, self.version_id)



class ServiceVersionController(rest.RestController):
    """Version 1 API controller root."""

    def __init__(self, api_name, version_id):
        self.api_name = api_name
        self.version_id = version_id

    @wsme_pecan.wsexpose(ServiceVersionRoot)
    def get(self):
        return ServiceVersionRoot.convert(self.api_name, self.version_id)


class APIGenerator(object):
    def __init__(self):
        self.data = None
        self.api_name = None
        self.db_models = None

    def add_model(self, model):
        self.data = model

    def create_controller(self, service_name, version_id, root):
        controller = ServiceController(service_name, version_id)
        setattr(root, service_name, controller)
        return controller

    def create_version_controller(self, service_name, version_id, root):
        controller = ServiceVersionController(service_name, version_id)
        setattr(root, version_id, controller)
        return controller

    def create_api(self, root, service_name, db_models):
        self.db_models = db_models
        self.service_name = service_name
        self.controllers = {}
        self.subcontrollers = {}
        self.child = {}
        if not self.data:
            raise Exception('Cannot create API from empty model.')
        for table_name, table_data in six.iteritems(self.data['api_objects']):
            try:
                # For every entry build a (sub_)api_controller
                # an APIObject, an APIObject and an APIListObject
                # and a RealObject is created
                api_object_fields = {}
                for attribute, attr_value in \
                        six.iteritems(table_data['attributes']):
                    api_type = self.translate_model_to_api_type(
                        attr_value.get('type'),
                        attr_value.get('values'),
                        attr_value.get('format'),
                        attr_value.get('min'),
                        attr_value.get('max'))
                    api_object_fields[attribute] = api_type

                # API object
                api_object_class = APIBaseObject.class_builder(
                    table_name, self.db_models[table_name], api_object_fields)

                # api_name
                api_name = table_data['api']['plural_name']

                # primary_key_type
                p_type, p_vals, p_fmt = self.get_primary_key_type(table_data)
                primary_key_type = self.translate_model_to_api_type(p_type,
                                                                    p_vals,
                                                                    p_fmt)

                new_controller_class = RootObjectController.class_builder(
                    api_name, api_object_class, primary_key_type,
                    self.service_name)
                self.controllers[table_name] = new_controller_class
            except Exception:
                print('During processing of table ' + table_name)
                raise

        # Now add all childs since the roots are there now
        # And init the controller since all childs are there now
        for table_name, table_data in six.iteritems(self.data['api_objects']):
            controller = self.controllers[table_name]
            if 'parent' in table_data['api']:
                parent = table_data['api'].get('parent')
                sub_name = table_data['api']['plural_name']
                parent_controller = self.controllers.get(parent)
                new_subcontroller_class = SubObjectController.class_builder(
                    sub_name,
                    controller.api_object_class,
                    controller.primary_key_type,
                    parent_controller.primary_key_type,
                    parent,
                    table_data['api'].get('parent_key'),
                    self.service_name)
                self.subcontrollers[table_name] = new_subcontroller_class
                self.child[parent] = table_name
                setattr(parent_controller, sub_name, new_subcontroller_class())
        for table_name, table_data in six.iteritems(self.data['api_objects']):
            api_name = table_data['api']['plural_name']
            controller_instance = self.controllers[table_name]()
            if table_name in self.child:
                child_name = self.child.get(table_name)
                child_data = self.data['api_objects'].get(child_name)
                child_api_name = child_data['api']['plural_name']
                sub_instance = self.subcontrollers[child_name]()
                setattr(controller_instance, child_api_name, sub_instance)
            setattr(root, api_name, controller_instance)
        ApiGenData.svc_controllers[service_name] = self.controllers

    def get_primary_key_type(self, table_data):
        primary_key = DataBaseModelProcessor.get_primary_key(table_data)
        attr = table_data['attributes'].get(primary_key)
        return attr.get('type'), attr.get('values'), attr.get('format')

    def translate_model_to_api_type(self, model_type, values,
                                    format=None,
                                    min_val=None,
                                    max_val=None):
        # first make sure it is not a foreign key
        if model_type in self.data['api_objects']:
            # if it is we point to the primary key type type of this key
            model_type, values, format = self.get_primary_key_type(
                self.data['api_objects'][model_type])

        if model_type == 'uuid':
            return types.uuid
        elif model_type == 'string':
            if format is not None:
                if format == 'date-time':
                    return types.datetime_type
                elif format == 'json':
                    return types.json_type
                elif format == 'ipv4':
                    return types.ipv4_type
                elif format == 'ipv6':
                    return types.ipv6_type
                elif format == 'mac':
                    return types.mac_type
                elif format == 'uri':
                    return types.uri_type
                elif format == 'email':
                    return types.email_type
                else:
                    return six.text_type
            return six.text_type
        elif model_type == 'enum':
            return types.create_enum_type(*values)
        elif model_type == 'integer':
            return types.int_type(min_val, max_val)
        elif model_type == 'number':
            return types.float_type
        elif model_type == 'boolean':
            return types.boolean
        raise Exception("Type %s not known." % model_type)


def get_controller(service_name, name):
    return ApiGenData.svc_controllers[service_name].get(name)
