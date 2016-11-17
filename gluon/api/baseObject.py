# All Rights Reserved.
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

import datetime

from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from gluon.db import api as dbapi
from gluon.managers.manager_base import get_api_manager


class APIBase(wtypes.Base):

    # TBD
    created_at = wsme.wsattr(datetime.datetime, readonly=True)
    """The time in UTC at which the object is created"""

    # #TBD
    updated_at = wsme.wsattr(datetime.datetime, readonly=True)
    """The time in UTC at which the object is updated"""

    def get_fields(self):
        return [attr.key for attr in self._wsme_attributes]

    def as_dict(self):
        """Render this object as a dict of its fields."""
        fields = self.get_fields()
        return dict((k, getattr(self, k))
                    for k in fields
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)

    def unset_fields_except(self, except_list=None):
        """Unset fields so they don't appear in the message body.

        :param except_list: A list of fields that won't be touched.

        """
        if except_list is None:
            except_list = []
        for k in self.as_dict():
            if k not in except_list:
                setattr(self, k, wsme.Unset)


class APIBaseObject(APIBase):

    @classmethod
    def class_builder(base_cls, name, _db_model, attributes):
        new_cls = type(name, (base_cls,), attributes)
        new_cls.db_model = _db_model
        new_cls.db = dbapi.get_instance()
        return new_cls

    @classmethod
    def build(cls, db_obj):
        obj = cls()
        fields = obj.get_fields()
        db_obj_dict = db_obj.as_dict()
        for field in fields:
            # Skip fields we do not expose.
            if not hasattr(obj, field):
                continue
            setattr(obj, field, db_obj_dict.get(field, wtypes.Unset))
        return obj

    @classmethod
    def get_from_db(cls, key):
        db_obj = cls.db.get_by_primary_key(cls.db_model, key)
        return cls.build(db_obj)

    @classmethod
    def create_in_db(cls, new_values):
        new_values['created_at'] = datetime.datetime.now()
        new_values['updated_at'] = new_values['created_at']
        db_object = cls.db.create(cls.db_model, new_values)
        return cls.build(db_object)

    @classmethod
    def update_in_db(cls, key, new_values):
        new_values['updated_at'] = datetime.datetime.now()
        db_object = cls.db.get_by_primary_key(cls.db_model, key)
        db_object.update(new_values)
        db_object.save()
        return cls.build(db_object)

    @classmethod
    def delete_from_db(cls, key):
        """Delete a Object in the DB."""
        db_object = cls.db.get_by_primary_key(cls.db_model, key)
        db_object.delete()


class APIBaseList(APIBase):

    @classmethod
    def class_builder(base_cls, name, list_name, api_object_class):
        new_cls = type(name, (base_cls,), {list_name: [api_object_class]})
        new_cls.list_name = list_name
        new_cls.api_object_class = api_object_class
        return new_cls

    @classmethod
    def build(cls):
        db = dbapi.get_instance()
        db_obj_list = db.get_list(cls.api_object_class.db_model)
        obj = cls()
        setattr(obj, cls.list_name,
                [cls.api_object_class.build(db_obj)
                 for db_obj in db_obj_list])
        return obj


class RootObjectController(rest.RestController):
    """Root Objects are Objects of the API which  do not have a parent"""

    @classmethod
    def class_builder(base_cls, name, api_obj_class, primary_key_type,
                      api_name):
        new_cls = type(name, (base_cls,), {})
        new_cls.list_object_class = APIBaseList.class_builder(name + 'List',
                                                              name,
                                                              api_obj_class)
        new_cls.api_object_class = api_obj_class
        new_cls.primary_key_type = primary_key_type
        new_cls.api_mgr = get_api_manager(api_name)

        @wsme_pecan.wsexpose(new_cls.list_object_class, template='json')
        def get_all(self):
            return self.list_object_class.build()
        new_cls.get_all = classmethod(get_all)

        @wsme_pecan.wsexpose(new_cls.api_object_class,
                             new_cls.primary_key_type,
                             template='json')
        def get_one(self, key):
            return self.api_object_class.get_from_db(key)
        new_cls.get_one = classmethod(get_one)

        @wsme_pecan.wsexpose(new_cls.api_object_class,
                             body=new_cls.api_object_class, template='json',
                             status_code=201)
        def post(self, body):
            return self.api_mgr.handle_create(self, body.as_dict())
        new_cls.post = classmethod(post)

        @wsme_pecan.wsexpose(new_cls.api_object_class,
                             new_cls.primary_key_type,
                             body=new_cls.api_object_class, template='json')
        def put(self, key, body):
            return self.api_mgr.handle_update(self, key, body.as_dict())
        new_cls.put = classmethod(put)

        @wsme_pecan.wsexpose(None, new_cls.primary_key_type, template='json')
        def delete(self, key):
            return self.api_mgr.handle_delete(self, key)
        new_cls.delete = classmethod(delete)

        return new_cls

# TODO(hambtw)  Needs to be reworked
# class SubObjectController(RootObjectController):
#
#     @classmethod
#     def class_builder(base_cls, name, object_class, primary_key_type,
#                       parent_identifier_type,
#                       parent_attribute_name):
#         new_cls = super(SubObjectController, base_cls).class_builder(
#             name, object_class, primary_key_type)
#         new_cls._parent_id_type = parent_identifier_type
#         new_cls._parent_attribute_name = parent_attribute_name
#
#         @wsme_pecan.wsexpose(new_cls._list_object_class,
#                              new_cls.parent_id_type,
#                              template='json')
#         def get_all(self, _parent_identifier):
#             filters = {self._parent_attribute_name: _parent_identifier}
#             return self._list_object_class.build(
#                 self._list_object_class.get_object_class().list(
#                     filters=filters))
#         new_cls.get_all = classmethod(get_all)
#
#         @wsme_pecan.wsexpose(new_cls.api_object_class,
#                              new_cls._parent_identifier_type,
#                              new_cls.primary_key_type,
#                              template='json')
#         def get_one(self, parent_identifier, key):
#             filters = {self._parent_attribute_name: parent_identifier}
#             return self.api_object_class.build(
#                 self.api_object_class.get_object_class(
#                 ).get_by_primary_key(key, filters))
#         new_cls.get_one = classmethod(get_one)
#
#         @wsme_pecan.wsexpose(new_cls.api_object_class,
#                              new_cls._parent_id_type,
#                              body=new_cls.api_object_class, template='json',
#                              status_code=201)
#         def post(self, parent_identifier, body):
#             call_func = getattr(get_api_manager(),
#                                 'create_%s' % self.__name__,
#                                 None)
#             if not call_func:
#                 raise Exception('create_%s is not implemented' %
#                                 self.__name__)
#             return self.api_object_class.build(call_func(
#                                                parent_identifier,
#                                                body.to_db_object()))
#         new_cls.post = classmethod(post)
#
#         return new_cls
