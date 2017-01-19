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

import dateutil.parser
import json
import netaddr
import re
from rfc3986 import is_valid_uri
import six
from wsme import types as wtypes

from oslo_log._i18n import _
from oslo_utils import strutils


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
            raise ValueError(value)
        return value

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return NameType.validate(value)


class UuidType(wtypes.UuidType):
    """A simple UUID type."""

    basetype = wtypes.text
    name = 'uuid'

    @staticmethod
    def validate(value):
        if value == '':
            return value
        if wtypes.UuidType.validate(value):
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
        except ValueError:
            # raise Invalid to return 400 (BadRequest) in the API
            raise ValueError("Invalid boolean value: %s" % value)

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return BooleanType.validate(value)


class FloatType(wtypes.UserType):
    """A simple float type. """

    basetype = float
    name = "float"

    def __init__(self):
        pass

    @staticmethod
    def frombasetype(value):
        return float(value) if value is not None else None

    def validate(self, value):
        try:
            float(value)
            return value
        except Exception:
            error = 'Invalid float value: %s' % value
            raise ValueError(error)


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
            except ValueError:
                pass
        else:
            raise ValueError(_("Expected '%(type)s', got '%(value)s'")
                             % {'type': self.types, 'value': type(value)})


class Text(wtypes.UserType):
    basetype = six.text_type
    name = 'text'

    #    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types):
            return value
        raise ValueError(_("Expected String, got '%s'") % value)


class DateTime(wtypes.UserType):
    basetype = six.text_type
    name = 'date-time'

    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types):
            try:
                dateutil.parser.parse(value)
                return value
            except Exception:
                raise ValueError(_("Invalid Date string: '%s'") % value)
            return value
        raise ValueError(_("Expected String, got '%s'") % value)


class JsonString(wtypes.UserType):
    basetype = six.text_type
    name = 'json-string'

    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types):
            try:
                if len(value) > 0:
                    json.loads(value)
                return value
            except Exception:
                raise ValueError(_("String not in JSON format: '%s'") % value)
        raise ValueError(_("Expected String, got '%s'") % value)


class Ipv4String(wtypes.UserType):
    basetype = six.text_type
    name = 'ipv4-string'

    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types) and netaddr.valid_ipv4(value):
            return value
        raise ValueError(_("Expected IPv4 string, got '%s'") % value)


class Ipv6String(wtypes.UserType):
    basetype = six.text_type
    name = 'ipv6-string'

    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types) and netaddr.valid_ipv6(value):
            return value
        raise ValueError(_("Expected IPv6  String, got '%s'") % value)


class MacString(wtypes.UserType):
    basetype = six.text_type
    name = 'mac-string'

    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types) and netaddr.valid_mac(value):
            return value
        raise ValueError(_("Expected MAC String, got '%s'") % value)


class UriString(wtypes.UserType):
    basetype = six.text_type
    name = 'uri-string'

    @staticmethod
    def validate(value):
        if isinstance(value, six.string_types):
            try:
                if is_valid_uri(value):
                    return value
                else:
                    raise ValueError(_("Not valid URI format: '%s'") % value)
            except Exception:
                raise ValueError(_("Not valid URI format: '%s'") % value)
        raise ValueError(_("Expected String, got '%s'") % value)


class EmailString(wtypes.UserType):
    basetype = six.text_type
    name = 'email-string'
    regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    def validate(self, value):
        if isinstance(value, six.string_types) and re.match(self.regex, value):
            return value
        raise ValueError(_("Expected Email String, got '%s'") % value)


def create_enum_type(*values):
    unicode_values = []
    for v in values:
        # Python 2/3 compatible way to convert to unicode
        if hasattr(v, 'decode'):  # Python 2
            v = v.decode('ascii')
        unicode_values.append(v)
    return wtypes.Enum(wtypes.text, *unicode_values)


int_type = wtypes.IntegerType
float_type = FloatType()
uuid = UuidType()
name = NameType()
uuid_or_name = MultiType(UuidType, NameType)
boolean = BooleanType()
datetime_type = DateTime()
json_type = JsonString()
ipv4_type = Ipv4String()
ipv6_type = Ipv6String()
mac_type = MacString()
uri_type = UriString()
email_type = EmailString()
