Installation
============

Deploy Contrail Mechanism Driver
--------------------------------
Contrail Mechanism Driver code is available here: https://github.com/codilime/ContrailMechanismDriver.
Please follow the instructions there to deploy Contrail Mechanism Driver.

Install Dependencies
--------------------
* https://github.com/Juniper/contrail-python-api
```bash
git clone https://github.com/Juniper/contrail-python-api
cd contrail-python-api
sudo python setup.py install
```

Configure Contrail Mechanism Driver
-----------------------------------
* In file `/etc/neutron/plugins/ml2/ml2_conf.ini`
	* Make sure that in section *ml2* key *mechanism_drivers* have value **contrail_driver** in list
* In file `/opt/stack/neutron/neutron.egg-info/entry_points.txt`
	* In section *neutron.ml2.mechanism_drivers* set key *contrail_driver* to **neutron.plugins.ml2.drivers.contrail_driver:ContrailMechanismDriver**

Running
=======
Neutron service need to be restarted
