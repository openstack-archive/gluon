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

import pkg_resources
import six
import yaml

from oslo_log import log as logging

from gluon.common import exception as exc
from gluon.db.sqlalchemy import models as sql_models

LOG = logging.getLogger(__name__)


class MyData(object):
    pass


GenData = MyData()
GenData.DBGeneratorInstance = None
GenData.models = dict()
GenData.package_name = "gluon"
GenData.model_dir = "models"


def raise_format_error(format_str, val_tuple):
    str = format_str % val_tuple
    raise exc.InvalidFileFormat(str)


def raise_obj_error(obj_name, format_str, val_tuple):
    str = format_str % val_tuple
    raise_format_error("Object: %s, %s", (obj_name, str))


def validate_attributes(obj_name, obj, model):
    props = ['type', 'primary', 'description', 'required',
             'length', 'values', 'format', 'min', 'max']
    types = ['integer', 'number', 'string', 'boolean', 'uuid', 'enum']
    formats = ['date-time', 'json', 'ipv4', 'ipv6', 'mac', 'uri', 'email']
    int_formats = ['int32', 'int64']

    for attr_name, attr_val in six.iteritems(obj.get('attributes')):
        if 'type' not in attr_val:
            raise_obj_error(obj_name,
                            'A type property is not specified for '
                            'attribute: %s, ',
                            (attr_name))
        for prop_name, prop_val in six.iteritems(attr_val):
            if prop_name in props:
                if prop_name == 'type':
                    if prop_val not in types and \
                       prop_val not in model.get('api_objects'):
                        raise_obj_error(
                            obj_name,
                            'Invalid type: %s for attribute: %s, '
                            'expected type or API Object Name',
                            (prop_val, attr_name))
                    elif prop_val == 'enum':
                        if 'values' not in attr_val:
                            raise_obj_error(
                                obj_name,
                                'No enum values specified for attribute: %s',
                                (attr_name))
                elif prop_name == 'format':
                    if attr_val.get('type') != 'string' and \
                       attr_val.get('type') != 'integer':
                        raise_obj_error(
                            obj_name,
                            'Format is only valid for string or integer '
                            'type: %s, attribute: %s',
                            (prop_val, attr_name))
                    if attr_val.get('type') == 'string':
                        if prop_val not in formats:
                            raise_obj_error(
                                obj_name,
                                'Invalid format: %s for attribute: %s',
                                (prop_val, attr_name))
                    if attr_val.get('type') == 'integer':
                        if prop_val not in int_formats:
                            raise_obj_error(
                                obj_name,
                                'Invalid int format: %s for attribute: %s',
                                (prop_val, attr_name))
                elif prop_name == 'values':
                    if attr_val.get('type') != 'enum':
                        raise_obj_error(
                            obj_name,
                            'Values without enum specified for attribute: %s',
                            (attr_name))
                elif prop_name == 'length':
                    if not isinstance(prop_val, six.integer_types):
                        raise_obj_error(
                            obj_name,
                            'Integer values required for length: '
                            '%s,  attribute: %s',
                            (prop_val, attr_name))
                elif prop_name == 'min' or prop_name == 'max':
                    if attr_val.get('type') != 'integer':
                        raise_obj_error(
                            obj_name,
                            'Min/Max is only valid for integer '
                            'type: %s,  attribute: %s',
                            (prop_val, attr_name))
                    if not isinstance(prop_val, six.integer_types):
                        raise_obj_error(
                            obj_name,
                            'Integer values required for Min/Max: '
                            '%s,  attribute: %s',
                            (prop_val, attr_name))
            else:
                raise_obj_error(
                    obj_name,
                    'Invalid property in AttributeSchema: %s for %s',
                    (prop_name, attr_name))


def validate_api(obj_name, obj_val, model):
    api = obj_val.get('api')
    if 'name' not in api:
        raise_format_error('Name is missing in API object for: %s', (obj_name))
    if 'parent' in api:
        if api.get('parent') not in model.get('api_objects'):
            raise_obj_error(
                obj_name,
                'API parent: %s does not reference an API object',
                (api.get('parent')))
        if 'parent_key' not in api:
            raise_obj_error(
                obj_name,
                'parent_key must be present if parent property is present',
                ())
        elif api.get('parent_key') not in obj_val.get('attributes'):
            raise_obj_error(
                obj_name,
                'parent_key contains unkown attribute: %s',
                (api.get('parent_key')))


