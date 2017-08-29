..
      Copyright 2016 and 2017, OpenStack Foundation

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
have already installed ``etcd`` and **Gluon Plugin**, and started
**Proton Server**.  If not, please refer to [1]_.

Advanced users may also want to enable RBAC feature in Gluon. Please refer to
"Gluon Authentication and Authorization" [2]_ for the basic concept,
and how to configure and enable RBAC in Gluon. The setup steps are also described
in [1]_.

This User Guide provides CLI examples. The RESTful API is specified in
"Gluon API Specification" [3]_. If RBAC is enabled, you need to make sure
that "X-Auth-Token: <auth-token>" header is always added in your
RESTful HTTP request.

Getting Help
------------

Just typing the ``protonclient --help`` command gives you general help
information:

.. code-block:: bash

    # The equivalent RESTful API is
    #     GET /proton HTTP/1.1

    $ protonclient --help
    --api is not specified!

    Usage: protonclient --api <api_name> [OPTIONS] COMMAND[ARGS]...

    Options:
    --api TEXT      Name of API, one of ['ietf-sfc', 'net-l3vpn', 'test']
    --port INTEGER  Port of endpoint (OS_PROTON_PORT)
    --host TEXT     Host of endpoint (OS_PROTON_HOST)
    --help          Show this message and exit.

Mandatory Parameters
--------------------

``--api <api_name>`` are mandatory parameters. For example, ``--api net-l3vpn``.

Just typing the ``protonclient`` command shows you that those mandatory
parameters are required, and gives you general help information too:

.. code-block:: bash

    # The equivalent RESTful API is
    #     GET /proton HTTP/1.1

    $ protonclient
    --api is not specified!

    Usage: protonclient --api <api_name> [OPTIONS] COMMAND[ARGS]...

    Options:
    --api TEXT      Name of API, one of ['ietf-sfc', 'net-l3vpn', 'test']
    --port INTEGER  Port of endpoint (OS_PROTON_PORT)
    --host TEXT     Host of endpoint (OS_PROTON_HOST)
    --help          Show this message and exit.

Using L3VPN Proton
------------------

**NOTE** that there is a KNOWN BUG in the **Usage** message where the mandatory
parameters ``--api net-l3vpn`` are missing. The **examples** show you the
correct command line usage.

