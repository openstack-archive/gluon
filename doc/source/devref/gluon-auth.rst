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

    For Gluon, we will add these objects.

        - Create a new user called "gluon"
        - Add "gluon" user to "service" project
        - Add "service" role to "gluon" user in the "service" project
        - Create a new service called "gluon"

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

It will be possible to specify authorization at object level. This allows a flexible access
control scheme however, the current Gluon model does not differentiate between APIs and objects
(Please see the open issues section). In the future, it will be better if we allow ACL rules
to be defined at the API level rather than at the object level.

Defining authorization rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The YAML model definitions will be enhanced to support authorization rules. We will add a new
section for policies. For example, following rules can be specified in the ProtonBasePort
model.

    ProtonBasePort:
    ...

        policies:
          rules:
            "owner": "tenant_id:%(tenant_id)s",
            "admin_or_owner": "rule:context_is_admin or rule:owner",
            "admin_or_network_owner": "rule:context_is_admin or tenant_id:%(network:tenant_id)s",
            "admin_owner_or_network_owner": "rule:owner or rule:admin_or_network_owner",
            "admin_only": "rule:context_is_admin",

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
of the policy.json file.  It might also be appropriate to provide a blanket 'get' policy for all
gets, single or multiple.

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

        "create_baseport": "rule:admin_or_network_owner",
        "get_baseport": "rule:admin_or_owner",
        "update_baseport": "rule:admin_or_network_owner",
        "delete_baseport": "rule:admin_or_network_owner",

        "create_service": "rule:admin_or_network_owner",
        "get_service": "rule:admin_or_owner",
        "update_service": "rule:admin_or_network_owner",
        "delete_service": "rule:admin_or_network_owner",

        "create_function": "rule:admin_or_network_owner",
        "get_function": "rule:admin_or_owner",
        "update_function": "rule:admin_or_network_owner",
        "delete_function": "rule:admin_or_network_owner",

        "create_service_binding": "rule:admin_or_network_owner",
        "delete_service_binding": "rule:admin_or_network_owner",

        "create_function_binding": "rule:admin_or_network_owner",
        "delete_function_binding": "rule:admin_or_network_owner",
    }


Bootstrapping policy.json
~~~~~~~~~~~~~~~~~~~~~~~~~

In the devstack environment, the gluon software is installed using "python setup.py install"
command from the gluon directory. The setup script will be enhanced to support creating
/etc/gluon/policy.json.template file from the YAML model file, and a policy.json if none exists
or if there is a logical way to merge the current policy.json content with the new rules.

For a production OpenStack environment, the above steps need to be done from the package
installation scripts that are supported by tools such as rpm or dpkg.

Action to API Mapping
~~~~~~~~~~~~~~~~~~~~~

Gluon service has to map the actions to respective API calls. The OpenStack oslo.policy
(http://docs.openstack.org/developer/oslo.policy/) framework will be integrated with Gluon
to enforce RBAC policies defined in the JSON.policy file.

There are several ways to implement this code and the best approach is to be finalized
through prototyping.

Future refinements
------------------
The current Gluon model does not model APIs, but models objects that constitute APIs.
It will be more clear if we allow modeling API endpoints in the YAML file. This will
also allow a more clear more representation of ACL rule on the API endpoint. Swagger
model is a good example on how to model APIs and internal objects. Please see
http://editor.swagger.io/

Reference
---------
    1) Port and service binding model - https://review.openstack.org/#/c/392250