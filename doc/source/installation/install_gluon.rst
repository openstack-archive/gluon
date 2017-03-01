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

**STEP-1**: Clone Gluon Repository ``stable/ocata`` branch:

.. code-block:: bash

    $ cd ~
    $ git clone https://github.com/openstack/gluon.git -b stable/ocata

**STEP-2**: Create user and group for gluon and proton users

.. code-block:: bash

    $ sudo adduser --system --group proton

**STEP-3**: Create directories

.. code-block:: bash

    $ sudo mkdir /opt/proton
    $ sudo chown proton /opt/proton
    $ sudo mkdir /etc/proton

**STEP-4**: Setup ``iptables``

.. code-block:: bash

    $ sudo iptables -A INPUT -p tcp -m multiport --ports 2705 -m comment --comment gluon -j ACCEPT
    $ sudo invoke-rc.d iptables-persistent save

    # Note: for Ubuntu 16.04, you may have to use netfilter-persistent as follows:
    # sudo apt-get install netfilter-persistent
    # sudo invoke-rc.d netfilter-persistent save

**STEP-5**: Create config files and set permissions

.. code-block:: bash

    $ sudo cat > /etc/proton/proton.conf <<EOF
    [DEFAULT]
    state_path = /opt/proton
    EOF

    $ sudo chown -R proton /etc/proton
    $ sudo chmod -R go+w /etc/proton

**STEP-6**: Install Gluon package

.. code-block:: bash

    $ cd ~/gluon
    $ python setup.py build
    $ sudo python setup.py develop
    $ sudo python setup.py install

**STEP-7**: Setup service for ``proton-server``

.. code-block:: bash

    $ sudo cp ~/gluon/scripts/proton-server.conf /etc/init
    $ sudo start proton-server

**STEP-8**: Test installation

You should now have the ``proton-server`` running. Test by running the
following command:

.. code-block:: bash

    $ protonclient baseport-list
    # The output should look like:
    []

**STEP-9**: Modify ``neutron.conf`` to point to the ``gluon plugin``

.. code-block:: bash

    # Edit /etc/neutron/neutron.conf. Change the core_plugin:
    core_plugin = gluon.plugin.core.GluonPlugin

**STEP-10**: Restart ``neutron-server``

.. code-block:: bash

    $ service neutron-server restart

Or in a devstack environment, do the following:

.. code-block:: bash

    # do "screen -x"
    # goto the screen for q-svc
    # do "Ctrl C" to kill the service
    # use arrow key to recollect the previous command and enter

**STEP-11**: Create Gluon Dummy Objects in Neutron:

.. code-block:: bash

    # Source the openrc file for the admin user (depends on your system)
    # Create the dummy Gluon Network:
    $ neutron net-create --shared --provider:network_type local GluonNetwork

    # Create the dummy GluonSubnet:
    $ neutron subnet-create --name GluonSubnet --no-gateway --disable-dhcp GluonNetwork 0.0.0.0/1

**STEP-12**: Restart ``neutron-server``

.. code-block:: bash

    service neutron-server restart

** The controller should be setup now**

**STEP-13**: Running the Sample Shim Layer Server

Please refer to vendor documentation for specific implementations and
installation procedure.

A test shim server is included in the gluon package. You need to:

.. code-block:: bash

    # Modify host list for shim server
    # Create br-gluon bridge

References

.. [1] install_etcd

