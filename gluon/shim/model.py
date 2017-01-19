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

import collections


class ChangeData(object):
    def __init__(self):
        self.new = dict()
        self.prev = dict()

    def __str__(self):
        """returns simple dict representation of the mapping"""
        return "new = " + str(self.new) + ", prev = " + str(self.prev)


class ObjBase(collections.MutableMapping):
    """Base object mapping

       Mapping that works like both a dict and a mutable object, i.e.
        d = ObjBase(foo='bar')
       and
        d.foo returns 'bar'
    """
    # ``__init__`` method required to create instance from class.
    def __init__(self, attributes=None):
        """Use the object dict"""
        if attributes is not None:
            self.__dict__.update(attributes)
    # The next five methods are requirements of the ABC.

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        """returns simple dict representation of the mapping"""
        return str(self.__dict__)

    def __repr__(self):
        """echoes class, id, & reproducible representation in the REPL"""
        return '{}, {}'.format(super(ObjBase, self).__repr__(), self.__dict__)

    def update_attrs(self, new_attributes):
        changes = ChangeData()
        for key in new_attributes:
            if key in self.__dict__:
                if new_attributes[key] != self.__dict__[key]:
                    changes.prev[key] = self.__dict__[key]
                    self.__dict__[key] = new_attributes[key]
                    changes.new[key] = new_attributes[key]
            else:
                self.__dict__[key] = new_attributes[key]
                changes.new[key] = new_attributes[key]
        return changes


class Port(ObjBase):

    def __init__(self, id, attributes=None):
        super(self.__class__, self).__init__(attributes)
        self.__dict__["__id"] = id
        self.__dict__["__state"] = "Unbound"   # "Unbound", "Bound", "InUse"


class DataObj(ObjBase):

    def __init__(self, id, attributes=None):
        super(self.__class__, self).__init__(attributes)
        self.__dict__["__id"] = id


class Model(object):

    def __init__(self):
        self.ports = dict()      # Port objects
        self.interfaces = dict()
