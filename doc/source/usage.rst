..
      Copyright 2016 and 2017, Nokia

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

      Convention for heading levels in Gluon documentation:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

==========
User Guide
==========

This User Guide shows you how to use **Proton** to create the needed objects,
and then use ``nova boot`` to bind the port to a VM. It is assumed that you
have already installed ``etcd``, **Gluon Plugin** and **Proton**.  If not,
please refer to [1]_.

Getting Help
------------

Just typing the ``protonclient`` command gives you general help info:

.. code-block:: bash

    $ protonclient
    Usage: protonclient [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      baseport-create
      baseport-delete
      baseport-list
      baseport-show
      baseport-update
      vpn-create
      vpn-delete
      vpn-list
      vpn-show
      vpn-update
      vpnafconfig-create
      vpnafconfig-delete
      vpnafconfig-list
      vpnafconfig-show
      vpnafconfig-update
      vpnport-create
      vpnport-delete
      vpnport-list
      vpnport-show
      vpnport-update

Create VPNAFConfig Object
-------------------------

.. code-block:: bash

    $ protonclient vpnafconfig-create --help
    Usage: protonclient vpnafconfig-create [OPTIONS]

    Options:
      --vrf_rt_value TEXT             Route target string  [required]
      --export_route_policy TEXT      Route target export policy
      --import_route_policy TEXT      Route target import policy
      --vrf_rt_type [export_extcommunity|import_extcommunity|both]
                                        Route target type  [required]
      --port INTEGER                  Port of endpoint (OS_PROTON_PORT)
      --host TEXT                     Host of endpoint (OS_PROTON_HOST)
      --help                          Show this message and exit.

Create an Object
~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ protonclient vpnafconfig-create --vrf_rt_type both --vrf_rt_value 1000:1000
    {
        "vrf_rt_type": "both",
        "vrf_rt_value": "1000:1000"
    }

Create VPN Object
-----------------

.. code-block:: bash

    $ protonclient vpn-create --help
    Usage: protonclient vpn-create [OPTIONS]

    Options:
      --id TEXT                    UUID of VPN instance
      --vpn_instance_name TEXT     Name of VPN  [required]
      --ipv4_family TEXT           Comma separated list of route target strings
                                   (VpnAfConfig)
      --ipv6_family TEXT           Comma separated list of route target strings
                                   (VpnAfConfig)
      --route_distinguishers TEXT  Route distinguisher for this VPN
      --description TEXT           About the VPN
      --port INTEGER               Port of endpoint (OS_PROTON_PORT)
      --host TEXT                  Host of endpoint (OS_PROTON_HOST)
      --help                       Show this message and exit.

You must specify the ``ipv4_family`` and ``ipv6_family`` attributes.  The values should
match the ``vrf_rt_value`` of the ``vpnafconfig`` object.

.. code-block:: bash

    $ protonclient vpn-create --vpn_instance_name "TestVPN" --ipv4_family 1000:1000 --ipv6_family 1000:1000 --route_distinguishers 1000:1000 --description "My Test VPN"
    {
        "description": "My Test VPN",
        "route_distinguishers": "1000:1000",
        "vpn_instance_name": "TestVPN",
        "ipv6_family": "1000:1000",
        "id": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010",
        "ipv4_family": "1000:1000"
    }

Create Baseport Object
----------------------

.. code-block:: bash

    $ protonclient baseport-create -help
    Usage: protonclient baseport-create [OPTIONS]

    Options:
      --mac_address TEXT              MAC address for port  [required]
      --mtu INTEGER                   MTU  [required]
      --device_owner TEXT             Name of compute or network service (if
                                      bound)
      --subnet_prefix INTEGER         Subnet mask
      --tenant_id TEXT                UUID of tenant owning this port  [required]
      --network_id TEXT               UUID of network - not used for Proton
      --admin_state_up BOOLEAN        Admin state of port  [required]
      --zone TEXT                     zone information
      --name TEXT                     Descriptive name for port
      --device_id TEXT                UUID of bound VM
      --gateway TEXT                  Default gateway
      --ipaddress TEXT                IP Address of port
      --host_id TEXT                  binding:host_id: Name of bound host
      --id TEXT                       UUID of base port instance
      --vlan_transparency BOOLEAN     Allow VLAN tagged traffic on port
                                      [required]
      --vnic_type [normal|virtual|direct|macvtap|sriov|whole-dev]
                                      binding:vnic_type: Port should be attached to
                                      this VNIC type  [required]
      --vif_details TEXT              binding:vif_details: JSON string for VIF
                                      details
      --vif_type TEXT                 binding:vif_type: Headline binding type for
                                      VIF
      --profile TEXT                  binding:profile: JSON string for binding
                                      profile dictionary
      --status [ACTIVE|DOWN]          Operational status of port  [required]
      --port INTEGER                  Port of endpoint (OS_PROTON_PORT)
      --host TEXT                     Host of endpoint (OS_PROTON_HOST)
      --help                          Show this message and exit.

These values should be specified.

The ``tenant_id`` should be obtained from OpenStack.

**Note** that the ``id`` is generated by the proton and returned.

.. code-block:: bash

    protonclient baseport-create --mac_address c8:2a:14:04:43:80 --mtu 1500 --subnet_prefix 30 --admin_state_up True --name "TestVPNPort" --ipaddress 10.10.10.3 --vlan_transparency True --vnic_type normal --vif_type ovs --status ACTIVE --tenant_id 5205b400fa6c4a888a0b229200562229
    {
        "status": "ACTIVE",
        "vif_type": "ovs",
        "name": "TestVPNPort",
        "admin_state_up": true,
        "tenant_id": "5205b400fa6c4a888a0b229200562229",
        "subnet_prefix": 30,
        "mtu": 1500,
        "vnic_type": "normal",
        "vlan_transparency": true,
        "mac_address": "c8:2a:14:04:43:80",
        "ipaddress": "10.10.10.3",
        "id": "fe338d4c-2aef-4487-aa25-cb753bf02518"
    }

At this point you have a ``baseport`` object and a ``vpn`` object created.

View VPN and Baseport Objects
-----------------------------

You can view the values with the following commands:

.. code-block:: bash

    $ protonclient vpn-list
    {
        "vpns": [
            {
                "description": "My Test VPN", 
                "route_distinguishers": "1000:1000", 
                "created_at": "2016-06-13 23:00:42.292113", 
                "updated_at": "2016-06-13 23:00:42.292113", 
                "vpn_instance_name": "TestVPN", 
                "ipv6_family": "1000:1000", 
                "id": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010",
                "ipv4_family": "1000:1000"
            }
        ]
    }
    $ 
    $ protonclient baseport-list
    {
        "baseports": [
            {
                "profile": "", 
                "vif_type": "ovs", 
                "updated_at": "2016-06-13 23:37:33.072294", 
                "device_owner": "", 
                "gateway": null, 
                "zone": "", 
                "vif_details": "{}", 
                "subnet_prefix": 30, 
                "id": "fe338d4c-2aef-4487-aa25-cb753bf02518", 
                "mac_address": "c8:2a:14:04:43:80", 
                "status": "ACTIVE", 
                "vlan_transparency": true, 
                "host_id": "", 
                "ipaddress": "10.10.10.3", 
                "device_id": "", 
                "name": "TestVPNPort", 
                "admin_state_up": true, 
                "network_id": null, 
                "tenant_id": "5205b400fa6c4a888a0b229200562229", 
                "created_at": "2016-06-13 23:05:12.316246", 
                "vnic_type": "normal", 
                "mtu": 1500
            }
        ]
    }

Create VPNPort Object
---------------------

You need to create a ``vpnport`` object to tie the ``baseport`` and the ``vpn`` together, i.e. service binding.

.. code-block:: bash

    $ protonclient vpnport-create --help
    Usage: protonclient vpnport-create [OPTIONS]

    Options:
      --id TEXT            Pointer to base port instance (UUID)  [required]
      --vpn_instance TEXT  Pointer to VPN instance (UUID)  [required]
      --port INTEGER       Port of endpoint (OS_PROTON_PORT)
      --host TEXT          Host of endpoint (OS_PROTON_HOST)
      --help               Show this message and exit.

The ``vpnport`` is created by using:
* the ``baseport id`` as its ``id``;
* the ``vpn id`` as the ``vpn_instance`` value.

.. code-block:: bash

    $ protonclient vpnport-create --id fe338d4c-2aef-4487-aa25-cb753bf02518 --vpn_instance b70b4bbd-aa40-48d7-aa4b-57cc2fd34010
    {
        "vpn_instance": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010",
        "id": "fe338d4c-2aef-4487-aa25-cb753bf02518"
    }

At this point you have all of the information entered for an L3VPN Port in Proton.

Create VM and Bind our L3VPN Port
---------------------------------

.. code-block:: bash

    $ nova --debug boot --flavor 1 --image cirros --nic port-id=fe338d4c-2aef-4487-aa25-cb753bf02518 TestGluon

When bound, the ``etcd`` data will look like:

.. code-block:: bash

    $ etcdctl ls --recursive
    /proton
    /proton/net-l3vpn
    /proton/net-l3vpn/VpnAfConfig
    /proton/net-l3vpn/VpnAfConfig/1000:1000
    /proton/net-l3vpn/VpnInstance
    /proton/net-l3vpn/VpnInstance/b70b4bbd-aa40-48d7-aa4b-57cc2fd34010
    /proton/net-l3vpn/ProtonBasePort
    /proton/net-l3vpn/ProtonBasePort/fe338d4c-2aef-4487-aa25-cb753bf02518
    /proton/net-l3vpn/VPNPort
    /proton/net-l3vpn/VPNPort/fe338d4c-2aef-4487-aa25-cb753bf02518
    /gluon
    /gluon/port
    /gluon/port/fe338d4c-2aef-4487-aa25-cb753bf02518
    /controller
    /controller/net-l3vpn
    /controller/net-l3vpn/ProtonBasePort
    /controller/net-l3vpn/ProtonBasePort/fe338d4c-2aef-4487-aa25-cb753bf02518
    $
    $ etcdctl get /proton/net-l3vpn/ProtonBasePort/fe338d4c-2aef-4487-aa25-cb753bf02518
    {"status": "ACTIVE", "vif_type": "ovs", "updated_at": "2016-06-13 23:37:33.072294", "device_owner": "nova", "id": "fe338d4c-2aef-4487-aa25-cb753bf02518", "zone": "compute:None", "vif_details": "None", "subnet_prefix": "30", "gateway": "None", "mac_address": "c8:2a:14:04:43:80", "profile": "{\n\"pci_profile\": \"\", \n\"rxtx_factor\": \"\"\n}", "vlan_transparency": "True", "host_id": "cbserver5", "ipaddress": "10.10.10.3", "device_id": "5d15a851-663a-479f-87c9-49ed356d94b4", "name": "TestVPNPort", "admin_state_up": "True", "network_id": "None", "tenant_id": "5205b400fa6c4a888a0b229200562229", "created_at": "2016-06-13 23:05:12.316246", "vnic_type": "normal", "mtu": "1500"}
    $
    $ etcdctl get /proton/net-l3vpn/VpnInstance/b70b4bbd-aa40-48d7-aa4b-57cc2fd34010
    {"description": "My Test VPN", "route_distinguishers": "1000:1000", "created_at": "2016-06-13 23:00:42.292113", "updated_at": "None", "vpn_instance_name": "TestVPN", "ipv6_family": "1000:1000", "id": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010", "ipv4_family": "1000:1000"}
    $
    $ etcdctl get /proton/net-l3vpn/VPNPort/fe338d4c-2aef-4487-aa25-cb753bf02518
    {"id": "fe338d4c-2aef-4487-aa25-cb753bf02518", "vpn_instance": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010", "created_at": "2016-06-13 23:07:18.510875", "updated_at": "None"}
    $
    $ etcdctl get /proton/net-l3vpn/VpnAfConfig/1000:1000
    {"vrf_rt_type": "both", "export_route_policy": "None", "updated_at": "None", "created_at": "2016-06-13 22:59:14.279513", "import_route_policy": "None", "vrf_rt_value": "1000:1000"}

To Use Gluon in a Project
-------------------------

.. code-block:: bash

    import gluon

References

.. [1] installation

