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
Install Proton Server
======================================

Here are the steps to install the Proton server in a local VM.
These are the steps copied from the install_gluon.rst file with some modifications on 
requirements.txt file to solve the different kind of oslo dependency issues araise 
during the proton server installation. 
In the future, we will need to update the requirements.txt file, sort out the various 
oslo library dependencies, and this file will be removed. The intall_gluon.rst file is 
the only one that is needed for install proton server. 

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

**STEP-6**: install requirements

Modify the requirements.txt file to set the list of oslo versions, pbr version and request version.
pbr>=2.0 # Apache-2.0
oslo.db==4.13.5 # Apache-2.0
oslo.versionedobjects==1.17.0 # Apache-2.0
oslo.config==3.17.1 # Apache-2.0
oslo.policy==1.14.0 # Apache-2.0
oslo.log==3.16.0 # Apache-2.0
oslo.utils==3.23.0 # Apache-2.0
oslo.i18n==3.9.0 # Apache-2.0
oslo.middleware==3.19.0
.
.
requests==2.10.0 # Apache-2.0

Then call the command below to manually install all the requirements. 
After installing all the requirements, make sure to COMMENT OUT all
the oslo libraries in the requirements.txt file before moving to the next step.
Otherwise, calling "sudo python setup.py develop" will throw out various oslo 
dependency issues. 

.. code-block:: bash

    $ sudo pip install -r requirements.txt

**STEP-7**: Install Gluon package

.. code-block:: bash

    $ cd ~/gluon
    $ python setup.py build
    $ sudo python setup.py develop
    $ sudo python setup.py install

**STEP-8**: Setup service for ``proton-server``
Open a new terminal and run this commands
.. code-block:: bash
    
    $ sudo mkdir /var/log/proton
    $ sudo /usr/local/bin/proton-server --config-file /etc/proton/proton.conf --logfile /var/log/proton/api.log
    

**STEP-9**: Test installation

You should now have the ``proton-server`` running. Test by running the
following command:

.. code-block:: bash

    $ protonclient baseport-list
    # The output should look like:
    []


