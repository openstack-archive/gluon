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
import sqlalchemy.orm.exc

from gluon.common import exception
from gluon.db import api
from gluon.db.sqlalchemy import models as sql_models
from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log as logging


CONF = cfg.CONF

_FACADE = None

LOG = logging.getLogger(__name__)


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = [model.get_primary_key()]
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    query = db_utils.paginate_query(query, model, limit, sort_keys,
                                    marker=marker, sort_dir=sort_dir)
    return query.all()


class Connection(api.Connection):
    """SqlAlchemy connection."""

    # TODO(name): this should not be done!!! a database should be
    # created and then migration should be triggered.
    LOG.error("models.Base.metadata.create_all(get_engine()) is still called"
              " this should not be done - migration should be triggered")
    sql_models.Base.metadata.create_all(get_engine())

    models = sql_models

    def __init__(self):
        pass

    def create(self, model, values):
        obj = model()
        obj.update(values)
        try:
            obj.save()
        except db_exc.DBDuplicateEntry as e:
            raise exception.AlreadyExists(
                key=e.__dict__['columns'][0],
                value=values[e.__dict__['columns'][0]],
                cls=model.__name__)
        return obj

    def _add_filters(self, query, filters):
        if filters is None:
            filters = {}
        for (key, value) in six.iteritems(filters):
            query = query.filter_by(**{key: value})

        return query

    def get_list(self, model, columns=None, filters=None, limit=None,
                 marker=None, sort_key=None, sort_dir=None, failed=None,
                 period=None):
        query = model_query(model)
        query = self._add_filters(query, filters)
        # query = self._add_period_filter(query, period)
        # query = self._add_failed_filter(query, failed)
        return _paginate_query(model, limit, marker,
                               sort_key, sort_dir, query)

    def get_by_uuid(self, model, uuid):
        query = model_query(model)
        query = query.filter_by(uuid=uuid)
        try:
            return query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.NotFound(cls=model.__name__, key=uuid)

    def get_by_primary_key(self, model, key):
        pk_type = model.get_primary_key()
        query = model_query(model)
        filter = {pk_type: key}
        query = query.filter_by(**filter)
        try:
            return query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.NotFound(cls=model.__name__, key=key)
