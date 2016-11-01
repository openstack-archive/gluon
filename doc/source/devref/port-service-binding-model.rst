Port and Service Binding Model
==============================

The following section describes the port- and service-binding model proposed for
the Gluon networking framework. The goal of this model is to clearly separate
ports from services and define how services bind to particular ports.

This model is based on the "service binding pattern" described in the NetReady
requirements document (insert reference) and was adapted for Gluon.

The goal of this section is to describe a generic model and establish it as a
general modeling paradigm for new service APIs for Gluon and Proton. Certainly,
one of the main driving factors behind Gluon and Proton is to have unprecedented
flexibility in defining new network service APIs. Hence, this model aims at
providing well established **guidelines** and describing **best practices** for
modeling new APIs which fundamentally aim at supporting developers in creating
new and powerful APIs.


General Design Paradigm
-----------------------

The fundamental design paradigm of this model is as follows. There are three
basic entities: i) baseports, ii) services, iii) service bindings.


* **baseports**

  An instance port object represents a vNIC which is bindable to an OpenStack
  instance by the compute service (Nova). It hence comprises all required
  information for defining the hand-off point between a network and a VM
  instance.

  Attributes: Since an instance-port is a layer 2 device, its attributes include
  the MAC address, MTU and others. See detailed YAML model below.


* **services**

  A service object represents a specific networking service, for example a L2
  network, a L3VPN or a service chaining service.

  Attributes: The attributes of the service objects are service specific and
  valid for a given service instance. See the YAML definition of a L3VPN service
  below.


* **service-bindings**

  A service-binding binds a networking service to a specific port. It hence
  comprises at least two attributes: a reference to a baseport and a reference to a
  service. In addition, it can comprise attributes which are specific to a
  service **and** a baseport.

  A service-binding is **not** an extension of a baseport (no inheritance).
  Instead, it is a separate entity. Modeling the binding as a separate entity
  instead of encoding it in the baseport object has the following advantages:

  i) It allows for dynamically binding and unbinding a service while keeping the
     VM and its port untouched. This simplifies VM migration across hosts as well
     as the migration of VMs between different network services and backends.

  ii) This entity allows for encapsulating service specific attributes which are
      specific to a port but shall not be part of the baseport. For example, in
      a L3 service, the IP address of the interface bound to the service can be
      specified here whereas this is not required for a pure L2 service.


A further evolution of a baseport is an interface. While a baseport corresponds
to a vNIC, an interface is a logical entity which specifies a traffic
segmentation mechanism (i.e., VLAN, VxLAN, GRE). Interfaces sit on top of ports
and services are bound to interfaces instead of ports. Hence, interfaces allow
for binding multiple (incompatible) services to a single port.



Example: L3VPN Port and Service Binding Model
---------------------------------------------

This example shows a generic baseport as well as a service and service-binding
model for a L3VPN service. It is an adaptation of the model used in the first
two Gluon demos.

The baseport object is service independent and an inherent property of Gluon::

 baseport:
    api:
      name: baseports
      parent:
        type: root
    attributes:
        id:
            type: uuid
            primary: 'True'
            description: "UUID of base port instance"
        tenant_id:
            type: 'uuid'
            required: True
            description: "UUID of tenant owning this port"
        name:
            type: 'string'
            length: 64
            description: "Descriptive name for port"
        mac_address:
            type: 'string'
            length: 17
            required: True
            description: "MAC address for port"
            validate: mac_address
        admin_state_up:
            type: 'boolean'
            required: True
            description: "Admin state of port"
        device_owner:
            type: 'string'
            length: 128
            description: "Name of compute or network service (if bound)"
        device_id:
            type: 'uuid'
            description: "UUID of bound VM"
        status:
            type: 'enum'
            required: True
            description: "Operational status of port"
            values:
                - 'ACTIVE'
                - 'DOWN'
        vnic_type:
            type: enum
            required: true
            description: "binding:vnic_type: Port should be attache to this VNIC type"
            values:
               - 'normal'
               - 'virtual'
               - 'direct'
               - 'macvtap'
               - 'sriov'
               - 'whole-dev'
        host_id:
            type: 'string'
            length: 32
            description: "binding:host_id: Name of bound host"
        vif_details:
            type: 'string' # what are we going to use, JSON?
            length: 128
            description: "binding:vif_details: JSON string for VIF details"
        profile:
            type: 'string' # what are we going to use, JSON?
            length: 128
            description: "binding:profile: JSON string for binding profile dictionary"
        vif_type:
            type: 'string'
            length: 32
            description: "binding:vif_type: Headline binding type for VIF"
        zone:
            type: 'string'
            length: 64
            description: "zone information"
        mtu:
            type: 'integer'
            description: "MTU"
            required: True
        vlan_transparency:
            type: 'boolean'
            description: "Allow VLAN tagged traffic on port"
            required: True

        #
        # the following attributes are layer 3 specific. We should think about
        # if those cannot be moved to a service binding object of a layer 3
        # service.
        #
        ipaddress:
            type: 'string'
            length: 64
            description: "IP Address of port"
            validate: 'ipv4address'
        subnet_prefix:
            type: 'integer'
            description: "Subnet mask"
            values:
                - '1-31'
        gateway:
            type: 'string'
            length: 64
            description: "Default gateway"
            validate: 'ipv4address'

        #
        # a "network" in the sense of Neutron is a service in itself. It hence
        # should be removed here as it corresponds to a service object.
        #
        network_id:
            type: 'uuid'
            description: "UUID of network - not used for Proton"


The l3vpn-instance object models an instance of a L3VPN **service**. It hence
comprises all attributes relevant to this specific type of service. In order to
avoid duplications among attributes, a separate vpn-af-config entity is
defined as well.::

 l3vpn-instance:
    api:
      name: l3vpns
      parent:
        type: root
    attributes:
        id:
            type: uuid
            primary: 'True'
            description: "UUID of VPN instance"
        vpn_instance_name:
            required: True
            type: string
            length: 32
            description: "Name of VPN"
        description:
            type: string
            length: 255
            description: "About the VPN"
        ipv4_family:
            type: string
            length: 255
            description: "Comma separated list of route target strings (vpn-af-config)"
        ipv6_family:
            type: string
            length: 255
            description: "Comma separated list of route target strings (vpn-af-config)"
        route_distinguishers:
            type: string
            length: 32
            description: "Route distinguisher for this VPN"

 vpn-af-config:
    api:
      name: vpnafconfigs
      parent:
        type: root
    attributes:
        vrf_rt_value:
            required: True
            type: string
            length: 32
            primary: 'True'
            description: "Route target string"
        vrf_rt_type:
            type: enum
            required: True
            description: "Route target type"
            values:
                - export_extcommunity
                - import_extcommunity
                - both
        import_route_policy:
            type: string
            length: 32
            description: "Route target import policy"
        export_route_policy:
            type: string
            length: 32
            description: "Route target export policy"


The l3vpn-binding object models the **binding** between a port and a l3vpn service.
In this particular example, it only comprises the two mandatory references to
the port and the service. However, as mentioned above, the IP address
information could be moved here from the baseport model.::

 l3vpn-binding:
    api:
      name: vpnbindings
      parent:
        type: root
    attributes:
        id:
            type: 'baseport'
            required: True
            primary: True
            description: "Pointer to base port instance (UUID)"
        vpn_instance:
            type: 'VpnInstance'
            required: True
            description: "Pointer to VPN instance (UUID)"

