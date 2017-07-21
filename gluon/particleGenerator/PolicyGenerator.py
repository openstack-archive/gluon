#    Copyright 2017, AT&T
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

from oslo_log._i18n import _
from oslo_log import log as logging
from oslo_policy import policy as oslo_policy

from gluon.particleGenerator import generator


LOG = logging.getLogger(__name__)


def policy_name(service, resource, action):
    re = "%s:%s_%ss"
    return re % (service, action, resource.lower())


def generatePolicies(service_list):
    policies = []
    for service in service_list:
        model = generator.load_model_for_service(service)
        generator.validate_policies(model)
        for obj_name, obj_val in model['api_objects'].items():
            actions = obj_val.get('policies')
            for action, rule in actions.items():
                name = policy_name(service, obj_name, action)
                policy = oslo_policy.RuleDefault(name, rule.get('role'))

                LOG.info('%(n)s : %(r)s' % dict(n=name, r=rule.get('role')))

                policies.append(policy)
    return policies
