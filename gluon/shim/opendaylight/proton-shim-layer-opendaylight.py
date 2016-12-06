#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Nokia
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its contributors
#       may be used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Gluon shim layer for handling etcd messages
"""

import etcd
import os
import json
import argparse
import urllib3
import time
import string
from odlc import restconf as odlc
from utils.log import LOG

from Queue import Queue
from threading import Thread

etcd_client = None

valid_host_ids = ('node-4.domain.tld')

proton_etcd_dir = '/proton/net-l3vpn'

def initialize_worker_thread(messages_queue):
    worker = Thread(target=process_queue, args=(messages_queue,))
    worker.setDaemon(True)
    worker.start()

    return worker

def process_base_port_port(message, uuid):
    action = message.action
    if action == 'set' or action == 'update':
        message_value = json.loads(message.value)
        if not message_value['host_id'] in valid_host_ids:
            LOG.info("host id %s is not recognized", message_value['host_id'])
            return
        id = name=message_value['id']
        # TODO get this from nova somehow
        parent_interface = 'tap%s' % id[:11]
        vif_dict = {'vif_type': 'ovs',
                    'vif_details': {'port_filter': False}}
        update_etcd_bound(id, vif_dict)
        odlc.update_ietf_interface(name=message_value['id'],
                                   parent_interface=parent_interface)

    elif action == 'delete':
        odlc.delete_ietf_interface(name=uudi)


def update_etcd_bound(key, vif_dict):
    vif_dict["controller"] = 'net-l3vpn'
    etcd_key = "{0:s}/{1:s}/{2:s}/{3:s}".format("controller",
                                                'net-l3vpn',
                                                "ProtonBasePort", key)
    try:
        global etcd_client
        etcd_client.write(etcd_key, json.dumps(vif_dict))
    except Exception, e:
        LOG.error("Update etcd to bound failed: %s" % str(e))

def process_vpn_instance(message, uuid):
    action = message.action
    if action == 'set' or action == 'update':
        message_value = json.loads(message.value)
        # TODO check is it belongs to us
        ipv4_vpnTargets = []
        if 'ipv4_family' in message_value:
            # TODO make lists possible as well
            vpn_af_config = json.loads(etcd_client.get(proton_etcd_dir +\
                                                  '/VpnAfConfig/' +\
                                                  message_value['ipv4_family']).value)
            ipv4_vpnTargets = {'vrfRTType': vpn_af_config['vrf_rt_type'],
                               'vrfRTValue': vpn_af_config['vrf_rt_value']}
        odlc.update_l3_vpn_instance(name=message_value['id'],
                                    ipv4_route_distinguisher=message_value['route_distinguishers'],
                                    ipv4_vpnTargets=ipv4_vpnTargets)
    elif action == 'delete':
        odlc.delete_l3_vpn_instance(name=uuid)

def process_vpn_port(message, uuid):
    action = message.action
    if action == 'set' or action == 'update':
        message_value = json.loads(message.value)
        # adjacency
        adjacency = []
        if 'id' in message_value:
            base_port = json.loads(etcd_client.get(proton_etcd_dir +\
                                              '/ProtonBasePort/' +\
                                              message_value['id']).value)
            if not base_port['host_id'] in valid_host_ids:
                return
            adjacency = [{"ip_address": base_port['ipaddress'],
                          "mac_address": base_port['mac_address']}]
        odlc.update_vpn_interface(name=message_value['id'],
                                  vpn_instance_name=message_value['vpn_instance'],
                                  adjacency=adjacency)
    elif action == 'delete':
        odlc.delete_vpn_interface(name=uuid)

def process_queue(messages_queue):
    LOG.info("processing queue")

    while True:
        item = messages_queue.get()
        process_message(item)
        messages_queue.task_done()


def process_message(message):
    try:
        #LOG.info("msg =  %s" % message)
        #LOG.info("msg.key =  %s" % message.key)
        #LOG.info("msg.value =  %s" % message.value)
        #LOG.info("msg.action =  %s" % message.action)
    
        path = message.key.split('/')
    
        if len(path) < 5:
            LOG.error("unknown message %s, ignoring" % message)
            return
    
        proton_name = path[1]
        table = path[3]
        uuid = path[4]
        if table == 'ProtonBasePort':
            LOG.info("Updating ProtonBasePort")
            process_base_port_port(message, uuid)
        elif table == 'VpnInstance':
            LOG.info("Updating VpnInstance")
            process_vpn_instance(message, uuid)
        elif table == 'VPNPort':
            LOG.info("Updating VpnInstance")
            process_vpn_port(message, uuid)
        else:
            LOG.error('unrecognized table %s' % table)
    except Exception as ex:
        LOG.error('Error when processing message: %s. ex: %s' % (message, str(ex)))

def getargs():
    parser = argparse.ArgumentParser(description='Start Shim Layer')

    parser.add_argument('-d', '--debug', required=False, help='Enable debug output', dest='debug',
                        action='store_true')
    parser.add_argument('-H', '--host-name', required=False, help='etcd hostname or ip, default to localhost',
                        dest='etcd_host', type=str)
    parser.add_argument('-p', '--port', required=False, help='etcd port number, default to 2379', dest='etcd_port',
                        type=str)

    args = parser.parse_args()
    return args

def full_sync(etcd_client, messages_queue):
    root = etcd_client.get(proton_etcd_dir)
    # /net-l3vpn/proton
    for child in root.get_subtree(leaves_only=True):
        # /net-l3vpn/proton/VpnAfConfig
        # /net-l3vpn/proton/VpnInstance
        # /net-l3vpn/proton/ProtonBasePort
        # /net-l3vpn/proton/VPNPort
        for message in etcd_client.get(child.key).get_subtree(leaves_only=True):
            message.action = 'update'
            process_message(message)

def main():
    global etcd_client
    LOG.info('Starting server in PID %s' % os.getpid())

    args = getargs()

    if args.etcd_host:
        etcd_host = args.etcd_host

    else:
        etcd_host = 'localhost'

    if args.etcd_host:
        etcd_port = int(args.etcd_port)

    else:
        etcd_port = 2379

    messages_queue = Queue()
    initialize_worker_thread(messages_queue)
    etcd_client = etcd.Client(host=etcd_host, port=etcd_port)

    wait_index = 0
    full_sync(etcd_client, messages_queue)

    while True:
        try:
            LOG.info("watching %s" % proton_etcd_dir)
            if wait_index:
                message = etcd_client.read(proton_etcd_dir, recursive=True, wait=True, waitIndex=wait_index)

            else:
                message = etcd_client.read(proton_etcd_dir, recursive=True, wait=True)
            process_message(message)
            #messages_queue.put(message)

            if (message.modifiedIndex - wait_index) > 1000:
                wait_index = 0

            else:
                wait_index = message.modifiedIndex + 1

        except etcd.EtcdWatchTimedOut:
            LOG.info("timeout")
            pass
        except etcd.EtcdException:
            LOG.error("cannot connect to etcd, make sure that etcd is running")
            exit(1)
        except KeyboardInterrupt:
            LOG.info("exiting on interrupt")
            exit(1)

        except:
            pass

if __name__ == '__main__':
    main()
