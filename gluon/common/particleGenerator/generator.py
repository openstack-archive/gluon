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

import os
import pkg_resources
import yaml

from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _LI


LOG = logging.getLogger(__name__)

class MyData:
    pass

GenData = MyData()
GenData.DataBaseModelGeneratorInstance = None
GenData.APIGeneratorInstance = None
GenData.model = None
GenData.package_name = "gluon"
GenData.model_dir = "models/proton/net-l3vpn"


def set_package(package, dir):
    GenData.package_name = package
    GenData.model_dir = dir


# Singleton generator
def load_model():
    if not GenData.model:
        GenData.model = {}
        for f in pkg_resources.resource_listdir(GenData.package_name, GenData.model_dir):
            f = GenData.model_dir + "/" + f
            with pkg_resources.resource_stream(GenData.package_name, f) as fd:
                GenData.model.update(yaml.safe_load(fd))


def build_sql_models(base):
    from gluon.common.particleGenerator.DataBaseModelGenerator import DataBaseModelProcessor
    load_model()
    if not GenData.DataBaseModelGeneratorInstance:
        GenData.DataBaseModelGeneratorInstance = DataBaseModelProcessor()
        GenData.DataBaseModelGeneratorInstance.add_model(GenData.model)
        GenData.DataBaseModelGeneratorInstance.build_sqla_models(base)


def build_api(root):
    from gluon.common.particleGenerator.ApiGenerator import APIGenerator
    if not GenData.DataBaseModelGeneratorInstance:
        LOG.error("Database must be generated before API!!")
        return
    load_model()
    if not GenData.APIGeneratorInstance:
        GenData.APIGeneratorInstance = APIGenerator(GenData.DataBaseModelGeneratorInstance.db_models)
        GenData.APIGeneratorInstance.add_model(GenData.model)
        GenData.APIGeneratorInstance.create_api(root)


def get_db_gen():
    return GenData.DataBaseModelGeneratorInstance
