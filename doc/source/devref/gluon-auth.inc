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

      Convention for heading levels in Gluon devref:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

======================================
Gluon Authentication and Authorization
======================================

Summary
-------

This document explains the integration of Gluon with OpenStack Identity service
or Keystone. When Keystone is enabled, users that submit requests to Gluon NFV
networking service will have to  provide an authentication token in X-Auth-Token
request header. The token is obtained via making a call to the Keystone authentication
service by passing in username and password.

Assumptions
-----------

This document conforms to Identity concepts, and the mechanism of managing services,
projects, users, and roles described in "OpenStack Keystone Administrator Guide" [2]_.

The document uses the proposed "Port and Service Binding Model" [3]_ to determine the
policy actions (see section on Authorization).

Authentication
--------------

Authentication is the process of determining that users are who they say they are.
Keystone acts as an authentication proxy which intercepts HTTP calls from clients,
validates the tokens and forwards requests to the OpenStack service.

If the token is valid, Keystone will retrieve additional information from token
such as user name, user id, project name, project id etc and send this information
to the OpenStack service. Otherwise, the request will be rejected.

Setting Up
~~~~~~~~~~

Once Keystone is installed and running, services have to be configured to work with it.
This involves setting up services, projects, and users, and assigning roles to
{ project, user } pair. After OpenStack is installed, when Identity (Keystone) is bootstrapped,
several services, projects, roles and users will be created by default.

Following is the normal process to add a service, and assign roles to
{ project, user } pairs in Keystone.

  - Create a **service**
  - Create **endpoint** of that **service**
  - Create a **project**
  - Create a **user** that is expected to use the **service** under the **project**
  - Assign an ``admin`` **role** to the { **project**, **user** } pair

For bootstrapping Gluon with Identity service, we will follow the procedure of:

* Step 1: Create a new "NFV Networking" **service** named ``gluon`` (or any name) with service type ``nfvnet``

.. code-block:: bash 

    $ openstack service create --name gluon --description "NFV Network Service" nfvnet

* Step 2: Create a new **endpoint** under the **service** ``gluon``

.. code-block:: bash 

    # Note: you need to change the IP address 10.0.2.7 to match your environment

    $ openstack endpoint create --region RegionOne gluon public http://10.0.2.7:2705/proton/
    $ openstack endpoint create --region RegionOne gluon admin http://10.0.2.7:2705/proton/
    $ openstack endpoint create --region RegionOne gluon internal http://10.0.2.7:2705/proton/

* Step 3: Either reuse an existing **project** (e.g. a default project named ``service``) or create a new **project**

.. code-block:: bash 

    #
    # We reuse "service" project here.
    # If you want to create a new project:
    #     $ openstack project create --description <description of your new project> <new-project-name> --domain default
    #

* Step 4: Create a new **user** named ``gluon`` (or any name)

.. code-block:: bash 

    $ openstack user create --password <password> gluon

* Step 5: Assign ``admin`` **role** to { ``service``, ``gluon`` } pair

.. code-block:: bash 

    $ openstack role add --project service --user gluon admin

Authorization
-------------

Each OpenSack service has its own role-based access policies to allow/disallow access to
specific actions. The access control policy is defined in the format of ``<action> : <rule>``.

The <action> represents an API call like "create a user" whereas <rule> determines
under which circumstances this API call is permitted. For example, consider following policy:

.. code-block:: bash

    "identity:create_user" : "role:admin"

This policy allows ``admin`` **role** to create a new user in the Identity service.

Authorization Scope
~~~~~~~~~~~~~~~~~~~

Currently, Gluon supports the policy-based authorization at object level. In the future,
we may consider to support this role-based access control (RBAC) at the attribute level.

Defining Authorization Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In OpenStack, typically a ``policy.json`` file is used to store those RBAC policies,
for example, in ``/etc/nova/policy.json``. Because the APIs of those services (e.g.
``nova`` / ``compute``) are fixed, this policy.json mechanism provides flexibility
for defining policies for those services.

On the other hand, Gluon provides a model-driven approach to generate
NFV Networking Service APIs (including objects, database schema, and
RESTful API endpoints) from a YAML file which models the Networking Service.
Thus it is natural to define the RBAC policies of a new service with its own YAML
model definitions in the same YAML file. Thus a new section for RBAC policies
is defined in the YAML of service model.

A set of default <rules> is defined at the system level (i.e. in ``gluon/policies/base.py``).
Model authors can then use those rules to define the actions, and thus the policies in YAML.
The default <rules> are defined in ``gluon/policies/base.py``:

