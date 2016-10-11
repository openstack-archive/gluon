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

import six
import sys
import yaml

from gluon.api import types
from gluon.api.baseObject import APIBaseObject
from gluon.api.baseObject import RootObjectController
from gluon.api.baseObject import SubObjectController
from gluon.common.particleGenerator.DataBaseModelGenerator import DataBaseModelProcessor
from gluon.core.manager import get_api_manager
from gluon.objects import base as obj_base
from oslo_versionedobjects import fields


class APIGenerator(object):

    def __init__(self, db_models):
        self.db_models = db_models
        self.objects = []

    def add_model(self, model):
        self.data = model

    def create_api(self, root):
        controllers = {}
        if not self.data:
            raise Exception('Cannot create API from empty model.')
        for table_name, table_data in six.iteritems(self.data):
            try:
                # For every entry build a (sub_)api_controller
                # an APIObject, an APIObject and an APIListObject
                # and a RealObject is created
                real_object_fields = {}
                api_object_fields = {}
                for attribute, attr_value in\
                        six.iteritems(table_data['attributes']):
                    api_type = self.translate_model_to_api_type(
                        attr_value['type'], attr_value.get('values'))
                    api_object_fields[attribute] = api_type
                    real_object_fields[attribute] = self.translate_model_to_real_obj_type(
                        attr_value['type'], attr_value.get('values'))

                # Real object
                object_class = obj_base.GluonObject.class_builder(
                    table_name, self.db_models[table_name], real_object_fields)

                # register in the API Manager instance
                get_api_manager().gluon_objects[table_name] = object_class

                # API object
                api_object_class = APIBaseObject.class_builder(
                    table_name, object_class, api_object_fields)

                # api_name
                api_name = table_data['api']['name']

                # primary_key_type
                primary_key_type = self.translate_model_to_api_type(
                    self.get_primary_key_type(table_data), None)

                # parent_identifier_type
                parent = table_data['api']['parent']['type']
                if parent != 'root':
                    parent_identifier_type = self.data[parent]['api']['name']
                    parent_attribute_name =\
                        table_data['api']['parent']['attribute']
                    new_controller_class = SubObjectController.class_builder(
                        api_name, api_object_class, primary_key_type,
                        parent_identifier_type, parent_attribute_name)
                else:
                    new_controller_class = RootObjectController.class_builder(
                        api_name, api_object_class, primary_key_type)

                # The childs have to be instantized before the
                # parents so lets make a dict
                if parent != 'root':
                    if 'childs' not in controllers.get(parent_attribute_name, {}):
                        self.data[parent]['childs'] = []
                    self.data[parent]['childs'].append(
                        {'name': api_name,
                         'object': new_controller_class})
                controllers[table_name] = new_controller_class
            except:
                print('During processing of table ' + table_name)
                raise

        # Now add all childs since the roots are there now
        # And init the controller since all childs are there now
        for table_name, table_data in six.iteritems(self.data):
            controller = controllers[table_name]
            for child in table_data.get('childs', []):
                setattr(controller, child['name'], child['object']())
            api_name = table_data['api']['name']
            setattr(root, api_name, controller())

    def get_primary_key_type(self, table_data):
        primary_key = DataBaseModelProcessor.get_primary_key(
            table_data)
        return table_data['attributes'][primary_key]['type']

    def translate_model_to_real_obj_type(self, model_type, values):
        # first make sure it is not a foreign key
        if model_type in self.data:
            # if it is we point to the primary key type type of this key
            model_type = self.get_primary_key_type(
                self.data[model_type])

        if model_type == 'uuid':
            return fields.UUIDField(nullable=False)
        if model_type == 'string':
            return fields.StringField()
        if model_type == 'enum':
            return fields.EnumField(values)
        if model_type == 'integer':
            return fields.IntegerField()
        if model_type == 'boolean':
            return fields.BooleanField()
        raise Exception("Type %s not known." % model_type)

    def translate_model_to_api_type(self, model_type, values):
        # first make sure it is not a foreign key
        if model_type in self.data:
            # if it is we point to the primary key type type of this key
            model_type = self.get_primary_key_type(
                self.data[model_type])

        if model_type == 'uuid':
            return types.uuid
        if model_type == 'string':
            return unicode
        if model_type == 'enum':
            return types.create_enum_type(*values)
        if model_type == 'integer':
            return types.int_type
        if model_type == 'boolean':
            return types.boolean
        raise Exception("Type %s not known." % model_type)
