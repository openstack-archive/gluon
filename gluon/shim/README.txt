OVERVIEW:

This directory contains an example shim layer server.  A dummy backend implementation
is provided to show how changes in the net-l3vpn model can be turned into events to
configure the underlying SDN controller.

The shim layer server recursively watches for changes to keys in the /proton directory.
It will receive changes to keys in the following directories:

/proton/net-l3vpn/ProtonBasePort
/proton/net-l3vpn/VPNPort
/proton/net-l3vpn/VpnInstance
/proton/net-l3vpn/VpnAfConfig

NOTE: This is a change from the previous implementation where it watched for changes in
the /net-l3vpn/proton directory.

When changes are detected in etcd, the net_l3vpn api model is called to process
the object change.  The net_l3vpn class will maintain an in-memory model of the etcd
database.  As changes are made to the model, callbacks will be made to the registered
backend to handle the following operations:

bind_port
unbind_port
modify_port
delete_port
modify_service
delete_service
modify_service_binding
delete_servcie_binding

The dummy_net_l3vpn class just prints out logging information when the callbacks
are called.  The idea is that a vendor could copy/paste the dummy_net_l3vpn class and
add the code to configure their SDN controller based on the callback and model data.

The bind_port() callback shows how to pass back vif_type and vif_details to be updated in
the ProtonBasePort instance.  This is done by the following protocol:

The bind_port() callback will return a dict containing the vif_tpe and vif_details.

For example: {'vif_type': 'ovs', 'vif_details': {'port_filter': False, 'bridge_name': 'br-gluon'}}

The net_l3vpn class (which maintains the model and invokes the callbacks) will create an entry
in etcd to provide this information back to the proton-server.  It will also create a field
for the controller name that handled the bind request.

The etcd key will be of the form:

/controller/net-l3vpn/ProtonBasePort/<uuid>

The data will look like:

{ 'vif_type': 'ovs',
  'vif_details': {'port_filter': False, 'bridge_name': 'br-gluon'},
  'controller': 'SimServer'
}

The proton-server will watch on this key for up to 8 seconds after the Port object is updated for
a bind request.  If it sees that the key's value has been changed, it will update the Port
database object with the vif_type and vif_details. So, when Nova subsequently retrieves the Port
information  during the VM creation it will have the correct vif_type and vif_details to give to
the VIF driver.

INSTALLATION:

The shimserver script is installed in /usr/local/bin when the gluon package is installed.
The only thing that has to be configured is the host_list.  The shim server will only
respond to bind requests for a host_id that is in this list.  Look at the shim.conf file
in this directory for an example.  You should query nova for the hypervisor list and populate
the host_list with the proper values.

To run the shimserver:

/usr/local/bin/shimserver --cofig-file=/<path>/shim.conf

Logging goes to stdout by default.


