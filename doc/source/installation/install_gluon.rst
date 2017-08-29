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

======================================
Install Gluon Plugin and Proton Server
======================================

Here the assumption is that ``etcd`` cluster is already installed. Otherwise,
please refer to [1]_.

On Controller
-------------

Assume the user logged in with sudo privileges.  On an Ubuntu system:

**STEP-1**: Clone Gluon Repository ``stable/pike`` branch:

.. code-block:: bash

    $ cd ~
    $ git clone https://github.com/openstack/gluon.git -b stable/pike

**STEP-2**: Create user and group for gluon and proton users

.. code-block:: bash

    $ sudo adduser --system --group proton

**STEP-3**: Create directories

.. code-block:: bash

    $ sudo mkdir /opt/proton        # Proton working directory, for such as gluon.sqlite
    $ sudo mkdir /etc/proton        # Proton configuration directory, for such as proton.conf
    $ sudo mkdir /var/log/proton    # Proton logs

**STEP-4**: Setup ``iptables``

.. code-block:: bash

    $ sudo iptables -A INPUT -p tcp -m multiport --ports 2705 -m comment --comment gluon -j ACCEPT
    $ sudo invoke-rc.d iptables-persistent save

    # Note: for Ubuntu 16.04, you may have to use netfilter-persistent as follows:
    # sudo apt-get install netfilter-persistent
    # sudo invoke-rc.d netfilter-persistent save

**STEP-5**: Create config files and set permissions

.. code-block:: bash

    #
    # Copy ~/gluon/etc/proton/proton.conf to /etc/proton/proton.conf
    #

    $ sudo cp ~/gluon/etc/proton/proton.conf /etc/proton/

    # After copying proton.conf, if you do not plan to use RBAC (Role-based Access Control) in Gluon,
    # please modify proton.conf by changing "auth_strategy" to "noauth" in [api] section. i.e:
    #
    # [api]
    # auth_strategy = noauth
    #

    $ sudo chown -R proton:proton /opt/proton
    $ sudo chown -R proton:proton /etc/proton
    $ sudo chown -R proton:proton /var/log/proton
    $ sudo chmod 750 /etc/proton
    $ sudo chmod 644 /etc/proton/proton.conf
    $ sudo chmod 750 /var/log/proton

**STEP-6**: Install Gluon package

.. code-block:: bash

    $ cd ~/gluon
    $ sudo pip install -r requirements.txt
    $ python setup.py build
    $ sudo python setup.py develop
    $ sudo python setup.py install

**STEP-7**: Setup service for ``proton-server``

If you use a Linux distribution which makes use of upstart (e.g. Ubuntu 14.10
and earlier), you can utilize an upstart script to define a system service for
the proton-server:

.. code-block:: bash

    $ sudo cp ~/gluon/scripts/proton-server.conf /etc/init
    $ sudo start proton-server

For distributions using other startup frameworks, either you need to create a
framework specific service definition file or start the proton-server manually
as follows:

.. code-block:: bash

   $ sudo /usr/local/bin/proton-server --config-file /etc/proton/proton.conf --logfile /var/log/proton/api.log

**STEP-8**: Test installation

You should now have the ``proton-server`` running. Test by running the
following command:

.. code-block:: bash

    $ protonclient --api net-l3vpn port-list
    # The output should look like:
    {
        "ports": []
    }

**STEP-9**: Modify ``neutron.conf`` to point ``core_plugin`` to the ``gluon.plugin.core.GluonPlugin``

.. code-block:: bash

    # Edit /etc/neutron/neutron.conf. Change the core_plugin:
    core_plugin = gluon.plugin.core.GluonPlugin

**STEP-10**: Restart ``neutron-server``

.. code-block:: bash

    $ service neutron-server restart

Or in a devstack environment, do the following:

.. code-block:: bash

    $ service devstack@q-svc restart

    # Alternatively, you can do:
    # do "screen -x"
    # goto the screen for q-svc
    # do "Ctrl C" to kill the service
    # use arrow key to recollect the previous command and enter

**STEP-11**: Create Gluon Dummy Objects in Neutron:

.. code-block:: bash

    # Source the openrc file for the admin user (depends on your system)
    # Create the dummy Gluon Network:
    $ openstack network create --share --provider-network-type local GluonNetwork

    # Or legacy way:
    # neutron net-create --shared --provider:network_type local GluonNetwork

    # Create the dummy GluonSubnet:
    $ openstack subnet create --network GluonNetwork --no-dhcp --gateway none --subnet-range 0.0.0.0/1 GluonSubnet

    # Or legacy way:
    # neutron subnet-create --name GluonSubnet --no-gateway --disable-dhcp GluonNetwork 0.0.0.0/1

