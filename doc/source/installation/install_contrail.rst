..
      Copyright 2017, Juniper Networks

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

=====================
Contrail Installation
=====================

Recommended way of having Contrail working with gluon is to install Contrail
on a separate node and configure it to use Keystone from Gluon's OpenStack.
Then deploy ContrailMechanismDriver on Gluon node.

This documment is instruction of how to configure ContrailMechanismDriver and
a summary of Contrail installation. Whole instruction is available here:
https://github.com/codilime/ContrailMechanismDriver.

#. Deploy Contrail Mechanism Driver
   Contrail Mechanism Driver code is available here:
   https://github.com/codilime/ContrailMechanismDriver.  Clone repository

   .. code-block:: bash
 
      git clone https://github.com/codilime/ContrailMechanismDriver
 
   .. end
 
   then copy directory ``ContrailMechanismDriver/neutron`` into
   ``/usr/lib/python2.7/dist-packages/``.
#. Install Dependencies

   * https://github.com/Juniper/contrail-python-api
#. Configure Contrail Mechanism Driver

   * In file ``/etc/neutron/plugins/ml2/ml2_conf.ini`` 
      - Make sure that in section ``[ml2]`` key ``mechanism_drivers`` have
        value **contrail_driver** in list
      - Add section ``[ml2_driver_contrail]`` and point to contrail controller
        node
      - In section ``[ml2_driver_contrail]`` key *controller* should contain
        Contrail controller address (default is 127.0.0.1)
      - In section ``[ml2_driver_contrail]`` key *port* should point to
        Contrail controller listen port (default is 8082)
   * Make sure that neutron-server reads ``ml2_conf.ini`` file during startup
      (this might require to modify ``/etc/init.d/neutron-server`` file and
      add ``--config-file=/etc/neutron/plugins/ml2/ml2_conf.ini`` to
      :samp:`{DAEMON_ARGS}` variable
   * In file ``entry_points.txt`` (location depends on neutron version and
      OpenStack installation method) in section
      *neutron.ml2.mechanism_drivers*
      set key *contrail_driver* to
      **neutron.plugins.ml2.drivers.contrail_driver:ContrailMechanismDriver**

      - For Fuel based installations: ``/usr/lib/python2.7/dist-packages/neutron-<version>.egg-info/entry_points.txt``
      - For devstack based installations: ``/opt/stack/neutron/neutron.egg-info/entry_points.txt``
#. Neutron service need to be restarted.

