Installation
============

Recommended way of having Contrail working with gluon is to install Contrail on a separate node and configure it to use Keystone from Gluon's OpenStack. Then deploy ContrailMechanismDriver on Gluon node.

This documment is instruction of how to configure ContrailMechanismDriver and a summary of Contrail installation. Whole instruction is available here: https://github.com/codilime/ContrailMechanismDriver.

1. Deploy Contrail Mechanism Driver
Contrail Mechanism Driver code is available here: https://github.com/codilime/ContrailMechanismDriver.
Clone repository 
```sh
git clone https://github.com/codilime/ContrailMechanismDriver
```
then copy directory `ContrailMechanismDriver/neutron` into `/usr/lib/python2.7/dist-packages/`.

2. Install Dependencies
* https://github.com/Juniper/contrail-python-api

3. Configure Contrail Mechanism Driver
	* In file `/etc/neutron/plugins/ml2/ml2_conf.ini`
		* Make sure that in section *ml2* key *mechanism_drivers* have value **contrail_driver** in list
		* Add section `ml2_driver_contrail` and point to contrail controller node:
			- key *controller* should contain Contrail controller address (default: 127.0.0.1)
			- key *port* should point to Contrail controller listen port (default: 8082)
	* Make sure that neutron-server reads `ml2_conf.ini` file during startup (this might require to modify `/etc/init.d/neutron-server` file and add `--config-file=/etc/neutron/plugins/ml2/ml2_conf.ini` to **DAEMON_ARGS** variable
	* In file `entry_points.txt` (location depends on neutron version and OpenStack installation method) in section *neutron.ml2.mechanism_drivers* set key *contrail_driver* to **neutron.plugins.ml2.drivers.contrail_driver:ContrailMechanismDriver**
		* For Fuel based installations: /usr/lib/python2.7/dist-packages/neutron-<version>.egg-info/entry_points.txt
		* For devstack based installations: /opt/stack/neutron/neutron.egg-info/entry_points.txt
4. Neutron service need to be restarted.
