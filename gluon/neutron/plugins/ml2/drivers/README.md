Installation
============

Dependencies
------------
* https://github.com/Juniper/contrail-python-api
```bash
git clone https://github.com/Juniper/contrail-python-api
cd contrail-python-api
sudo python setup.py install
```

ML2 mechanism driver
--------------------
* In file `/etc/neutron/plugins/ml2/ml2_conf.ini`
	* Make sure that in section *ml2* key *mechanism_drivers* have value **contrail_driver** in list
	* In section *neutron.ml2.mechanism_drivers* set key *contrail_driver* to **neutron.plugins.ml2.drivers.contrail_driver:ContrailMechanismDriver**

Running
=======
Neutron service need to be restarted