.. code-block:: bash

    # The equivalent RESTful API is
    #     GET /proton/net-l3vpn/v1.0 HTTP/1.1

    $ protonclient --api net-l3vpn
    Usage: protonclient [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      bgppeering-create
      bgppeering-delete
      bgppeering-list
      bgppeering-show
      bgppeering-update
      dataplanetunnel-create
      dataplanetunnel-delete
      dataplanetunnel-list
      dataplanetunnel-show
      dataplanetunnel-update
      interface-create
      interface-delete
      interface-list
      interface-show
      interface-update
      port-create
      port-delete
      port-list
      port-show
      port-update
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
      vpnbinding-create
      vpnbinding-delete
      vpnbinding-list
      vpnbinding-show
      vpnbinding-update

Create ``Interface`` Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/interfaces HTTP/1.1

    $ protonclient --api net-l3vpn interface-create --help
    Usage: protonclient interface-create [OPTIONS]

    Options:
      --segmentation_id INTEGER Segmentation identifier  [required]
      --name TEXT               Descriptive name of Object
      --id TEXT                 UUID of Object
      --segmentation_type [none|vlan|tunnel_vxlan|tunnel_gre|mpls]
                                  Type of segmentation for this interface
                                  [required]
      --tenant_id TEXT          UUID of Tenant  [required]
      --port_id TEXT            Pointer to Port instance  [required]
      --port INTEGER            Port of endpoint (OS_PROTON_PORT)
      --host TEXT               Host of endpoint (OS_PROTON_HOST)
      --help                    Show this message and exit.

There is a default ``Interface`` which is automatically created when a ``Port``
is created. The UUID of this default ``Interface`` will be the same as the
UUID of the parent ``Port``.

**For example: list the default ``Interface`` Object**:

.. code-block:: bash

    # The equivalent RESTful API is
    #     GET /proton/net-l3vpn/v1.0/interfaces HTTP/1.1

    $ protonclient --api net-l3vpn interface-list
    {
        "interfaces": [
            {
                "name": "TestVPNPort_default",
                "segmentation_id": 0,
                "created_at": "2017-02-14T20:35:47.760126",
                "updated_at": "2017-02-14T20:35:47.760126",
                "tenant_id": "a868a466bca84df18404a77db0ecac72", 
                "port_id": "fe338d4c-2aef-4487-aa25-cb753bf02518",
                "segmentation_type": "none",
                "id": "fe338d4c-2aef-4487-aa25-cb753bf02518"
            }
        ]
    }

Create ``VPNAFConfig`` Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/vpnafconfigs HTTP/1.1

    $ protonclient --api net-l3vpn vpnafconfig-create --help
    Usage: protonclient vpnafconfig-create [OPTIONS]

    Options:
      --vrf_rt_value TEXT Route       target string [required]
      --export_route_policy TEXT      Route target export policy
      --import_route_policy TEXT      Route target import policy
      --vrf_rt_type [export_extcommunity|import_extcommunity|both]
                                        Route target type [required]
      --tenant_id TEXT                UUID of Tenant  [required]
      --port INTEGER                  Port of endpoint (OS_PROTON_PORT)
      --host TEXT                     Host of endpoint (OS_PROTON_HOST)
      --help                          Show this message and exit.

**For example: create a ``VPNAFConfig`` Object**:

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/vpnafconfigs HTTP/1.1

    $ protonclient --api net-l3vpn vpnafconfig-create --vrf_rt_type both --vrf_rt_value 1000:1000 --tenant_id a868a466bca84df18404a77db0ecac72
    {
        "vrf_rt_type": "both",
        "vrf_rt_value": "1000:1000"
    }

Create ``VPN`` Object
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/vpns HTTP/1.1

    $ protonclient --api net-l3vpn vpn-create --help
    Usage: protonclient vpn-create [OPTIONS]

    Options:
      --id TEXT                    UUID of Object
      --name TEXT                  Descriptive name of Object
      --tenant_id TEXT             UUID of Tenant  [required]
      --ipv4_family TEXT           Comma separated list of route target strings
                                   (VpnAfConfig)
      --ipv6_family TEXT           Comma separated list of route target strings
                                   (VpnAfConfig)
      --route_distinguishers TEXT  Route distinguisher for this VPN
      --description TEXT           Description of Service
      --port INTEGER               Port of endpoint (OS_PROTON_PORT)
      --host TEXT                  Host of endpoint (OS_PROTON_HOST)
      --help                       Show this message and exit.

You must specify the ``ipv4_family`` and ``ipv6_family`` attributes. The
values should match the ``vrf_rt_value`` of the ``vpnafconfig`` object.
The UUID of VPN instance ``id`` is generated by Proton and returned.

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/vpns HTTP/1.1

    $ protonclient --api net-l3vpn vpn-create --name "TestVPN" --ipv4_family 1000:1000 --ipv6_family 1000:1000 --route_distinguishers 1000:1000 --tenant_id a868a466bca84df18404a77db0ecac72 --description "My Test VPN"
    {
        "description": "My Test VPN",
        "route_distinguishers": "1000:1000",
        "tenant_id": "a868a466bca84df18404a77db0ecac72", 
        "created_at": "2017-02-14T20:37:58.592999",
        "updated_at": "2017-02-14T20:37:58.592999",
        "ipv6_family": "1000:1000",
        "ipv4_family": "1000:1000",
        "id": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010",
        "name": "TestVPN"
    }

Create ``Port`` Object
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/ports HTTP/1.1

    $ protonclient --api net-l3vpn port-create --help
    Usage: protonclient port-create [OPTIONS]

    Options:
      --device_id TEXT                UUID of bound VM
      --id TEXT                       UUID of Object
      --host_id TEXT                  binding:host_id: Name of bound host
      --mac_address TEXT              MAC address for Port [required]
      --vlan_transparency BOOLEAN     Allow VLAN tagged traffic on Port
                                      [required]
      --device_owner TEXT             Name of compute or network service (if
                                      bound)
      --mtu INTEGER                   MTU [required]
      --vnic_type [normal|virtual|direct|macvtap|sriov|whole-dev]
                                      Port should be attached to this VNIC type
                                      [required]
      --vif_details TEXT              binding:vif_details: JSON string for VIF
                                      details
      --tenant_id TEXT                UUID of Tenant [required]
      --admin_state_up BOOLEAN        Admin state of Port  [required]
      --name TEXT                     Descriptive name of Object
      --vif_type TEXT                 binding:vif_type: binding type for VIF
      --profile TEXT                  JSON string for binding profile dictionary
      --status [ACTIVE|DOWN]          Operational status of Port [required]
      --port INTEGER                  Port of endpoint (OS_PROTON_PORT)
      --host TEXT                     Host of endpoint (OS_PROTON_HOST)
      --help                          Show this message and exit.

These values should be specified.

The ``tenant_id`` should be a ``project-id``obtained from OpenStack.

The UUID of the object ``id`` is generated by the Proton and returned.

**For example: create a ``Port`` Object**:

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/ports HTTP/1.1

    $ protonclient --api net-l3vpn port-create --mac_address c8:2a:14:04:43:80 --mtu 1500 --admin_state_up True --name "TestVPNPort" --vlan_transparency True --vnic_type normal --vif_type ovs --status ACTIVE --tenant_id 5205b400fa6c4a888a0b229200562229
    {
        "profile": null,
        "status": "ACTIVE",
        "vif_type": "ovs",
        "name": "TestVPNPort",
        "device_owner": null,
        "admin_state_up": true,
        "tenant_id": "a868a466bca84df18404a77db0ecac72", 
        "created_at": "2017-02-14T20:35:47.749427",
        "vif_details": null,
        "updated_at": "2017-02-14T20:35:47.749427",
        "mtu": 1500,
        "vnic_type": "normal",
        "vlan_transparency": true,
        "mac_address": "c8:2a:14:04:43:80",
        "host_id": null,
        "id": "fe338d4c-2aef-4487-aa25-cb753bf02518",
        "device_id": null
    }

As we mentioned earlier, a default ``interface`` object is created too, and
attached to this ``port`` object.

At this point you have a ``port`` object, default ``interface`` object and a
``vpn`` service object created.

View ``VPN`` and ``Port`` Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can view the values with the following commands:

.. code-block:: bash

    # The equivalent RESTful API is
    #     GET /proton/net-l3vpn/v1.0/vpns HTTP/1.1

    $ protonclient --api net-l3vpn vpn-list
    {
        "vpns": [
            {
                "description": "My Test VPN",
                "route_distinguishers": "1000:1000",
                "tenant_id": "a868a466bca84df18404a77db0ecac72", 
                "created_at": "2017-02-14T20:37:58.592999",
                "updated_at": "2017-02-14T20:37:58.592999",
                "ipv6_family": "1000:1000",
                "ipv4_family": "1000:1000",
                "id": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010",
                "name": "TestVPN"
            }
        ]
    }
    $

    # The equivalent RESTful API is
    #     GET /proton/net-l3vpn/v1.0/ports HTTP/1.1

    $ protonclient --api net-l3vpn port-list
    {
        "ports": [
            {
                "profile": null,
                "status": "ACTIVE",
                "vif_type": "ovs",
                "name": "TestVPNPort",
                "device_owner": null,
                "admin_state_up": true,
                "tenant_id": "a868a466bca84df18404a77db0ecac72", 
                "created_at": "2017-02-14T20:35:47.749427",
                "vif_details": null,
                "updated_at": "2017-02-14T20:35:47.749427",
                "mtu": 1500,
                "vnic_type": "normal",
                "vlan_transparency": true,
                "mac_address": "c8:2a:14:04:43:80",
                "host_id": null,
                "id": "fe338d4c-2aef-4487-aa25-cb753bf02518",
                "device_id": null
            }
        ]
    }

Create ``VPNBinding`` Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create a ``vpnbinding`` object to tie the ``Interface`` and the
``Service`` together in order to achieve service binding.

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/vpnbindings HTTP/1.1

    $ protonclient --api net-l3vpn vpnbinding-create --help
    Usage: protonclient vpnbinding-create [OPTIONS]

    Options:
      --interface_id TEXT      Pointer to Interface instance  [required]
      --gateway TEXT           Default gateway
      --ipaddress TEXT         IP Address of port
      --subnet_prefix INTEGER  Subnet mask
      --service_id TEXT        Pointer to Service instance  [required]
      --tenant_id TEXT         UUID of Tenant [required]
      --port INTEGER           Port of endpoint (OS_PROTON_PORT)
      --host TEXT              Host of endpoint (OS_PROTON_HOST)
      --help                   Show this message and exit.

The ``vpnbinding`` object is created by using an ``interface_id`` and a
``service_id``. In our example, a default ``interface`` object was
automatically created and attached to a ``port`` object when the ``port``
object was created. The ``Service`` is ``vpn``. Thus we use the ``id`` of the
default ``interface`` object, and the ``id`` of the ``vpn`` object.

**For example: create a ``VPNBinding`` Object**:

.. code-block:: bash

    # The equivalent RESTful API is
    #     POST /proton/net-l3vpn/v1.0/vpnbindings HTTP/1.1

    $ protonclient --api net-l3vpn vpnbinding-create --interface_id fe338d4c-2aef-4487-aa25-cb753bf02518 --service_id b70b4bbd-aa40-48d7-aa4b-57cc2fd34010 --ipaddress 10.10.0.2 --subnet_prefix 24 --gateway 10.10.0.1 --tenant_id a868a466bca84df18404a77db0ecac72
    {
        "tenant_id": "a868a466bca84df18404a77db0ecac72", 
        "created_at": "2017-02-14T20:39:52.382433",
        "subnet_prefix": 24,
        "updated_at": "2017-02-14T20:39:52.382433",
        "interface_id": "fe338d4c-2aef-4487-aa25-cb753bf02518",
        "service_id": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010",
        "ipaddress": "10.10.0.2",
        "gateway": "10.10.0.1"
    }

View ``VPNBinding`` Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # The equivalent RESTful API is
    #     GET /proton/net-l3vpn/v1.0/vpnbindings HTTP/1.1

    $ protonclient --api net-l3vpn vpnbinding-list
    {
        "vpnbindings": [
            {
                "tenant_id": "a868a466bca84df18404a77db0ecac72",
                "created_at": "2017-02-14T20:39:52.382433",
                "subnet_prefix": 24,
                "updated_at": "2017-02-14T20:39:52.382433",
                "interface_id": "fe338d4c-2aef-4487-aa25-cb753bf02518",
                "service_id": "b70b4bbd-aa40-48d7-aa4b-57cc2fd34010",
                "ipaddress": "10.10.0.2",
                "gateway": "10.10.0.1"
            }
        ]
    }

At this point you have had all of the information needed for an L3VPN Port in
Proton.

Create VM and Bind our L3VPN Port
---------------------------------

.. code-block:: bash

    # Refer to Nova documentation for RESTful APIs

    $ nova --debug boot --flavor m1.tiny --image cirros --nic port-id=fe338d4c-2aef-4487-aa25-cb753bf02518 TestGluon

When bound, the ``etcd`` data will look like:

.. code-block:: bash

    $ etcdctl  --endpoint http://192.0.2.4:2379 ls / --recursive
    /proton
    /proton/net-l3vpn
    /proton/net-l3vpn/Port
    /proton/net-l3vpn/Port/fe338d4c-2aef-4487-aa25-cb753bf02518
    /proton/net-l3vpn/Interface
    /proton/net-l3vpn/Interface/fe338d4c-2aef-4487-aa25-cb753bf02518
    /proton/net-l3vpn/VpnService
    /proton/net-l3vpn/VpnService/b70b4bbd-aa40-48d7-aa4b-57cc2fd34010
    /proton/net-l3vpn/VpnBinding
    /proton/net-l3vpn/VpnBinding/fe338d4c-2aef-4487-aa25-cb753bf02518
    /gluon
    /gluon/port
    /gluon/port/fe338d4c-2aef-4487-aa25-cb753bf02518
    $

You may use other command in ``etcd`` to check specific data record, such as:

.. code-block:: bash

    # etcdctl --endpoint http://192.0.2.4:2379 get /proton/net-l3vpn/Port/fe338d4c-2aef-4487-aa25-cb753bf02518

To Use Gluon in a Project
-------------------------

.. code-block:: bash

    import gluon

References

.. [1] installation.rst
.. [2] devref/gluon-auth.inc
.. [3] devref/gluon_api_spec.inc