.. code-block:: bash

    "context_is_admin": "role:admin",
    "owner": "tenant_id:%(tenant_id)s",
    "admin_or_owner": "rule:context_is_admin or rule:owner",
    "context_is_advsvc": "role:advsvc",
    "admin_or_network_owner": "rule:context_is_admin or tenant_id:%(network:tenant_id)s",
    "admin_owner_or_network_owner": "rule:owner or rule:admin_or_network_owner",
    "admin_only": "rule:context_is_admin",
    "regular_user": "",
    "default": "rule:admin_or_owner",

The default policies are defined at the system level too (i.e. within the ``policies`` section
in ``BaseObject`` definition and ``BaseServiceBinding`` definition in
``gluon/models/base/base.yaml`` file). Model authors can define own policies for those
service objects in its own service YAML, or reuse the default policies if there is no policy
definition in service objects. The default policies defined in ``gluon/models/base/base.yaml``
are as follows:

.. code-block:: bash

    BasePort:
        ...
        existing model definition
        ...
        policies:
            create:
                role: "rule:admin_or_owner"
            delete:
                role: "rule:admin_or_owner"
            list:
                role: "rule:admin"
            get:
                role: "rule:admin_or_owner"
            update:
                role: "rule:admin_or_owner"

This policy defines ``create``, ``delete``, ``get``, ``get_one`` and ``update`` actions on
the ``BasePort`` object. The rules section can embed any OpenStack policy directive
that is supported.

Summary of Gluon Authorization Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to ``doc/samples/policy.json`` for a summary of default <rules> and default policies
used in Gluon. Note that this policy.json is a historical record for informational purpose.
The mechanism of how to define those default <rules> and default policies is at system level
as described above.

More Details of OpenStack Policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to "OpenStack Security Guide - Policies" [4]_ for more details of
OpenStack policy directive.

Action to API Mapping
~~~~~~~~~~~~~~~~~~~~~

Gluon service has to map actions to respective API calls. The OpenStack ``keystonemiddleware``
and ``oslo.policy`` [5]_ modules is integrated with Gluon to add keystone authentication
and enforce RBAC policies defined in the YAMl files.

The pecan-wsgi service in the Neutron is used as a reference code for above implementation in Gluon.

Current implementation in Gluon is at ``gluon/api/hooks/policy_enforcement.py``.

Configuration
~~~~~~~~~~~~~

The /etc/proton/proton.conf file is used to configure the authentication details. A sample
configuration is shown below. Note that you need to change IP address ``127.0.0.1``
to your keystone endpoint.

.. code-block:: ini

    [api]
    auth_strategy = keystone

    [keystone_authtoken]
    auth_uri = http://127.0.0.1:5000
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = <password>
    username = gluon
    auth_url = http://127.0.0.1:35357
    auth_type = password

The default ``auth_strategy`` is ``noauth`` in Gluon.

Please note that:

* ``auth_uri`` is the **external** or **public** URL that ends up in the
  ``WWW-Authenticate: keystone-uri=<auth_uri>`` header. It is the unversioned public endpoint,
  which tells someone where they need to go to authenticate.
* ``auth_url`` is the **internal** URL that the **auth plugin** is using. It is
  where the process will authenticate to before it authenticates tokens. 

Set Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~

If Keystone is enabled for authentication, some environment variables will need
to be set up in order for ``protonclient`` commands to work properly.

Modify the ``openrc`` file in Gluon home directory (or in ``devstack`` home directory)
with the appropriate value for you Keystone endpoint, your project name/tenant name,
your user name and password.

A sample is shown as follows:

.. code-block:: bash

    #
    # Configure a set of credentials for $PROJECT/$USERNAME:
    #     set OS_AUTH_URL to Keystone end point
    #     set OS_PROJECT_NAME to openstack project name
    #     set OS_USERNAME to openstack user name
    #     set ADMIN_PASSWORD to openstack password
    #
    # If using devstack:
    #     set both OS_USERNAME and OS_TENANT_NAME to "admin" or "demo"
    #
    # Example config for devstack:
    #     export OS_AUTH_URL="http://192.168.56.101:5000"
    #     export OS_TENANT_NAME="admin"
    #     export OS_USERNAME="admin"
    #     export OS_PASSWORD="ubuntu"
    #

Then run the following command to set these variables.

.. code-block:: bash

    $ source openrc <project_name> <user_name> <user_password>

References

.. [2] https://docs.openstack.org/keystone/latest/admin/index.html
.. [3] ./service_binding_model
.. [4] https://docs.openstack.org/security-guide/identity/policies.html
.. [5] https://docs.openstack.org/oslo.policy/latest/
