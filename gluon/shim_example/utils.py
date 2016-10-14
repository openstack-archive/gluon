# Copyright (c) 2016 Nokia, Inc.
# All Rights Reserved
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

def compute_network_addr(ip, prefix):
    """
    return network address
    """

    addr = ip.split('.')
    prefix = int(prefix)

    mask = [0, 0, 0, 0]
    for i in range(prefix):
        mask[i / 8] += (1 << (7 - i % 8))

    net = []
    for i in range(4):
        net.append(int(addr[i]) & mask[i])

    return '.'.join(str(e) for e in net)


def compute_netmask(prefix):
    """
    return netmask
    :param prefix:
    :return:
    """
    prefix = int(prefix)

    mask = [0, 0, 0, 0]
    for i in range(prefix):
        mask[i / 8] += (1 << (7 - i % 8))

    ret = '.'.join(str(e) for e in mask)
    print('Calculated mask = %s' % ret)
    return  ret
