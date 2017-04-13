Gluon and Proton version
========================

Both Gluon and Proton support multiple versions. This document describes how
to access different Gluon and Proton versions using their RESTful API.

Gluon Version
-------------

Gluon's root URI will return a list of version info. To access the default
version, use http://host_name:2705/proton/. To access v1 if there is one and is
still supported, use http://host_name:2075/v1/.

.. code-block:: bash

    $ curl http://127.0.0.1:2705/
    {
    "default_version":
                {"id": "v1",
                 "status": "CURRENT",
                "links": [{"href": "http://192.168.59.103:2705/proton/",
                           "rel": "self"
                         }]
                },
    "versions":
                [{"id": "v1",
                  "status": "CURRENT",
                  "links": [{"href": "http://192.168.59.103:2705/proton/",
                             "rel": "self"}]
                }],
    "name": "Gluon API",
    "description": "OpenStack Gluon is a port arbiter that maintains a list of
                    ports and bindings of different network backends. A Proton
                    Server is the API server that hosts multiple Protons,
                    i.e. multiple sets of APIs."
    }

Proton Version
--------------

Proton currently does not support versioning yet, this is a proposal to be
implemented in future release.

A Proton's root URI will return a list of version info. To access v1 of Proton
XYZ use http://host_name:2705/proton/XYZ/v1/. For example, to access v1 of
net-l3vpn use http://host_name:2705/proton/net-l3vpn/v1.

Proton providers can specify version info in the proton model's yaml file.

.. code-block:: bash

    $ curl http://127.0.0.1:2705/proton/net-l3vpn/
    {
    "default_version":
                {"id": "v1",
                 "status": "CURRENT",
                "links":
                    [{"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/",
                      "rel": "self"
                    }]
                },
    "versions":
                [{"id": "v1",
                  "status": "CURRENT",
                  "links":
                    [{"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/",
                      "rel": "self"}]
                }],
    "name": "net-l3vpn",
    "description": "net-l3vpn description..."
    }

**Example**

::

  file_version: 1.0
  imports: base/base.yaml
  info:
    name: net-l3vpn
    version: 1.0
    description "L3VPN API Specification"
    ...
