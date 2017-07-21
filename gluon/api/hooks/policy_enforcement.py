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

import json
import webob

from oslo_config import cfg
from oslo_policy import policy as oslo_policy
# from oslo_utils import excutils
from pecan import hooks
from pecan.routing import lookup_controller

from gluon import constants as gluon_constants
from gluon import policy
from gluon.particleGenerator.ApiGenerator import API_OBJECT_CLASSES

# from gluon._i18n import _


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
        
        service = path_info.split("/")[2]
        action = "%s:%s_%s" % (service, method, resource)

        gluon_context = state.request.context.get('gluon_context')

        policy.init()
        
        target = generateTarget(state, service, resource)
        try:
            policy.enforce(
                gluon_context, action, target)
        except oslo_policy.PolicyNotAuthorized as e:
            raise webob.exc.HTTPForbidden(str(e))

    def after(self, state):
        # This method could be used for implementing access control
        # at the attribute level.
        return


# The policy enforce function requires target parameter
# oslo_policy doc descripbes target param as: "As much information about the
# object being operated on as possible"
# For delete and get, prefetch data from database and put tenant_id into target
# For post and put, get all user inputs from request body and put into target
def generateTarget(state, service, resource):
    target = {}
    method = state.request.method
    if method in ('GET','DELETE') and state.arguments.args:
        api_object_class = API_OBJECT_CLASSES[service][resource]
        key = state.arguments.args[0]
        obj = api_object_class.get_from_db(key)
        tenant_id = obj.tenant_id
        target['tenant_id'] = tenant_id
    if method in ('POST', 'PUT'):
        request_body = json.loads(state.request.body)
        target = request_body
    return target


def findContrller(state):
    path = state.request.path_info
    pathList = path.split('/')[1:]
    controller =  state.app.root
    resource = state.request.context.get('resource')
    if pathList:
        for item in pathList:
            controller = getattr(controller, item)
            if resource == item:
                return controller
    else:
        return controller