def verify_model(model):
    valid_versions = ["1.0"]
    # Verify file version is correct
    if 'file_version' not in model:
        raise_format_error('Missing file_version object', ())
    if model['file_version'] not in valid_versions:
        raise_format_error('Invalid file version: %s', (model['file_version']))
    if 'info' not in model:
        raise_format_error('No info object defined', ())
    if 'name' not in model.get('info'):
        raise_format_error('Info object missing name', ())
    # Verify that BasePort, BaseInterface and BaseService have been extended
    if 'api_objects' not in model or len(model['api_objects']) == 0:
        raise_format_error('No API objects are defined', ())
    baseport_found = False
    baseinterface_found = False
    baseservice_found = False
    for obj_name, obj_val in six.iteritems(model['api_objects']):
        if obj_val.get('extends') == 'BasePort':
            if baseport_found:
                raise_format_error(
                    'Only one object can extend BasePort', ())
            baseport_found = True
        if obj_val.get('extends') == 'BaseInterface':
            if baseinterface_found:
                raise_format_error(
                    'Only one object can extend BaseInterface', ())
            baseinterface_found = True
        if obj_val.get('extends') == 'BaseService':
            baseservice_found = True
        if 'attributes' not in obj_val:
            raise_format_error(
                'No attributes specified for object: %s', (obj_name))
        validate_attributes(obj_name, obj_val, model)
        validate_api(obj_name, obj_val, model)
    if not baseport_found:
        raise_format_error(
            'BasePort must be extended by an API object', ())
    if not baseinterface_found:
        raise_format_error(
            'BaseInterface must be extended by an API object', ())
    if not baseservice_found:
        raise_format_error(
            'BaseService must be extended by an API object', ())


def extend_object(obj, obj_dict):
    name = obj.get('extends')
    if name not in obj_dict:
        raise_format_error('extends references unkown object: %s', (name))
    ext_obj = obj_dict.get(name)
    orig_attrs = obj.get('attributes', dict())
    obj['attributes'] = dict()
    orig_policies = obj.get('policies', dict())
    obj['policies'] = dict()
    if 'attributes' in ext_obj:
        for attr_name, attr_val in \
                six.iteritems(ext_obj.get('attributes')):
            if attr_name not in obj['attributes']:
                obj['attributes'].__setitem__(attr_name, attr_val)
            else:
                obj['attributes'][attr_name].update(attr_val)
    for attr_name, attr_val in six.iteritems(orig_attrs):
        if attr_name not in obj['attributes']:
            obj['attributes'].__setitem__(attr_name, attr_val)
        else:
            obj['attributes'][attr_name].update(attr_val)
    if 'policies' in ext_obj:
        for rule_name, rule_val in six.iteritems(ext_obj.get('policies')):
            if rule_name not in obj['policies']:
                obj['policies'].__setitem__(rule_name, rule_val)
            else:
                obj['policies'][rule_name].update(rule_val)
    for rule_name, rule_val in six.iteritems(orig_policies):
        if rule_name not in obj['policies']:
            obj['policies'].__setitem__(rule_name, rule_val)
        else:
            obj['policies'][rule_name].update(rule_val)
    return obj


def proc_object_extensions(dicta, dictb):
    moved_list = list()
    for obj_name, obj_val in six.iteritems(dicta):
        if obj_val.get('extends') in dictb:
            dictb[obj_name] = extend_object(obj_val, dictb)
            moved_list.append(obj_name)
    for obj_name in moved_list:
        dicta.__delitem__(obj_name)
    if len(dicta):
        proc_object_extensions(dicta, dictb)


