# Copyright (c) 2016 OpenStack Foundation.
# All Rights Reserved.
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


from oslo_policy import policy

rules = [
    policy.RuleDefault('context_is_admin', 'role:admin'),
    policy.RuleDefault('owner', 'tenant_id:%(tenant_id)s'),
    policy.RuleDefault('admin_or_owner',
                       'rule:context_is_admin or rule:owner'),
    policy.RuleDefault('context_is_advsvc', 'role:advsvc'),
    policy.RuleDefault(
        'admin_or_network_owner',
        'rule:context_is_admin or tenant_id:%(network:tenant_id)s'),
    policy.RuleDefault('admin_owner_or_network_owner',
                       'rule:owner or rule:admin_or_network_owner'),
    policy.RuleDefault('admin_only', 'rule:context_is_admin'),
    policy.RuleDefault('regular_user', ''),
    policy.RuleDefault('default', 'rule:admin_or_owner')
]


def list_rules():
    return rules
