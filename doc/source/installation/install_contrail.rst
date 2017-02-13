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

============
Installation
============

Deploy Contrail Mechanism Driver
--------------------------------

Contrail Mechanism Driver code is available here:

.. code-block:: bash

    https://github.com/codilime/ContrailMechanismDriver.

Please follow the instructions there to deploy Contrail Mechanism Driver.

Install Dependencies
--------------------

Contrail dependency is required: ``https://github.com/Juniper/contrail-python-api``

.. code-block:: bash

    git clone https://github.com/Juniper/contrail-python-api
    cd contrail-python-api
    sudo python setup.py install

Configure Contrail Mechanism Driver
-----------------------------------

* In file ``/etc/neutron/plugins/ml2/ml2_conf.ini``:
	* Make sure that in section **ml2** key ``mechanism_drivers`` have value **contrail_driver** in list

* In file ``/opt/stack/neutron/neutron.egg-info/entry_points.txt``
	* In section **neutron.ml2.mechanism_drivers** set key ``contrail_driver`` to **neutron.plugins.ml2.drivers.contrail_driver:ContrailMechanismDriver**

Running
-------

Neutron service need to be restarted
