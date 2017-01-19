=================
High Level Design
=================


Summary
-------

Gluon brings a Networking Service Framework that enables Telecom Service
Providers to provide their customers with networking services on-demand. Gluon
uses a model-driven approach to generate Networking Service APIs (including
objects, database schema, and RESTful API endpoints) from a YAML file which
models the Networking Service. When a Telecom Service Provider needs to launch
a new Networking Service, it only needs to model the new service in a YAML
file. The Gluon framework generates the APIs accordingly. Thus Gluon helps
Telecom Service Providers accelerate the time-to-market and achieve business
agility through its extensibility and scalability in generating APIs for new
use-cases and services.


Nova
----

Gluon currently integrates in Nova by means of a Nova network service plugin
mechanism. This replaces the traditional Neutron or Nova-Networking plugins.
The Gluon plugin uses (imports) the Gluon Client (gluonlib Module). The Gluon
Client enables Nova to perform bind and unbind operations between ports and
VMs.  To this end, the Gluon Client uses the Gluon REST API model for
communications between Nova and Gluon.

In the Mitaka release this “plugin mechanism” has been removed allowing Nova
only to communicate to Neutron. This issue will have to be addressed with the
Nova team.


Gluon
-----

Gluon is the port arbiter that maintains a list of ports and bindings of
different networking backends. Inside Gluon there is a backend driver used to
speak to Protons.  Currently this driver for L3VPN is called net_l3vpn. This
driver in turn updates the “base-port” object which is stored in the Proton
object database upon the bind and unbind operations.  There is room for
improvement with the net_l3vpn driver.  A more generic driver should be
created.  This type of port modeling is currently being driven through the
NetReady project in OPNFV.


Proton
------

A Proton is a model driven specification for Networking APIs.  A Proton is
created using a YAML descriptor file fed into the particle generator. As a
result from the particle generator, the Proton containing the objects,
database schema, and REST APIs are created.  A Proton uses the Gluon REST API
to register itself to Gluon.  As a result, the Proton specific drivers would
be loaded into Gluon.  In the L3VPN case this is the net_l3vpn driver.
Currently the net_l3vpn driver is created manually.  Automation of this could
be future work.

A port is created using the northbound REST API of the Proton.  The Proton will
store the port in its database, update etcd and use the Gluon REST API to
register the port in Gluon.  The Shim Layer which is discussed below will pick
up the information from etcd.  This port (base-port information) is stored in
the Proton database itself.  By storing the base-port information inside the
Proton the user is free to “describe” a port however they want.  The
base-ports can be viewed using the :command:`port-list` command.  As
previously mentioned, when a bind action happens Gluon uses the net_l3vpn
driver to bind a baseport to a VM. Currently the base-port model was built
modeling what Neutron requires to ensure compatibility.  For different
use-cases it would be possible to reduce a portion of the base-port model for
layer 3 use-cases.

When a VPN is created through a Proton, the Proton creates the VPN object and
stores this in its database.  This can viewed using the :command:`vpn-list`
command. Furthermore, the API of the L3VPN allows for creating service
bindings between a baseport and a VPN service. These service binding can be
viewed using the :command:`vpnservice-list` command.

All objects (VPNs, Base-ports, and Bindings) are stored into the Proton
database.  This information is then copied into etcd. The shim layers (see
below) monitor the etcd data store and take appropriate actions in the
networking backend upon an update. Currently, the Proton database is not
redundant, but it can be stored in the same database backend as the other
OpenStack services, thereby inheriting the same level of redundancy as those
services.


Networking Backends (SDN Controllers)
-------------------------------------

A Proton is built to enable the API for each networking backend. A networking
backend can be considered OpenDaylight, Neutron or others.  For a networking
backend to be able to use the Proton a shim layer has to be created.  The shim
layer monitors changes in the data model stored in etcd and performs
appropriate actions in the respective SDN controller backend, for instance
creating a VPN service or binding a port. In an example of using
OpenDaylight, if a bind occurs the Shim Layer is responsible for seeing the
request in the data model and updating the Flow Entries on the OVS of that
particular compute where the Virtual Machine resides.
