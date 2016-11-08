===========================
Gluon Plugin Wrapper Design
===========================

**Original Gluon Architecture**

In the original design of Gluon, the Gluon Server was placed in the
communication path between Nova and the networking backends.  Its main purpose
was to maintain a mapping of ports to networking backends and to route
port-related requests to the correct backend. See diagram below.

::

                         +-------------------------+
                         |                         |
                         |          Nova           |
                         |                         |
                         |    +---------------+    |
                         |    |     Gluon     |    |
                         |    |     Plugin    |    |
                         +----+---------------+----+
                                      |
                                      | Port Requests
                                      |
                                      v
                         +-------------------------+
                         |                         |
                         |         Gluon           |
     Register Port       |         Server          |       Register Port
     +------------------>|                         |<-------------------+
     |                   |  +---------+---------+  |                    |
     |                   |  | Neutron |  Proton |  |                    |
     |                   +--+---------+---------+--+                    |
     |                           |         |                            |
     |     Neutron Port Requests |         |    Gluon Port Requests     |
     |               +-----------+         +------------+               |
     |               |                                  |               |
     |               |                                  |               |
     |               v                                  v               |
     |  +-------------------------+        +-------------------------+  |
     |  |                         |        |                         |  |
     |  |        Neutron          |        |         Proton          |  |
     +--|         Server          |        |         Server          |--+
        |                         |        |                         |
        +-------------------------+        +-------------------------+

The set of networking backends could be the Neutron Server plus one or more
Proton Servers.  In the original design, each networking backend would register
a new port with the Gluon Server in order to populate the mapping.  When the
Gluon Server received a port-related request, it would look up the port and
then forward the request to the correct backend by calling its associated
client driver.  This  required the Gluon Server to import and manage drivers
for the different types of networking backends.  Another important aspect of
the original design is that the port objects and associated networking service
objects were maintained in each networking backend database.  Hence, the
Neutron Server had no visibility to the ports defined in the Proton Server(s).

In order to get the port-related requests directed to the Gluon Server, the
original design of Gluon replaced the Networking API plugin in Nova with a
modified version of the code that would provide a port-centric model of
networking and forward all requests to the Gluon Server.  In the Mitaka
release, the Networking API plugin in Nova was deprecated allowing Nova to only
communicate with Neutron.  This requires a significant change to the Gluon
design.

**New Gluon Architecture**

This document describes a way to loosely integrate the Gluon Server
functionality into Neutron while minimizing changes to the existing Proton
Server design.  In this proposed design, the Proton Server will remain an API
endpoint and maintain a separate database from the Neutron Server.  Since we
can no longer replace the plugin in Nova, the integration point for Gluon can
be done in the Neutron Server using the Core plugin interface.

The Gluon Wrapper Plugin will subclass off of the ML2 core plugin class  (or
any other Core Plugin class) and override just the port-related methods.  If
the method call is for a Gluon port, the Gluon Wrapper Plugin code will forward
the request to the Proton Server for processing.  Otherwise, the superclass
method will be called.  The goal is to introduce the Gluon networking
functionality without breaking the existing ML2 networking - and to ensure
that a user that doesn't need extended network functionality does not have
to install it and is not affected by Gluon development - the stability of their
system remains as before because the code they're running is no different.
The following diagram provides an overview of this design.

