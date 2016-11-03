# coding: utf-8
#
# Copyright 2015, Ericsson AB
# Copyright 2013 Red Hat, Inc.
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

import six
import wsme
from wsme import types as wtypes

from gluon.common import exception
from oslo_log._i18n import _
from oslo_utils import strutils
from oslo_utils import uuidutils


class DynamicDict(wtypes.DynamicBase):
    pass


class DynamicList(wtypes.DynamicBase):
    pass


class NameType(wtypes.UserType):
    """A logical name type."""

    basetype = wtypes.text
    name = 'name'

    @staticmethod
    def validate(value):
        if not value:
            raise exception.InvalidName(name=value)
        return value

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return NameType.validate(value)


class UuidType(wtypes.UserType):
    """A simple UUID type."""

    basetype = wtypes.text
    name = 'uuid'

    @staticmethod
    def validate(value):
        if value == '':
            value = wtypes.Unset
            return value
        if not uuidutils.is_uuid_like(value):
            raise exception.InvalidUUID(uuid=value)
        return value

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return UuidType.validate(value)


class BooleanType(wtypes.UserType):
    """A simple boolean type."""

    basetype = wtypes.text
    name = 'boolean'

    @staticmethod
    def validate(value):
        try:
            return strutils.bool_from_string(value, strict=True)
        except ValueError as e:
            # raise Invalid to return 400 (BadRequest) in the API
            raise exception.Invalid(e)

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return BooleanType.validate(value)


class MultiType(wtypes.UserType):
    """A complex type that represents one or more types.

    Used for validating that a value is an instance of one of the types.

    :param types: Variable-length list of types.

    """
    basetype = wtypes.text

    def __init__(self, *types):
        self.types = types

    def __str__(self):
        return ' | '.join(map(str, self.types))

    def validate(self, value):
        for t in self.types:
            try:
                return wtypes.validate_value(t, value)
            except (exception.InvalidUUID, ValueError):
                pass
        else:
            raise ValueError(_("Expected '%(type)s', got '%(value)s'")
                             % {'type': self.types, 'value': type(value)})


class Text(wtypes.UserType):
    basetype = six.text_type
    name = 'text'

    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types):
            return
        raise ValueError(_("Expected String, got '%s'") % value)


def create_enum_type(*values):
    unicode_values = []
    for v in values:
        # Python 2/3 compatible way to convert to unicode
        if hasattr(v, 'decode'):  # Python 2
            v = v.decode('ascii')
        unicode_values.append(v)
    return wtypes.Enum(wtypes.text, *unicode_values)

int_type = wtypes.IntegerType()
uuid = UuidType()
name = NameType()
uuid_or_name = MultiType(UuidType, NameType)
boolean = BooleanType()
