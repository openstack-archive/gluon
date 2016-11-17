# Copyright (c) 2015 Cisco Systems, Inc.
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

import pkg_resources
import yaml

from gluon.db.sqlalchemy import models as sql_models

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class MyData(object):
    pass

GenData = MyData()
GenData.DBGeneratorInstance = None
GenData.models = dict()
GenData.package_name = "gluon"
GenData.model_dir = "models/proton"


# Singleton generator
def load_model(service):
    if GenData.models.get(service) is None:
        model_dir = GenData.model_dir + "/" + service
        GenData.models[service] = {}
        for f in pkg_resources.resource_listdir(
                GenData.package_name, model_dir):
            f = model_dir + "/" + f
            with pkg_resources.resource_stream(GenData.package_name, f) as fd:
                GenData.models[service].update(yaml.safe_load(fd))
    return GenData.models.get(service)


def build_sql_models(service_list):
    from gluon.particleGenerator.DataBaseModelGenerator \
        import DataBaseModelProcessor
    if GenData.DBGeneratorInstance is None:
        GenData.DBGeneratorInstance = DataBaseModelProcessor()
    base = sql_models.Base
    for service in service_list:
        GenData.DBGeneratorInstance.add_model(load_model(service))
        GenData.DBGeneratorInstance.build_sqla_models(service, base)


def build_api(root, service_list):
    from gluon.particleGenerator.ApiGenerator import APIGenerator
    for service in service_list:
        load_model(service)
        api_gen = APIGenerator()
        service_root = api_gen.create_controller(service, root)
        api_gen.add_model(load_model(service))
        api_gen.create_api(service_root, service,
                           GenData.DBGeneratorInstance.get_db_models(service))


def get_db_gen():
    return GenData.DBGeneratorInstance
