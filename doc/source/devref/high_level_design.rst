..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

      Convention for heading levels in Gluon devref:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

=================
High Level Design
=================

Summary
-------

**Gluon** brings a Networking Service Framework that enables Telecom Service
Providers to provide their customers with networking services on-demand.
**Gluon** uses a model-driven approach to generate Networking Service APIs
(including objects, database schema, and RESTful API endpoints) from a YAML
file which models the Networking Service. When a Telecom Service Provider needs
to launch a new Networking Service, it only needs to model the new service in a
YAML file. The **Gluon** framework generates the APIs accordingly. Thus
**Gluon** helps Telecom Service Providers accelerate the time-to-market and
achieve business agility through its extensibility and scalability in
generating APIs for new use-cases and services.

Gluon
-----

**Gluon** is the port arbiter that maintains a list of ports and bindings of
different networking backends. A **Proton Server** is the API server that hosts
multiple **Protons**, i.e. multiple sets of APIs. **Gluon** uses backend
drivers to interact with the **Proton Server** for port binding and other
operations. The backend drivers are specified in ``setup.cfg``, and loaded
at runtime.

For example, the driver for **L3VPN** is named ``net-l3vpn``, and implemented
in ``gluon.backends.models.net_l3vpn:Provider``. This driver in turn updates
the ``Port`` object which is stored in the **Proton Server's** object
database upon the ``bind``, ``unbind`` and other operations.

When the **Proton Server** receives port binding and other operations requests,
it broadcasts those requests to ``etcd``. The **Shim Layers** of respective SDN
Controllers listen to ``etcd``, and get the notification from ``etcd``. Based
on the type of operations, parameter data, and its own deployment and policy
configuration, SDN Controllers act upon accordingly. This mechanism is similar
to Neutron's Hierarchical Port Binding (HPB), and provides the flexibility and
scalability when a port operation needs to be supported by multiple SDN
Controllers in collaborative and interoperable way.

Integration with Neutron
~~~~~~~~~~~~~~~~~~~~~~~~

**Gluon** currently integrates with Neutron by means of extending Neutron's
core plugin as a subclass, namely **Extended ML2 Plugin for Gluon** (a.k.a.
Gluon Wrapper Plugin). This replaces the original Neutron's core plugin in
``neutron.conf``. The **Gluon Plugin** differentiates **Proton** ports from
Neutron ports based on a Proton's record in ``etcd``, and sends the port
binding and other operations requests to either **Proton Server** or its
superclass (i.e. the original Neutron's core plugin).

Proton and Proton Server
------------------------

A **Proton** is a set of  APIs of a particular NFV Networking Service. 

A **Proton Server** is the API server that hosts multiple **Protons**, i.e.
multiple sets of APIs.

A **Proton** is created by **Particle Generator** based on a YAML file modeled
for this particular NFV Networking Service. When a **Proton** is created, the
objects, database schema, and RESTful APIs of this **Proton** are created. Then
the **Proton** specific driver would be loaded into **Gluon**.  In case of
L3VPN ``net-l3vpn``, the driver is ``gluon.backends.models.net_l3vpn:Provider``.

Currently the ``net-l3vpn`` driver is created manually. Automation of this could
be future work.

A port, namely ``port``, is created when an application uses the northbound
RESTful API of the **Proton**. The **Proton** will store the port and all
related information in its database and update the record in ``etcd``. The
**Shim Layers** of respective SDN Controllers listen to ``etcd``, and get the
notification from ``etcd``. Then the **Shim Layer** will pick up the
information from ``etcd``.

The ``ports`` can be viewed using the command:

.. code-block:: bash
    $ protonclient --api net-l3vpn port-list

As previously mentioned, when a ``bind`` operation is requested, Gluon uses the
driver of ``net-l3vpn`` to bind a port to a VM.

Proton of L3VPN
~~~~~~~~~~~~~~~

When an L3VPN is created through a L3VPN **Proton**, the Proton creates a
``vpn`` object and stores it in its database.  This can be viewed using the
command:

.. code-block:: bash

    $ protonclient --api net-l3vpn vpn-list

Furthermore, the API of the L3VPN allows for creating service bindings between
a ``port`` and a ``vpn`` service. This service binding, namely ``vpnbinding``,
can be viewed using the command:

.. code-block:: bash

    $ protonclient --api net-l3vpn vpnbinding-list

All objects (``interfaces``, ``vpns``, ``ports``, and ``vpnbindings``) are
stored into the **Proton Server's** database.  This information is then copied
into ``etcd``. The **Shim layers** monitor the ``etcd`` data store and take
appropriate actions in the networking backend upon an update. Currently,
**Proton Server** database is not HA, but it can be stored in the same database
backend as the other OpenStack services, thereby inheriting the same level of
HA as those services.

Networking Backends (SDN Controllers)
-------------------------------------

A **Proton** is built to enable the set of APIs for a particular NFV Networking
service that is supported by one or multiple networking backends. A
networking backend can be considered Open Daylight, or others. A **Shim Layer**
is created for a networking backend to be able to use the **Proton**. The
**Shim Layer** monitors changes in the data model stored in ``etcd``, and
performs appropriate actions in the respective SDN Controller backend, for
instance creating a VPN service or binding a port. In an example of using Open
Daylight, if a ``bind`` operation request occurs, the **Shim Layer** is
responsible for understanding the request in the data model and updating the
Flow Entries on the OVS of that particular compute where the Virtual Machine
resides.

The data model of **Shim Layer**, e.g. L3VPN, and respective backend drivers of
**ShimLayer** for specific SDN Controllers are specified in ``setup.cfg``, and
loaded at runtime.
