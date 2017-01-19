#   Copyright 2016 Nokia
#   All Rights Reserved.
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

import webob

from oslo_config import cfg
from oslo_policy import policy as oslo_policy
from oslo_utils import excutils
from pecan import hooks

from gluon import constants as gluon_constants
from gluon import policy

from gluon._i18n import _


class PolicyHook(hooks.PecanHook):
    priority = 100

    def before(self, state):

        if cfg.CONF.api.auth_strategy == 'noauth':
            return

        if state.request.method not in ('GET', 'POST', 'PUT', 'DELETE'):
            return

        method = gluon_constants.ACTION_MAP[state.request.method]

        path_info = state.request.path_info

        if not path_info:
            return

        resource = state.request.context.get('resource')

        if not resource:
            return

        action = "%s_%s" % (method, resource)

        gluon_context = state.request.context.get('gluon_context')

        policy.init()

        try:
            policy.enforce(
                gluon_context, action, None)
        except oslo_policy.PolicyNotAuthorized as e:
            raise webob.exc.HTTPForbidden(str(e))

    def after(self, state):
        # This method could be used for implementing access control
        # at the attribute level.
        return
