# Copyright 2015, Ericsson AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Gluon base exception handling.

Includes decorator for re-raising Cloudpulse-type exceptions.

"""

import six

from oslo_config import cfg

from oslo_log import log as logging

from oslo_log._i18n import _
from oslo_log._i18n import _LE

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class GluonException(Exception):
    """Base Gluon Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if message:
            self.message = message

        try:
            self.message = self.message % kwargs
        except Exception as e:
            # kwargs doesn't match a variable in the message
            # log the issue and the kwargs
            LOG.exception(_LE('Exception in string format operation'))
            for name, value in six.iteritems(kwargs):
                LOG.error(_LE("%(name)s: %(value)s") %
                          {'name': name, 'value': value})
            try:
                if CONF.fatal_exception_format_errors:
                    raise e
            except cfg.NoSuchOptError:
                # Note: work around for Bug: #1447873
                if CONF.oslo_versionedobjects.fatal_exception_format_errors:
                    raise e

        super(GluonException, self).__init__(self.message)

    def __str__(self):
        if six.PY3:
            return self.message
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)


class Conflict(GluonException):
    message = _('Conflict.')
    code = 409


class AlreadyExists(Conflict):
    message = _("Object of %(cls)s with %(key)s \"%(value)s\" already exists.")


class NotFound(GluonException):
    code = 404
    message = _("Object of %(cls)s with Primay Key %(key)s not found.")


class BackendDoesNotExsist(GluonException):
    code = 409
    message = _("Backend with name %(name)s does not exsist.")


class GluonClientException(GluonException):
    """Base exception which exceptions from Gluon are mapped into.

    NOTE: on the client side, we use different exception types in order
    to allow client library users to handle server exceptions in try...except
    blocks. The actual error message is the one generated on the server side.
    """

    status_code = 0

    def __init__(self, message=None, **kwargs):
        if 'status_code' in kwargs:
            self.status_code = kwargs['status_code']
        super(GluonClientException, self).__init__(message, **kwargs)


class EndpointNotFound(GluonClientException):
    message = _("Could not find Service or Region in Service Catalog.")


class EndpointTypeNotFound(GluonClientException):
    message = _("Could not find endpoint type %(type_)s in Service Catalog.")


class AmbiguousEndpoints(GluonClientException):
    message = _("Found more than one matching endpoint in Service Catalog: "
                "%(matching_endpoints)")


class RequestURITooLong(GluonClientException):
    """Raised when a request fails with HTTP error 414."""

    def __init__(self, **kwargs):
        self.excess = kwargs.get('excess', 0)
        super(RequestURITooLong, self).__init__(**kwargs)


class ConnectionFailed(GluonClientException):
    message = _("Connection to Gluon failed: %(reason)s")


class SslCertificateValidationError(GluonClientException):
    message = _("SSL certificate validation has failed: %(reason)s")


class MalformedResponseBody(GluonClientException):
    message = _("Malformed response body: %(reason)s")


class InvalidContentType(GluonClientException):
    message = _("Invalid content type %(content_type)s.")


class InvalidConfigurationOption(GluonClientException):
    """An error due to an invalid configuration option value."""

    message = _("An invalid value for configuration option %(opt_name): "
                "%(opt_value)")


class PolicyInitError(GluonClientException):
    """An error due to policy initialization failure."""

    message = _("Failed to initialize policy %(policy)s because %(reason)s.")


class PolicyCheckError(GluonClientException):
    """An error due to a policy check failure."""

    message = _("Failed to check policy %(policy)s because %(reason)s.")


class InvalidFileFormat(GluonClientException):
    """An error due to a invalid API specification file."""
    message = _("Invalid file format")
