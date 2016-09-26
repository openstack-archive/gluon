#    Copyright 2015, Ericsson AB
#    Copyright 2013 - Red Hat, Inc.
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
import sys
from wsgiref import simple_server

from gluon.api import app as api_app
from gluon.common import service
from gluon.common.particleGenerator.generator import set_package
from gluon.common.particleGenerator import generator as particle_generator
from gluon.core.manager import register_api_manager
import gluon.cmd.config
from gluon.cmd.manager import ProtonManager
from gluon.db.sqlalchemy import models as sql_models
from gluon.sync_etcd.thread import start_sync_thread
from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _LI


LOG = logging.getLogger(__name__)
#
# Set the package name before class generation.
# The generator will look in the models directory of the package for the yaml files.
#
#
# Register API Manager for this service.
# Loading these modules will trigger the generation of the API and DB classes
#


def main():
    service.prepare_service(sys.argv)
    # Set source of model files
    set_package("gluon", "models/proton/net-l3vpn")
    LOG.info("Generating DB Classes")
    particle_generator.build_sql_models(sql_models.Base)
    register_api_manager(ProtonManager())
    # API is generated during the setup_app phase.
    LOG.info("Generating API Classes")
    app = api_app.setup_app()

    # Create the WSGI server and start it
    host, port = cfg.CONF.api.host, cfg.CONF.api.port
    srv = simple_server.make_server(host, port, app)

    LOG.info(_LI('Starting server in PID %s') % os.getpid())
    LOG.debug("Configuration:")
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)

    if host == '0.0.0.0':
        LOG.info(_LI('serving on 0.0.0.0:%(port)s, '
                     'view at http://127.0.0.1:%(port)s') %
                 dict(port=port))
    else:
        LOG.info(_LI('serving on http://%(host)s:%(port)s') %
                 dict(host=host, port=port))
    start_sync_thread(service_name=cfg.CONF.api.service_name,
                      etcd_host=cfg.CONF.api.etcd_host,
                      etcd_port=cfg.CONF.api.etcd_port)
    srv.serve_forever()
