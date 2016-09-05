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

===============
Gluon Task List
===============

---------------------------------
For Infrastructure and Repository
---------------------------------

#. Set up cloud infrastructure with 5 blade servers in Ericsson's new data center
#. Create repos based on new architecture
   #. For now, we need to consolidate everything back int one repo
#. The requirements.txt files needs to be updated and aligned with the Global Requirements

---------------------------------
For Proof-of-Concept in Barcelona
---------------------------------

#. Setup system with base linux bridge networking
#. Use separate SDN-C for each host to support gluon networking
#. Implement Gluon Neutron ML2 Plugin

----------------------------
For Neutron Gluon ML2 Plugin
----------------------------

#. Investigate using subclass of Neutron Core plugin to direct bind/unbind operations to Gluon/Proton

----------------------------------------
For Enhancements of Gluon Implementation
----------------------------------------

#. Investigate how different VIF drivers can be used for different port types on the same hypervisor
   #. Need to understand VIF plugging and how it affects Gluon
   #. Generic VIF driver may be okay for most use cases
#. Investigate and resolve synchronization issues in the gluon/proton architecture
   #. Need to re-sync proton with gluon upon restart
      #. This is partially done
   #. Synchronization of mysql and etcd databases needs to be investigated
      #. Are we covered if Proton restarts or etcd is unavailable for a period of time?
#. Synchronize bind operation with SDN controller
   #. There is no feedback if the SDN bind fails
   #. Need to make sure bind is done before VM is spawned. Synchronize bind with port_update response
   #. Binding information needs to be pushed back to Proton
      #. Should Proton just read this from etcd?
#. Rebuild Gluon to not use particle generator

------------------------------------
For Enhancements of Proton API Model
------------------------------------

#. Fix VPNAFConfig in L3VPN Model (only one reference currently)
#. The API modeling approach needs to be cleaned up
   #. Need a baseport that is common to all APIs
      #. Right now each new API should need to copy/paste baseport object
   #. Binding information needs be be modeled consistently
      #. Separate table or part of baseport?
      #. Or, just resides in etcd?
   #. IP Addressing information should be modeled with a separate table
      #. IPAM is broken with current model.
      #. It is possible to assign IP address that cannot be supported because of SDN-C/Host mapping
#. Proton needs to be reworked to support multiple APIs
#. Create a cookiecutter (or script) to create a new API within the Proton source tree
#. Sync thread needs to be updated to use log table to support Proton HA
#. The Particle Generator only supports flat APIs at this time.
   #. Support for hierarchical APIs was started but not completed.
#. Need consistent way of handling empty/unset fields in the API

-----------------------------
For Proton Database Migration
-----------------------------

#. Modify Proton code to use MySQL (currently only using sqlite)
#. Need a strategy to handle database migrations if the API model is changed

-----------
For Testing
-----------

#. We need to add unit, functional, and tempest testing

-----------------------------------------
For Installer Support (Devstack and Fuel)
-----------------------------------------

#. Need to update devstack code to install Gluon
   #. Install etcd.
   #. Setup database
#. Create Fuel plugin to install Gluon

------------------------
For Keystone Integration
------------------------

#. Need to hook in keystone authorization to access API (wide open now)

