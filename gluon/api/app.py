#    Copyright 2016, Ericsson AB
#    Copyright 2017, Nokia
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

from keystonemiddleware import auth_token
import pecan

from oslo_config import cfg
from oslo_log import log as logging
from oslo_middleware import cors
from oslo_middleware import http_proxy_to_wsgi
from oslo_middleware import request_id

from gluon.api import hooks
from gluon.common import exception as g_exc


# TODO(enikher)
# from gluon.api import middleware

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

app_dic = {'root': 'gluon.api.root.RootController',
           'modules': ['gluon.api'],
           'debug': True,
           # TODO(enikher) HOOKS
           # 'hooks': [
           #    hooks.ContextHook(),
           #    hooks.RPCHook(),
           #    hooks.NoExceptionTracebackHook(),
           #  ],
           'acl_public_routes': ['/']}


def setup_app(config=None):
    app_hooks = [
        hooks.ContextHook(),
        hooks.PolicyHook()
    ]

    app = pecan.make_app(
        app_dic.pop('root'),
        logging=getattr(config, 'logging', {}),
        wrap_app=_wrap_app,
        hooks=app_hooks,
        # TODO(enikher)
        # wrap_app=middleware.ParsableErrorMiddleware,
        **app_dic
    )

    # TODO(enikher) test hook later
    # timer(30, timerfunc, "Cpulse")
    # tm = Periodic_TestManager()
    # tm.start()

    # TODO(enikher) add authentication
    # return auth.install(app, CONF, config.app.acl_public_routes)
    return app


# adapted from Neutron code
def _wrap_app(app):
    app = request_id.RequestId(app)

    if CONF.api.auth_strategy == 'noauth':
        pass
    elif CONF.api.auth_strategy == 'keystone':
        app = auth_token.AuthProtocol(app, {})
        LOG.info("Keystone authentication is enabled")
    else:
        raise g_exc.InvalidConfigurationOption(
            opt_name='auth_strategy', opt_value=CONF.auth_strategy)

    # dont bother authenticating version
    # app = versions.Versions(app)

    # gluon server is behind the proxy
    app = http_proxy_to_wsgi.HTTPProxyToWSGI(app)

    # This should be the last middleware in the list (which results in
    # it being the first in the middleware chain). This is to ensure
    # that any errors thrown by other middleware, such as an auth
    # middleware - are annotated with CORS headers, and thus accessible
    # by the browser.
    app = cors.CORS(app, CONF)
    app.set_latent(
        allow_headers=['X-Auth-Token', 'X-Identity-Status', 'X-Roles',
                       'X-Service-Catalog', 'X-User-Id', 'X-Tenant-Id',
                       'X-OpenStack-Request-ID',
                       'X-Trace-Info', 'X-Trace-HMAC'],
        allow_methods=['GET', 'PUT', 'POST', 'DELETE', 'PATCH'],
        expose_headers=['X-Auth-Token', 'X-Subject-Token', 'X-Service-Token',
                        'X-OpenStack-Request-ID',
                        'X-Trace-Info', 'X-Trace-HMAC']
    )

    return app
