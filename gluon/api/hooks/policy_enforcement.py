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

from oslo_policy import policy as oslo_policy
from oslo_utils import excutils
from pecan import hooks
import webob

from gluon._i18n import _
from gluon import constants
from gluon import policy


class PolicyHook(hooks.PecanHook):
    priority = 100

    def before(self, state):

        # This hook should be run only for PUT,POST and DELETE methods
        resources = state.request.context.get('resources', [])

        if state.request.method not in ('POST', 'PUT', 'DELETE'):
            return

        # As this routine will likely alter the resources, do a shallow copy
        resources_copy = resources[:]
        gluon_context = state.request.context.get('gluon_context')
        resource = state.request.context.get('resource')

        # If there is no resource for this request, don't bother running authZ
        # policies
        if not resource:
            return

        # controller = utils.get_controller(state)
        controller = state.arguments.args[0]

        # if not controller or utils.is_member_action(controller):
        #    return

        collection = state.request.context.get('collection')
        needs_prefetch = (state.request.method == 'PUT' or
                          state.request.method == 'DELETE')
        policy.init()

        action = controller.plugin_handlers[
            constants.ACTION_MAP[state.request.method]]

        for item in resources_copy:
            try:
                policy.enforce(
                    gluon_context, action, item,
                    pluralized=collection)
            except oslo_policy.PolicyNotAuthorized:
                with excutils.save_and_reraise_exception() as ctxt:
                    # If a tenant is modifying it's own object, it's safe to
                    # return a 403. Otherwise, pretend that it doesn't exist
                    # to avoid giving away information.
                    orig_item_tenant_id = item.get('tenant_id')
                    if (needs_prefetch and
                        (gluon_context.tenant_id != orig_item_tenant_id or
                         orig_item_tenant_id is None)):
                        ctxt.reraise = False
                msg = _('The resource could not be found.')
                raise webob.exc.HTTPNotFound(msg)

    def after(self, state):
        gluon_context = state.request.context.get('gluon_context')
        resource = state.request.context.get('resource')
        collection = state.request.context.get('collection')
        # = utils.get_controller(state)
        controller = state.arguments.args[0]

        if not resource:
            # can't filter a resource we don't recognize
            return

        if resource == 'extension':
            return
        try:
            data = state.response.json
        except ValueError:
            return

        if state.request.method not in constants.ACTION_MAP:
            return

        action = '%s_%s' % (constants.ACTION_MAP[state.request.method],
                            resource)

        if not data or (resource not in data and collection not in data):
            return

        is_single = resource in data
        key = resource if is_single else collection
        to_process = [data[resource]] if is_single else data[collection]

        # in the single case, we enforce which raises on violation
        # in the plural case, we just check so violating items are hidden
        policy_method = policy.enforce if is_single else policy.check

        try:
            resp = [self._get_filtered_item(state.request, controller,
                                            resource, collection, item)
                    for item in to_process
                    if (state.request.method != 'GET' or
                        policy_method(gluon_context, action, item,
                                      pluralized=collection))]
        except oslo_policy.PolicyNotAuthorized as e:
            # This exception must be explicitly caught as the exception
            # translation hook won't be called if an error occurs in the
            # 'after' handler.
            raise webob.exc.HTTPForbidden(str(e))

        if is_single:
            resp = resp[0]
        state.response.json = {key: resp}

    def _get_filtered_item(self, request, controller, resource, collection,
                           data):
        gluon_context = request.context.get('gluon_context')
        to_exclude = self._exclude_attributes_by_policy(
            gluon_context, controller, resource, collection, data)
        return self._filter_attributes(request, data, to_exclude)

    def _filter_attributes(self, request, data, fields_to_strip):
        # This routine will remove the fields that were requested to the
        # plugin for policy evaluation but were not specified in the
        # API request
        user_fields = request.params.getall('fields')
        return dict(item for item in data.items()
                    if (item[0] not in fields_to_strip and
                        (not user_fields or item[0] in user_fields)))

    def _exclude_attributes_by_policy(self, context, controller, resource,
                                      collection, data):
        """Identifies attributes to exclude according to authZ policies.

        Return a list of attribute names which should be stripped from the
        response returned to the user because the user is not authorized
        to see them.
        """
        attributes_to_exclude = []
        for attr_name in data.keys():
            attr_data = controller.resource_info.get(attr_name)
            if attr_data and attr_data['is_visible']:
                if policy.check(context, 'get_%s:%s' % (resource, attr_name),
                                data, might_not_exist=True,
                                pluralized=collection):
                    # this attribute is visible, check next one
                    continue
            # if the code reaches this point then either the policy check
            # failed or the attribute was not visible in the first place
            attributes_to_exclude.append(attr_name)
        return attributes_to_exclude
