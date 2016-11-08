==============================
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
requirements document [1]_ and was adapted for Gluon.

The modeling tools in Gluon provide building blocks to allow the creation of
arbitrarily complex networking APIs.  However, some constraints are needed to
enforce model consistency and to ensure interworking with the rest of the
Openstack system.  This document describes the base objects that provide the
building blocks for defining new API objects and the relationship constraints
enforced by the system.

Objects and Relationships
-------------------------

The fundamental goal of this design paradigm is to clearly separate VM ports
from services and define how services bind to particular VM ports.
Specifically, there are four basic entities:

 i)   ports,
 ii)  interfaces,
 iii) services, and
 iv)  service bindings.


* **Port**

  A Port object represents a vNIC which is bindable to an OpenStack instance by
  the compute service (Nova). It hence comprises all required information for
  defining the hand-off point between a network and a VM instance.  Other
  services may in the future bind to ports (today, this happens within Neutron
  to bind things like routers and DHCP services in the ML2 world).

* **Interface**

  An interface is a logical entity which specifies a traffic segmentation
  mechanism (i.e., VLAN, VxLAN, GRE). Interfaces sit on top of ports and
  services are bound to interfaces instead of ports. Hence, interfaces allow
  for binding multiple (incompatible) services to a single port.

  When a Port is created, a corresponding default Interface object is
  automatically created for un-segmented traffic.  The UUID of this default
  interface will be the same as the UUID of the parent Port.  Additional
  Interface objects created for the Port will have unique UUID identifiers.

* **Service**

  A Service object represents a specific networking service, for example a L2
  network, a L3VPN or a service chaining service.

* **Service Binding**

  A Service Binding object binds a networking service to an Interface object.
  It has at least two attributes: a reference to an Interface and a reference
  to a Service. In addition, it can comprise attributes which are specific to a
  Service **and** an Interface.

  A Service Binding is **not** an extension of an Interface (no inheritance).
  Instead, it is a separate entity. Modeling the binding as a separate entity
  instead of encoding it in the Interface object has the following advantages:

  i) It allows for dynamically binding and unbinding a Service while keeping
  the VM and its port untouched. This simplifies VM migration across hosts as
  well as the migration of VMs between different network services and backends.

  ii) This entity allows for encapsulating service specific attributes which
  are specific to an Interface but that are not part of the Interface. For
  example, in a L3 service, the IP address of the interface bound to the
  service can be specified here whereas this is not required for a pure L2
  service.

The following diagram shows the relationship between these objects:

::


                                         +-----------+
                                         |           |
                                         |   Port    |
                                         |           |
                                         +-----+-----+
                                               | 1
                                               |
                                               |
                                               |
                                               | *
                 +-----------+           +-----+-----+
                 |  Service  | *       1 |           |
                 |  Binding  +-----------+ Interface +
                 |           |           |           |
                 +-----+-----+           +-----------+
                       | 1
                       |
                       |
                       |
                       |
                       | 1
                 +-----+-----+
                 |           |
                 |  Service  |
                 |           |
                 +-----------+


Base Object Definitions
-----------------------

These are the base objects for defining APIs.  These objects cannot be used
directly in an API definition.  They must be used as the base object for
objects of similar type.  There is an **"extends"** keyword in the
YAML model to provide this capability.  To have a functional networking API,
one must extend the ``BasePort``, ``BaseInterface``, ``BaseService`` and 
``BaseServiceBinding`` objects.  It is not required that additional attributes
are defined for the extended objects.  See the Interface definition in the
example_ at the end of this document.

In addition, you can also define objects that do not extend any of the base
objects.  The proton server will provide CRUD functions on these objects but it
will not ensure any model consistency.  However, objects that are extensions of
base objects will be examined to ensure model consistency.  For example, the
proton server will have logic to validate that a Service Binding object
references only valid Interface and Service objects.

**BasePort**

  The ``BasePort`` object must be extended in an API model.  This base object
  contains all of the attributes needed by Nova to bind the Port to a VM.  The
  extended object may contain additional attributes needed by the API model
  (but not Nova).  Note, the extended object does not have to define additional
  attributes.

