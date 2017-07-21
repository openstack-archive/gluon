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

from gluon.policies import base


# TODO(JinLi) This file is NOT used, it is an example of moving policy to code.
# Unlike other Openstack projects whose api has a fix set of restControllers,
# Gluon dynamically generates its restControllers from yaml files. If Gluon
# follows the policy in code approach, Gluon users will need to modify source
# code by adding similar files like this one. And then call the list_rules
# function inside the gluon.policies.__init__.py
#
# Gluon takes a different approach by defining policies inside the yaml file of
# a model, so that users do not need to modify any source code
#
# If user prefers to use plicy in code, they can use this file. And create
# similar file for new service.
net_l3vpn_policies = [
    policy.RuleDefault(
        name='net-l3vpn:create_dataplanetunnels',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_dataplanetunnels',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:update_dataplanetunnels',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_one_dataplanetunnels',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:delete_dataplanetunnels',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:create_bgppeerings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_bgppeerings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:update_bgppeerings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_one_bgppeerings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:delete_bgppeerings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:create_vpnafconfigs',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_vpnafconfigs',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:update_vpnafconfigs',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_one_vpnafconfigs',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:delete_vpnafconfigs',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:create_vpnservices',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_vpnservices',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:update_vpnservices',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_one_vpnservices',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:delete_vpnservices',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:create_interfaces',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_interfaces',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:update_interfaces',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_one_interfaces',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:delete_interfaces',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:create_vpnbindings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_vpnbindings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:update_vpnbindings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_one_vpnbindings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:delete_vpnbindings',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:create_ports',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_ports',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:update_ports',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:get_one_ports',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        ),
    policy.RuleDefault(
        name='net-l3vpn:delete_ports',
        check_str=base.RULE_ADMIN_OR_OWNER,
        description='net-l3vpn policy'
        )
]


def list_rules():
    return net_l3vpn_policies
