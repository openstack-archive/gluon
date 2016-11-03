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

import abc
import six

from oslo_config import cfg
from oslo_db import api as db_api
_BACKEND_MAPPING = {'sqlalchemy': 'gluon.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


def get_models():
    return IMPL.models


@six.add_metaclass(abc.ABCMeta)
class Connection(object):

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def create(self, model, values):
        """Create a new Gluon object from model.

        :param model: Class of the object which should be created
        :param values: A dict containing several items used to identify
                       and track the port, and several dicts which are passed
                       into the Drivers when managing this port. For example:

                       ::

                        {
                         'uuid': utils.generate_uuid(),
                         'result': 'pass'
                        }
        :returns: A port.
        """

    @abc.abstractmethod
    def get_list(self, model, columns=None, filters=None, limit=None,
                 marker=None, sort_key=None, sort_dir=None,
                 failed=None, period=None):
        """Get specific columns for matching model.

        Return a list of the specified columns for all tess that match the
        specified filters.

        :param model: Class of the object which should be listed
        :param columns: List of column names to return.
                        Defaults to 'id' column when columns == None.
        :param filters: Filters to apply. Defaults to None.

        :param limit: Maximum number of tests to return.
        :param marker: the last item of the previous page; we return the next
                       result set.
        :param sort_key: Attribute by which results should be sorted.
        :param sort_dir: direction in which results should be sorted.
                         (asc, desc)
        :returns: A list of tuples of the specified columns.
        """

    @abc.abstractmethod
    def get_by_uuid(self, model, uuid):
        """Return an object of model.

        :param uuid: The uuid of a object.
        :returns: an object of model.
        """