::

  BasePort:
      attributes:
          id:
              type: uuid
              primary: true
              description: "UUID of Port instance"
          name:
              type: string
              length: 64
              description: "Descriptive name for Port"
          tenant_id:
              type: uuid
              required: true
              description: "UUID of Tenant owning this Port"
          mac_address:
              type: string
              length: 17
              required: true
              description: "MAC address for Port"
              validate: mac_address
          admin_state_up:
              type: boolean
              required: true
              description: "Admin state of Port"
          status:
              type: enum
              required: true
              description: "Operational status of Port"
              values:
                  - 'ACTIVE'
                  - 'DOWN'
          vnic_type:
              type: enum
              required: true
              description: "Port should be attache to this VNIC type"
              values:
                 - 'normal'
                 - 'virtual'
                 - 'direct'
                 - 'macvtap'
                 - 'sriov'
                 - 'whole-dev'
          zone:
              type: string
              length: 64
              description: "zone information"
          mtu:
              type: integer
              description: "MTU"
              required: true
          vlan_transparency:
              type: boolean
              description: "Allow VLAN tagged traffic on Port"
              required: true
          profile:
              type: string # JSON Format
              length: 128
              description: "JSON string for binding profile dictionary"
          device_id:
              type: uuid
              description: "UUID of bound VM"
          device_owner:
              type: string
              length: 128
              description: "Name of compute or network service (if bound)"
          host_id:
              type: string
              length: 32
              description: "binding:host_id: Name of bound host"
          vif_details:
              type: string # JSON Format
              length: 128
              description: "binding:vif_details: JSON string for VIF details"
          vif_type:
              type: string
              length: 32
              description: "binding:vif_type: Headline binding type for VIF"

**BaseInterface**

  The ``BaseInterface`` object must be extended in an API model.  A default
  Interface object will automatically be created for each Port object.  Note,
  the extended object does not have to define additional attributes.

::

  BaseInterface:
      attributes:
          id:
              type: uuid
              required: true
              primary: true
              description: "UUID of Interface instance"
          port_id:
              type: uuid
              required: true
              description: "Pointer to Port instance"
          segmentation_type:
              type: enum
              required: true
              description: "Type of segmention for this interface"
              values:
                 - 'none'
                 - 'vlan'
                 - 'tunnel_vxlan'
                 - 'tunnel_gre'
                 - 'mpls'
                 - 'other'
          segmentation_id:
              type: integer
              required: true
              description: "Segmentation identifier"

**BaseService**

  The ``BaseService`` object must be extended in an API model. There can be
  multiple Services defined of a given model.  However, an Interface can only
  be bound to one Service.  Note, the extended object does not have to define
  additional attributes.

::

  BaseService:
      attributes:
          id:
              type: uuid
              required: true
              primary: true
              description: "UUID of Service instance"
          name:
              type: string
              length: 64
              description: "Descriptive name of Service"
          description:
              type: string
              length: 256
              description: "Description of Service"

**BaseServiceBinding**

  The ``BaseServiceBinding`` object must be extended in an API model.  Additional
  attributes can be added to the extended object that are specific for a Port
  bound to the Service. Note, the extended object does not have to define
  additional attributes.

  The ``service_id`` attribute can be re-defined in the extended object to specify
  the specific type of Service that can be bound.  The system will validate
  that the UUID specified for the ``interface_id`` is a known Interface object.  A
  null value is also accepted to effectively "unbind" the interface from the
  service.  The system will also validate that the UUID specified for the
  ``service_id`` is a known Service object.

::

  BaseServcieBinding:
      attributes:
          interface_id:
              type: uuid
              required: true
              primary: true
              description: "Pointer to Interface instance"
          service_id:
              type: uuid
              required: true
              description: "Pointer to Service instance"


Example L3VPN API using proposed model:
---------------------------------------

The following model defines an L3VPN service.  The Port and Interface objects
extend the ``BasePort`` and ``BaseInterface``, respectively.  You can extend an object
without adding attributes.  That is done with the Interface object.  Even if no
attributes are added, you are still required to extend these objects for a
functional API.  You must also extend the ``BaseService`` and ``BaseServiceBinding``
base objects in a similar manner.

Note, the VpnAfConfig object does not extend a base class.  The
modeling tools allow for the creation of arbitrary objects as needed by an API
model.  The proton server will not enforce any constraints on the relationships
between these objects and objects extended from base objects.

.. _example:

::

  Port:
      extends: BasePort
      api:
        name: ports
        parent:
          type: root
      attributes:
          alarms:
              type: string
              length: 256
              description: "Alarm summary for port"

  Interface:
      extends: BaseInterface
      api:
        name: interfaces
        parent:
          type: root

  VpnService:
    extends: BaseService
    api:
      name: vpns
      parent:
        type: root
    attributes:
        ipv4_family:
            type: string
            length: 255
            description: "Comma separated list of route target strings"
        ipv6_family:
            type: string
            length: 255
            description: "Comma separated list of route target strings"
        route_distinguishers:
            type: string
            length: 32
            description: "Route distinguisher for this VPN"

  VpnBinding:
      extends: BaseServiceBinding
      api:
        name: vpnbindings
        parent:
          type: root
      attributes:
          service_id:    # Override from base object for specific Service type
              type: VpnService
              required: true
              description: "Pointer to VpnService instance"
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

  VpnAfConfig:
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



References

.. [1] NetReady - Service Binding model: http://artifacts.opnfv.org/netready/colorado/docs/requirements/index.html#service-binding-design-pattern

