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


import pecan
# TODO enikher
# from gluon.api import middleware

app_dic = {
           'root': 'gluon.api.root.RootController',
           'modules': ['gluon.api'],
           'debug': True,
# TODO (enikher) HOOKS
#    'hooks': [
#        hooks.ContextHook(),
#        hooks.RPCHook(),
#        hooks.NoExceptionTracebackHook(),
#    ],
        'acl_public_routes': [
                              '/'
                              ],
}


def setup_app(config=None):

    app = pecan.make_app(
        app_dic.pop('root'),
        logging=getattr(config, 'logging', {}),
        # TODO (enikher)
        # wrap_app=middleware.ParsableErrorMiddleware,
        **app_dic
    )

#   TODO test hook later
    # timer(30, timerfunc, "Cpulse")
    # tm = Periodic_TestManager()
    # tm.start()
    # TODO add authentication
    # return auth.install(app, CONF, config.app.acl_public_routes)
    return app