**STEP-12**: Restart ``neutron-server``

.. code-block:: bash

    service neutron-server restart

    # Or in Devstack:
    $ service devstack@q-svc restart

** The controller should be setup now**

**STEP-13**: Running the Sample Shim Layer Server

Please refer to vendor documentation for specific implementations and
installation procedure.

A test shim server is included in the gluon package. You need to:

.. code-block:: bash

    # Modify host list for shim server
    # Create br-gluon bridge

Role-based Access Control of Gluon
----------------------------------

After we complete the basic setups as instructed above,
Advanced users may also want to enable RBAC feature in Gluon.
Please refer to [2]_ for the basic concept, and how to configure
and enable RBAC in Gluon. Here is the summary of steps:

* RBAC-1: Create a new "NFV Networking" **service** named ``gluon``
  with service type ``nfvnet``

.. code-block:: bash

    $ openstack service create --name gluon --description "NFV Network Service" nfvnet

* RBAC-2: Create a new **endpoint** under the **service** ``gluon``

.. code-block:: bash

    # Note: you need to change the IP address 10.0.2.7 to match your environment

    $ openstack endpoint create --region RegionOne gluon public http://10.0.2.7:2705/proton/
    $ openstack endpoint create --region RegionOne gluon admin http://10.0.2.7:2705/proton/
    $ openstack endpoint create --region RegionOne gluon internal http://10.0.2.7:2705/proton/

* RBAC-3: We reuse an existing **project** named ``service``

.. code-block:: bash

    #
    # If you want to create a new project:
    #     $ openstack project create --description <description of your new project> <new-project-name> --domain default
    #

* RBAC-4: Create a new **user** named ``gluon`` and password ``gluon``

.. code-block:: bash

    $ openstack user create --password gluon gluon

* RBAC-5: Assign ``admin`` **role** to { ``service``, ``gluon`` } pair

.. code-block:: bash

    $ openstack role add --project service --user gluon admin

* RBAC-6: Set environment variables

.. code-block:: bash

    # Modify the ``openrc`` file in Gluon home directory (or in``devstack`` home directory)
    # with the appropriate value for you Keystone endpoint, your project name/tenant name,
    # your user name and password. Then run the following command to set these variables.
    #
    #     $ source openrc <project_name> <user_name> <user_password>

    $ source openrc service gluon gluon

* RBAC-7: Add the following configuration in ``/etc/proton/proton.conf``. Note that the
  ``project_name``, ``username`` and ``password`` must match what you have created/used
  in prior steps.

.. code-block:: ini

    [api]
    auth_strategy = keystone

    [keystone_authtoken]
    auth_uri = http://10.0.2.7:5000
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = gluon
    username = gluon
    auth_url = http://10.0.2.7:35357
    auth_type = password

* RBAC-8: If policies are defined in YAML, those policies will be applied.
  Otherwise, default policies defined in ``gluon/models/base/base.yaml`` will be used.

* RBAC-9: Restart ``proton-server``

.. code-block:: bash

   $ sudo /usr/local/bin/proton-server --config-file /etc/proton/proton.conf --logfile /var/log/proton/api.log

* RBAC-10: Get token using curl or OpenStack CLI:

.. code-block:: bash

    #
    # Use curl
    #
    $ curl -s -X POST http://192.0.2.4:5000/v2.0/tokens \
      -H "Content-Type: application/json" \
      -d '{"auth": {"tenantName": "'"$OS_TENANT_NAME"'", \
           "passwordCredentials": {"username": "'"$OS_USERNAME"'", \
                                   "password": "'"$OS_PASSWORD"'"}}}' \
      | python -m json.tool

    #
    # Or use OpenStack CLI
    #

    $ openstack token issue

* RBAC-10: Now you can access Proton server with token

.. code-block:: bash

    #
    # Note: you need to replace the exemplary token value with your own token value
    #       and replace the Proton server URL with your own URL
    #

    $ curl -s -H "X-Auth-Token: 1678f8ef3a97497b842f0f7088b0b090" http://192.0.2.4:2705 | python -m json.tool

    #
    # Get a specific port information
    # Note you also need to replace the exemplary port-id with your own port-id
    #

    $ curl -s -H "X-Auth-Token: 1678f8ef3a97497b842f0f7088b0b090" http://192.0.2.4:2705/proton/net-l3vpn/v1.0/ports/30f12741-ffe8-4c85-819b-04a496251f00

* RBAC-11: At this moment, RBAC should work fine now. You need to make sure that
  "X-Auth-Token: <auth-token>" header is always added in your RESTful http request.

References

.. [1] install_etcd
.. [2] ../devref/gluon-auth.inc
