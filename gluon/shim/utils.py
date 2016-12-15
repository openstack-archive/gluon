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

import netaddr
import pprint


def compute_network_addr(ip, prefix):
    """return network address"""

    addr = netaddr.IPNetwork(ip)
    addr.prefixlen = int(prefix)
    return str(addr.network)


def compute_netmask(prefix):
    """return netmask

    :param prefix:
    :return:
    """
    addr = netaddr.IPNetwork("0.0.0.0")
    addr.prefixlen = int(prefix)
    return str(addr.netmask)


def compute_gateway(network, prefix):
    """compute the default gateway IP of a network

    :param network: the network IP
    :param prefix: the prefix of the network
    :return: a string representation of the gateway IP
    """
    addr = netaddr.IPNetwork(network)
    addr.prefixlen = prefix
    return str(addr[1])


def compute_hostip_range(network, prefix):
    """compute the IP range of a network

    :param network: the network IP
    :param prefix: the prefix of the network
    :return: a tupel with the first and last host IP in the network
    """
    addr = netaddr.IPNetwork(network)
    addr.prefixlen = prefix
    return (addr[2], addr[-2])


def pretty_print_message(message):
    pp = pprint.PrettyPrinter()
    return pp.pformat(vars(message))
