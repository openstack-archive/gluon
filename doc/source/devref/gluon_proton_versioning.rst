Proton API Version Management
=============================

Each Proton API set, e.g. L3VPN, may evolve over time. Proton API version evolves
independently of Gluon releases. Thus version management of Proton APIs plays an
important role to ensure the backward compatibility and forward compatibility of
applications and services that use particular Proton APIs.

This document describes the mechanism of version management of Proton APIs.

Proton Root URI
---------------

When the Proton root URI "/proton/" is accessed it will return a list of Proton APIs.

.. code-block:: bash

    $ curl http://192.168.59.103:2705/proton/
    {
    "protons":
            [
                {"id": "net-l3vpn",
                 "status": "CURRENT",
                 "links":
                     [
                         {"href": "http://192.168.59.103:2705/proton/net-l3vpn/",
                          "rel": "self"
                         }
                     ]
                },
                {"id": "bgp",
                 "status": "CURRENT",
                 "links":
                     [
                         {"href": "http://192.168.59.103:2705/proton/bgp/",
                          "rel": "self"
                         }
                     ]
                }
                ...
            ]
    }

Proton Version Management
-------------------------

Version information is appended to the root URL of a particular Proton, e.g. L3VPN.
For example, <some URL>/proton/net-l3vpn/v1.

When accessing the root URL of a particular Proton without version information, all
available versions of this Proton will be returned so that users can choose to use
a particular version of this Proton.

When accessing the root URL of a particular Proton with version information, all
available resources in this version of Proton will be returned.

Proton providers can specify version info in the proton model's yaml file.

.. code-block:: bash

    $ curl http://192.168.59.103:2705/proton/net-l3vpn/
    {
    "default_version":
        {"id": "v1",
         "status": "CURRENT",
         "links":
             [
                 {"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/",
                  "rel": "self"
                 }
             ]
        },
    "versions":
        [
            {"id": "v1",
             "status": "CURRENT",
             "links":
                 [
                     {"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/",
                      "rel": "self"
                     }
                 ]
            }
        ],
    "name": "net-l3vpn",
    "description": "net-l3vpn description..."
    }

    .. code-block:: bash

    $ curl http://192.168.59.103:2705/proton/net-l3vpn/v1/
    {
    "resources":
        [
            {"id": "interface",
             "status": "CURRENT",
             "links":
                 [
                     {"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/interface/",
                      "rel": "self"
                     }
                 ]
            },
            {"id": "port",
             "status": "CURRENT",
             "links":
                 [
                     {"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/port/",
                      "rel": "self"
                     }
                 ]
            },
            {"id": "vpn",
             "status": "CURRENT",
             "links":
                 [
                     {"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/vpn/",
                      "rel": "self"
                     }
                 ]
            },
            {"id": "vpnafconfig",
             "status": "CURRENT",
             "links":
                 [
                     {"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/vpnafconfig/",
                      "rel": "self"
                     }
                 ]
            },
            {"id": "vpnbinding",
             "status": "CURRENT",
             "links":
                 [
                     {"href":"http://192.168.59.103:2705/proton/net-l3vpn/v1/binding/",
                      "rel": "self"
                     }
                 ]
            }
        ]
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