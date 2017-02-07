====================================
Gluon Authentication & Authorization
====================================

Summary
-------

This document explains the integration of Gluon with OpenStack identity service
or Keystone. When Keystone is enabled, users that submit requests to Gluon
networking service will have to  provide an authentication token in X-Auth-Token
request header. The token is obtained by making a call to the Keystone authentication
service by passing in username and password.

Assumptions
-----------

The document uses the proposed "port and service binding model"[1] to determine the
policy actions (see section on Authorization).

Authentication
--------------

Authentication is the process of determining that users are who they say they are.
Keystone acts as an authentication proxy which intercepts HTTP calls from clients,
validates the tokens and forwards requests to the OpenStack service.

If the token is valid, Keystone will retrieve additional information from token
such as user name, user id, project name, project id etc and send this information
to the OpenStack service. Otherwise, the request will be rejected.

    Setting up
    ~~~~~~~~~~

    Once Keystone is installed and running, services have to be configured to work with it.
    This involves setting up projects, roles, users, and services. By default, OpenStack
    already has several projects, roles and users created.

    Following is the normal process to add a service to Keystone.

        - Create a project
        - Create a user for the service and add the user to the project
        - Create an admin role and assign to the user
        - Create service
        - Create endpoint

    For Gluon, we will add these objects.

        - Create a new user called "gluon"
        - Add "gluon" user to "service" project
        - Add "service" role to "gluon" user in the "service" project
        - Create a new service called "gluon"
        - Create a new endpoint under the service "gluon"

Authorization
-------------

Each OpenSack service has its own role-based access policies to allow/disallow access to
specific actions. The policy.json is used to define the access control, which contains
each policy defined in the format "<action> : <rule>".

The <action> represents an API call like "create network" whereas <rule> determines
under which circumstances API call is permitted. As an example, consider following rule

``"identity:create_user" : "role:admin"``

This rule allows admin role to create a new user in the identity service.

Authorization Scope
~~~~~~~~~~~~~~~~~~~

It will be possible to specify authorization at object level. In the future, we may allow
setting access control at the attribute level.

Defining authorization rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The YAML model definitions will be enhanced to support authorization rules. We will add a new
section for policies.

The "rules" will be defined at the system level and model authors can use the rules while
defining the actions.

Following will be the default rules:

    "owner": "tenant_id:%(tenant_id)s",
    "admin_or_owner": "rule:context_is_admin or rule:owner",
    "admin_or_network_owner": "rule:context_is_admin or tenant_id:%(network:tenant_id)s",
    "admin_owner_or_network_owner": "rule:owner or rule:admin_or_network_owner",
    "admin_only": "rule:context_is_admin",

The actions are defined within the "policies" section as shown below.

    ProtonBasePort:
        ...
        existing model definition
        ...


        policies:

          actions:
            create:
              role: "rule:admin_or_network_owner"
            delete:
              role: "rule:admin_or_network_owner"
            get:
              role: "rule:admin_or_owner"
            get_one:
              role: "rule:admin_or_owner"
            update:
              role: "rule:admin_or_network_owner"


This policy defines create, delete, get, get_one and update actions on the ProtonBasePort object.
The rules section can embed any openstack policy directive that is supported. Please see
http://docs.openstack.org/kilo/config-reference/content/policy-json-file.html for complete details
of the policy.json file

Converting to policy.json file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During the installation of Gluon, the embedded policies in the YAML model file will be converted
to /etc/gluon/policy.json file. This file will have the following format.

    {
        "context_is_admin":  "role:admin or user_name:gluon",
        "owner": "tenant_id:%(tenant_id)s",
        "admin_or_owner": "rule:context_is_admin or rule:owner",
        "context_is_advsvc":  "role:advsvc",
        "admin_or_network_owner": "rule:context_is_admin or tenant_id:%(network:tenant_id)s",
        "admin_owner_or_network_owner": "rule:owner or rule:admin_or_network_owner",
        "admin_only": "rule:context_is_admin",
        "regular_user": "",
        "default": "rule:admin_or_owner",

        "create_ports": "rule:admin_or_network_owner",
        "get_ports": "rule:admin_or_owner",
        "update_ports": "rule:admin_or_network_owner",
        "delete_ports": "rule:admin_or_network_owner",

        "create_interfaces": "rule:admin_or_network_owner",
        "get_interfaces": "rule:admin_or_owner",
        "update_interfaces": "rule:admin_or_network_owner",
        "delete_interfaces": "rule:admin_or_network_owner",

        "create_vpns": "rule:admin_or_network_owner",
        "get_vpns": "rule:admin_or_owner",
        "update_vpns": "rule:admin_or_network_owner",
        "delete_vpns": "rule:admin_or_network_owner",

        "create_vpnbindings": "rule:admin_or_network_owner",
        "get_vpnbindings": "rule:admin_or_owner",
        "update_vpnbindings": "rule:admin_or_network_owner",
        "delete_vpnbindings": "rule:admin_or_network_owner",

        "create_vpnafconfigs": "rule:admin_or_network_owner",
        "get_vpnafconfigs": "rule:admin_or_owner",
        "update_vpnafconfigs": "rule:admin_or_network_owner",
        "delete_vpnafconfigs": "rule:admin_or_network_owner",
    }


Bootstrapping policy.json
~~~~~~~~~~~~~~~~~~~~~~~~~

In the Devstack environment, the gluon software is installed using "python setup.py install"
command from the gluon directory. The setup script will be enhanced to support creating
/etc/gluon/policy.json file from the YAML model file. Users will be able to edit the generated
policy.json file to add their own local rules even though it is not a recommended approach.

For a production OpenStack environment, the above steps need to be done from the package
installation scripts that are supported by tools such as rpm or dpkg.

Action to API Mapping
~~~~~~~~~~~~~~~~~~~~~

Gluon service has to map actions to respective API calls. The OpenStack keystonemiddleware
and oslo.policy(http://docs.openstack.org/developer/oslo.policy/) modules will be integrated
with Gluon to add keystone authentication and enforce RBAC policies defined in the JSON.policy file.

The pecan-wsgi service in the Neutron will be used as a reference code for Gluon implementation

Configuration 
~~~~~~~~~~~~~
The /etc/proton/proton.conf file can be used to configure the authentication details. A sample
configuration is shown below. 

	[api]
	auth_strategy = keystone

	[keystone_authentication]
	auth_uri = http://127.0.0.1/identity
	project_domain_name = Default
	project_name = service
	user_domain_name = Default
	password = welcome
	username = gluon
	auth_url = http://127.0.0.1/identity_admin
	auth_type = password

	[oslo_policy]
	policy_file = /etc/proton/policy.json

Appendix
--------
Configuring identity details for Keystone:

    1. Create gluon user:

        > openstack user create --name gluon --pass <password>

    2. Add the admin role to the gluon user:

        > openstack user role add --user gluon --tenant service --role admin

    3. Create the gluon service

        > openstack service create --name gluon --type network --description "Gluon"

    4. Create Gluon API endpoints

        > openstack endpoint create —publicurl http://10.0.2.15:2705  \
            —adminurl http://10.0.2.15:2705 —internalurl http://10.0.2.15:2705 \
            —region regionOne gluon

Reference
---------
    1) Port and service binding model - https://review.openstack.org/#/c/392250
