#    Copyright 2016, Ericsson AB
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
from gluon.common import exception
from oslo_log import log as logging
from gluon.backends import backend_base as BackendBase
# This has to be dne to get the Database Models
# build before the API is build.
# It should be done in a better way.
from gluon.db.sqlalchemy import models

LOG = logging.getLogger(__name__)
logger = LOG

class MyData:
    pass

ManagerData = MyData()
ManagerData.manager = None

#
# Base class for ApiManager
#
class ApiManager(object):

    def __init__(self):
        # TODO
        # backend_manager = BackendBase.Manager(app.config)
        self.gluon_objects = {}

    def get_gluon_object(self, name):
        return self.gluon_objects[name]


def register_api_manager(manager):
    """
    Each service should create a subclass from manager to handle the routing from the API.
    This manager should be registered before
    :param manager:
    """
    ManagerData.manager = manager

def get_api_manager():
    """
    Return registered API Manager instance
    :return:
    """
    if ManagerData.manager is None:
        LOG.error("No manager registered!")
    return ManagerData.manager