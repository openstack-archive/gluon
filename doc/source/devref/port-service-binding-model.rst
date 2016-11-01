Port and Service Binding Model
==============================

This document describes a generic modeling paradigm for new service APIs
(Protons) for OpenStack Gluon.

One fundamental driving force behind Gluon is the need for flexibility in
defining new network service APIs. The modeling paradigm described in the
following provides **design guidelines** and describes **best practices** for
creating new network service APIs. It hence supports developers in making the
best use of the flexibility provided by Gluon.

This model is based on the "service binding pattern" described in the NetReady
requirements document [1] and was adapted for Gluon.


General Design Paradigm
-----------------------

The fundamental goal of this design paradigm is to clearly separate VM ports
from services and define how services bind to particular VM ports.
Specifically, there are four basic entities:

 i)   baseports,
 ii)  interfaces,
 iii) services, and
 iv)  service bindings.

It is important to note that baseports and interfaces are concrete objects
which exist in Gluon. In contrast, services and service bindings are logical
concepts which represent templates for new service APIs.


Ports and Interfaces
''''''''''''''''''''

* **baseports**

  A baseport object represents a vNIC of a VM, that is, the hand-off point
  between a network and a VM instance. It hence comprises all required
  binding information for Nova.

  Baseports are service-independent and hence exist in Gluon as generic
  entities. They do not need to be defined in service YAML models. 

  Attributes: Since a baseport represents a layer 2 device, its attributes
  include the MAC address, MTU and others in addition to a list of references
  to interfaces. See the example YAML model below.


* **interface**

  An interface is a virtual entity located logically on top of a baseport. Its
  purpose is to separate the traffic traversing a baseport according
  to a specific configurable layer 2 segmentation mechanism (e.g., VLAN, VxLAN,
  etc.). Conceptually, interfaces are hence similar to virtual VLAN interfaces
  in Linux which are defined on top of a NIC.

  Network services bind to interfaces by means of a service-binding (see below).
  Hence, the interface concept allows for binding multiple different network
  services to the same baseport (vNIC) - each service separated by a specific
  layer 2 segmentation mechanism and its configuration (ID).

  Interfaces are service-independent and hence exist in Gluon as generic
  entities. They do not need to be defined in service YAML models. 

  Interfaces store a pointer to a parent object. This can be either a baseport
  or another interface. The latter allows for building hierarchies of
  encapsulation mechanisms if needed.

  Attributes: Layer 2 segmentation mechanism and its configuration, e.g. VLAN
  and VLAN ID, VxLAN and VNI.


Service templates
'''''''''''''''''

* **services**

  A service object represents a specific networking service, for example a L2
  network, a L3VPN or a service-chaining service.

  Attributes: The attributes of the service objects are service specific and
  valid for a given service instance. See the YAML definition of a L3VPN service
  below.


* **service-bindings**

  A service-binding binds a networking service to a specific interface. It hence
  comprises at least two attributes: a reference to an interface and a reference
  to a service. In addition, it can comprise attributes which are specific to a
  service **and** an interface .

  A service-binding is **not** an extension of a baseport or interface 
  (no inheritance). Instead, it is a separate entity. Modeling the binding as a
  separate entity instead of encoding it in the interface or baseport object has
  the following advantages:

  i) It allows for dynamically binding and unbinding a service while keeping the
     VM and its port untouched. This simplifies VM migration across hosts as well
     as the migration of VMs between different network services and backends.

  ii) This entity allows for encapsulating service specific attributes which are
      specific to a port/interface but shall not be part of the baseport or
      interface. For example, in a L3 service, the IP address of the interface
      bound to the service can be specified here whereas this is not required
      for a pure L2 service.



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
        
        #
        # to be replaced/extended by the interface model
        #
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



The **interface** object is service independent and logically located on top of a
baseport::

 interface:
    api:
      name: interfaces
      parent:
        type: root
    attributes:
        id:
            type: uuid
            primary: 'True'
            description: "UUID of the interface"
        parent
            type: uuid
            description "UUID of the parent baseport or interface"
        encap-type:
            type: string
            length: 32
            description: "the encapsulation type used (VLAN, VxLAN, etc.)"
        encap-id:
            type: integer
            description: "the ID used by the encap mechanism (VLAN ID, VxLAN VNI)"



The l3vpn-service model defines a L3VPN **service**. It hence comprises all
attributes relevant to this specific type of service. In order to avoid
duplications among attributes, a separate vpn-af-config entity is defined as
well.::

 l3vpn-service:
    api:
      name: l3vpns
      parent:
        type: root
    attributes:
        id:
            type: uuid
            primary: 'True'
            description: "UUID of a L3VPN service instance"
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
      name: l3vpnbindings
      parent:
        type: root
    attributes:
        id:
            type: 'interface'
            required: True
            primary: True
            description: "Pointer to an instance of an interface (UUID)"
        vpn_instance:
            type: 'l3vpn-service'
            required: True
            description: "Pointer to an instance of a VPN (UUID)"


References
[1] NetReady - Service Binding model: http://artifacts.opnfv.org/netready/colorado/docs/requirements/index.html#service-binding-design-pattern