def extend_base_objects(model):
    # First we move non-extended objects to new list
    for obj_name, obj_val in six.iteritems(model.get('base_objects')):
        if 'extends' in obj_val:
            if obj_val.get('extends') not in model.get('base_objects'):
                raise_format_error('extends references unkown object: %s',
                                   (obj_val.get('extends')))
    new_dict = dict()
    moved_list = list()
    for obj_name, obj_val in six.iteritems(model.get('base_objects')):
        if 'extends' not in obj_val:
            moved_list.append(obj_name)
            new_dict.__setitem__(obj_name, obj_val)
    for obj_name in moved_list:
        model['base_objects'].__delitem__(obj_name)
    proc_object_extensions(model['base_objects'], new_dict)
    model['base_objects'] = new_dict
    return model


def extend_api_objects(model):
    new_dict = dict()
    for obj_name, obj_val in six.iteritems(model.get('api_objects')):
        if 'extends' in obj_val:
            if obj_val.get('extends') not in model.get('base_objects'):
                raise_obj_error(obj_name,
                                'extends references unkown object: %s',
                                (obj_val.get('extends')))
            new_dict[obj_name] = extend_object(obj_val,
                                               model.get('base_objects'))
    model.get('api_objects').update(new_dict)
    return model


def append_model(model, yaml_dict):
    main_objects = ['file_version', 'imports', 'info', 'objects']
    for obj_name in six.iterkeys(yaml_dict):
        if obj_name not in main_objects:
            raise_format_error('Invalid top level object: %s', (obj_name))
    file_version = yaml_dict.get('file_version')
    cur_file_version = model.get('file_version')
    if file_version and cur_file_version:
        if file_version != file_version:
            raise_format_error('File version mismatch %s', (file_version))
        else:
            model['file_version'] = yaml_dict['file_version']
    elif file_version:
        model['file_version'] = file_version
    if 'imports' in yaml_dict:
        model['imports'] = yaml_dict.get('imports')
    if 'info' in yaml_dict:
        model['info'] = yaml_dict.get('info')
    if 'api_objects' not in model:
        model['api_objects'] = dict()
    if 'base_objects' not in model:
        model['base_objects'] = dict()
    for obj_name, obj_val in six.iteritems(yaml_dict.get('objects')):
        if 'api' in obj_val:
            if 'plural_name' not in obj_val['api']:
                obj_val['api']['plural_name'] = \
                    obj_val['api'].get('name', '') + 's'
            model['api_objects'].__setitem__(obj_name, obj_val)
        else:
            model['base_objects'].__setitem__(obj_name, obj_val)


def load_model(package_name, model_dir, model_name):
    model_path = model_dir + "/" + model_name
    model = {}
    for f in pkg_resources.resource_listdir(package_name, model_path):
        f = model_path + '/' + f
        with pkg_resources.resource_stream(package_name, f) as fd:
            append_model(model, yaml.safe_load(fd))
    imports_path = model.get('imports')
    if imports_path:
        f = model_dir + '/' + imports_path
        with pkg_resources.resource_stream(package_name, f) as fd:
            append_model(model, yaml.safe_load(fd))
    extend_base_objects(model)
    extend_api_objects(model)
    return model


# Singleton generator
def load_model_for_service(service):
    if GenData.models.get(service) is None:
        GenData.models[service] = load_model(GenData.package_name,
                                             GenData.model_dir,
                                             service)
    return GenData.models.get(service)


def build_sql_models(service_list):
    from gluon.particleGenerator.DataBaseModelGenerator \
        import DataBaseModelProcessor
    if GenData.DBGeneratorInstance is None:
        GenData.DBGeneratorInstance = DataBaseModelProcessor()
    base = sql_models.Base
    for service in service_list:
        GenData.DBGeneratorInstance.add_model(load_model_for_service(service))
        GenData.DBGeneratorInstance.build_sqla_models(service, base)


def build_api(root, service_list):
    from gluon.particleGenerator.ApiGenerator import APIGenerator
    for service in service_list:
        load_model_for_service(service)
        api_gen = APIGenerator()
        service_root = api_gen.create_controller(service, root)
        api_gen.add_model(load_model_for_service(service))
        api_gen.create_api(service_root, service,
                           GenData.DBGeneratorInstance.get_db_models(service))


def get_db_gen():
    return GenData.DBGeneratorInstance