::

                         +-------------------------+
                         |                         |
                         |          Nova           |
                         |                         |
                         |    +---------------+    |
                         |    |    Neutron    |    |
                         |    |   API Plugin  |    |
                         +----+---------------+----+
                                      |
                                      |  Port Requests
                                      |
                                      v
                     +--------------------------------+
                     |            Neutron             |
                     |             Server             |
                     |                                |
                     |      +-------------------+     |
                     |      |+-----------------+|     |
                     |      ||   ML2 Plugin    ||     |
                     |      |+-----------------+|     |
                     |      |   Gluon Wrapper   |     |
                     |      |      Plugin       |     |
                     |      |    +-------------+|     |
                     |      |    |Proton Driver||     |
                     +------+----+-------------++-----+
                              ^         |
                              |         |
        Check Gluon Port      |         | Gluon Port Requests
                  +-----------+         +-----------+
                  |                                 |
                  |                                 |
                  v                                 v
             +---------+               +-------------------------+
             |  etcd   |               |                         |
             |         |               |          Proton         |
             +---------+               |          Server         |
                  ^                    |                         |
                  |                    |                         |
                  |                    |                         |
                  |                    |                         |
                  |                    +-------------------------+
                  |                                 |
                  |                                 |
                  +---------------------------------+
                                         Register Port


The Gluon Wrapper Plugin will determine if a port belongs to Gluon by examining
(looking up the UUID) the etcd database.  The port registration code in the
Proton Server will be changed to also update the etcd database when a new port is
created or deleted. When a port is registered in the etcd database, the
following backend information is stored: tenant identifier, networking service
identifier and Proton Server base URL.  In order to forward the requests to the
Proton Server(s), the same backend driver mechanism will be used by the Gluon
Wrapper Plugin as was used by the Gluon Sever.

Since we can no longer replace the Networking API plugin in Nova, we must
provide a consistent “Neutron” networking model to Nova.   Therefore, we have
to maintain the Network, Subnet and Port associations required by the logic in
the Neutron API plugin (in Nova), at least until we can simplify the Nova-Neutron
communication so that Nova does not need to retrieve subnet and network objects.
In the short term, we can create a “dummy”
Network and Subnet object in the Neutron Server that can be associated with all
Gluon ports.  In the long term, it may be possible to add attributes to the
Network and Subnet objects to change the semantics of the objects to reflect a
more logical association with the Gluon ports.  This document describes the
creation and usage of the Network and Subnet “dummy” objects without any
changes to the existing Neutron model.

The “dummy” Network and Subnet objects need to be created during system turn
up.   The Network and Subnet objects must be uniquely identifiable by the Gluon
Wrapper Plugin.  One approach would be to specify the UUID of these objects in
the configuration file which can be loaded when the Neutron Server starts.
Another approach would be to give the objects unique names that can be
retrieved at runtime.  The Network object needs to be created as a local shared
provider network. The Subnet object created for the Network should have the
gateway and DHCP disabled.  The CIDR should not matter.

**Plugin Processing**

The Gluon Wrapper Plugin only has to intercept and handle the following methods
from the Core plugin base class:

- update_port() - Update port values for bind/unbind operations
- get_port() - Return port values for specific port
- get_ports() - Return a list of ports

The following diagram show the component interaction required to support the
processing of the above requests.


::

          Neutron API

               | update_port()
               | get_port()
               | get_ports()
               |
               v
     +------------------+      Function       +------------------+
     |                  |        Call         |                  |
     |                  |                     |                  |
     |  Gluon Wrapper   |                     |  Proton Backend  |
     |      Plugin      |-------------------->|      Driver      |
     |                  |    bind_port()      |                  |
     |                  |    unbind_port()    |                  |
     +------------------+    get_port()       +------------------+
               |                                        |
               |                                        |
               | read(port)                             |
               | read(directory)                        |   HTTP/REST
               |                                        |
               |                                        |
               v                                        v
         +-----------+                        +------------------+
         |   etcd    |                        |                  |
         |           |                        |                  |
         +-----------+                        |  Proton Server   |
                                              |                  |
                                              |                  |
                                              |                  |
                                              +------------------+

