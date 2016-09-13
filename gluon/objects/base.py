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

from oslo_versionedobjects import exception
from oslo_versionedobjects import base as ovoo_base
from pecan import Response
from oslo_log._i18n import _LI
from gluon.db import api as dbapi
from oslo_log import log as logging
from gluon.common import exception

LOG = logging.getLogger(__name__)


class GluonObject(ovoo_base.VersionedObject, ovoo_base.VersionedObjectDictCompat):
    """Base class and object factory.
    """

    VERSION = '1.0'

    db_instance = dbapi.get_instance()

    @classmethod
    def class_builder(base_cls, name, db_model, fields):
        new_cls = type(name, (base_cls,), {'fields': fields})
        new_cls.db_model = db_model
        ovoo_base.VersionedObjectRegistry.register(new_cls)
        return new_cls

    def as_dict(self):
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k))

    @staticmethod
    def as_list(db_obj_list):
        return [obj.as_dict() for obj in db_obj_list]

    @classmethod
    def list(cls, limit=None, marker=None, sort_key=None,
             sort_dir=None, filters=None, failed=None, period=None):
        db_list = cls.db_instance.get_list(cls.db_model,
                                           filters=filters,
                                           limit=limit, marker=marker,
                                           sort_key=sort_key,
                                           sort_dir=sort_dir,
                                           failed=failed,
                                           period=period)
        return cls._from_db_object_list(cls, db_list)

    @classmethod
    def get_by_filter(cls, filter):
        return cls.list(filters=filter)

    @classmethod
    def get_by_primary_key(cls, key):
        filter = {}
        pk_type = cls.db_model.get_primary_key_type()
        filter[pk_type] = key
        obj = cls.get_by_filter(filter)
        if obj:
            return obj[0]
        else:
            raise exception.NotFound(cls=cls.db_model.__name__, key=key)

    @classmethod
    def get_by_parent_and_primary_key(self, parent_identifier,
                                      key):
        pk_type = cls.db_model.get_primary_key_type()
        pk_type = cls.db_model.get_primary_key_type()

    @classmethod
    def get_by_uuid(cls, uuid):
        obj = cls.get_by_filter({'uuid': uuid})
        if obj:
            return obj[0]
        else:
            raise exception.NotFound(cls=cls.db_model.__name__, key=uuid)

    @classmethod
    def get_by_id(cls, uuid):
        obj = cls.get_by_filter({'id': uuid})
        if obj:
            return obj[0]
        else:
            raise exception.NotFound(cls=cls.db_model.__name__, key=uuid)

    @classmethod
    def get_by_name(cls, name):
        return cls.get_by_filter({'name': name})

    @staticmethod
    def from_dict_object(cls, dict):
        """Converts a database entity to a formal object."""
        for field in cls.fields:
            if dict[field] is not None:
                cls[field] = dict[field]

        cls.obj_reset_changes()
        return cls

    @staticmethod
    def _from_db_object_list(cls, db_objects):
        return [cls.from_dict_object(cls(), obj) for obj in db_objects]

    def create(self):
        """Create a Object in the DB.
        """
        values = self.obj_get_changes()
        LOG.info(_LI('Dumping CREATE port datastructure  %s') % str(values))
        db_object = self.db_instance.create(self.db_model, values)
        self.from_dict_object(self, db_object)

    @classmethod
    def update(cls, key, values):
        """Delete a Object in the DB.
        """
        db_object = cls.db_instance.get_by_primary_key(cls.db_model, key)
        db_object.update(values)
        db_object.save()
        return cls.from_dict_object(cls(), db_object)

    @classmethod
    def delete(cls, key):
        """Delete a Object in the DB.
        """
        db_object = cls.db_instance.get_by_primary_key(cls.db_model, key)
        db_object.delete()





