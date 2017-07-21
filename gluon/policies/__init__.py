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


import itertools

from gluon.particleGenerator import generator
from gluon.particleGenerator import PolicyGenerator
from gluon.policies import base
from gluon.policies import net_l3vpn


def list_rules():
    service_list = generator.get_service_list()
    return itertools.chain(
       base.list_rules(),
       PolicyGenerator.generatePolicies(service_list)
       # net_l3vpn.list_rules()
    )