The Neutron API will convert updates to the port object into an update_port()
method call to the Core Plugin.  The port UUID is passed as a parameter to this
method. The Gluon Wrapper Plugin overrides this method and will attempt to read
the corresponding backend information for the port from the etcd database. The
key used is “/gluon/port/<uuid>”.  If no backend information is found, the port
is assumed to be a Neutron port and the superclass update_port() method is
called.  If the backend information is found, the network service identifier is
used to retrieve the backend driver for the specific networking service. The
port values are examined to determine if the port is being bound or unbound.
The host identifier field is used for this determination.  The bind_port() or
unbind_port() method is called on the backend driver.  The backend driver will
convert the "bind/unbind" operation into the appropriate REST calls to a Proton
Server.  It is possible to have multiple Proton Server endpoints. The base URL
from the backend information is used to identify the Proton Server hosting the
networking service API.  It is the responsibility of the backend driver to
collect the response(s) from the Proton Server and reformat the response into
the format expected by the plugin.  In this case, the entire set of port values
is expected in the response. The backend driver will also insert the network_id
and fixed_ips fields in the response to make the object fit in the Neutron
model.  The network_id is the UUID of the “dummy” Gluon Network object.  The
fixed_ips field contains the UUID of the “dummy” Gluon Subnet object with the
IP address taken from the Gluon port (if applicable).

The Neutron API will convert a retrieval of a port object into a get_port()
method call to the Core Plugin.  The port UUID is passed as a parameter to this
method. The Gluon Wrapper Plugin overrides this method and will attempt to read
the corresponding backend information for the port from the etcd database. The
key used is “/gluon/port/<uuid>”.  If no backend information is found, the port
is assumed to be a Neutron port and the superclass get_port() method is called.
If the backend information is found, the network service identifier is used to
retrieve the backend driver for the specific networking service.  The
get_port() method is called on the backend driver.  The backend driver will
convert the “get" operation into the appropriate REST calls to a Proton Server.
It is possible to have multiple Proton Server endpoints. The base URL from the
backend information is used to identify the Proton Server hosting the
networking service API.  It is the responsibility of the backend driver to
collect the response(s) from the Proton Server and reformat the response into
the format expected by the plugin.  In this case, the entire set of port values
is expected in the response. The backend driver will also insert the network_id
and fixed_ips fields in the response to make the object fit in the Neutron
model.  The network_id is the UUID of the “dummy” Gluon Network object.  The
fixed_ips field contains the UUID of the “dummy” Gluon Subnet object with the
IP address taken from the Gluon port (if applicable).

The Neutron API will convert a retrieval of multiple port objects into a
get_ports() method call to the Core Plugin.  An optional filter parameter may
be passed to restrict the list of ports to be returned.  The Gluon Wrapper
Plugin overrides this method and will first call the superclass method to get
the list of Neutron ports meeting the filter criteria.  Next the etcd database
is read to get all of the values in the “/gluon/port” directory.  For each UUID
found, the corresponding backend driver get_port() method is called to retrieve
the port information.  The filter is applied to the port data and if passes the
port is appended to the port list.  The final result is a list of Neutron and
Gluon ports that meet the filter criteria.

**Plugin Usage**

The Gluon package must be installed on the same controller server as the Neutron
package.  The core_plugin option in the neutron.conf has to be changed to
point to the Gluon Wrapper plugin.  For example, edit /etc/neutron.conf and set
core_plugin as follows:

``core_plugin = gluon.plugin.core.GluonPlugin``

Restart the Neutron Server. It should pickup the Gluon Plugin. You can verify
by looking for "gluon" in the neutron server log file.

For now, the GluonPlugin expects the etcd server and Proton Server to be
running on the same server.  This will be changed when configuration parameters
are added to the .conf file.

Before a Gluon port can be used, the "dummy" objects need to be created in
Neutron (as admin).  The names are significant for now.

Create Gluon Network object:

*neutron net-create --shared --provider:network_type local GluonNetwork*

Create Gluon Subnet object:

*neutron subnet-create --name GluonSubnet --no-gateway --disable-dhcp GluonNetwork 0.0.0.0/1*

At this point you should be able to create the objects in the Proton Server and
use nova boot to create a VM using the Gluon port.



