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

=============================
Proton API Version Management
=============================

Summary
-------

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
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn",
                "rel": "self"
              }
            ]
        },
        { "status": "CURRENT",
          "proton_service": "test",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/test",
                "rel": "self"
              }
            ]
        },
        { "status": "CURRENT",
          "proton_service": "ietf-sfc",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/ietf-sfc",
                "rel": "self"
              }
            ]
        }
      ]
    }

Proton Version Management
-------------------------

Proton providers can specify version info in the proton model's YAML file.

**Example**

.. code-block:: yaml

    file_version: 1.0
    imports: base/base.yaml
    info:
      name: net-l3vpn
      version: 1.0
      description "L3VPN API Specification"
    ...

Version information is appended to the root URL of a particular Proton, e.g. L3VPN.
For example, http://192.168.59.103:2705/proton/net-l3vpn/v1.0/.

When accessing the root URL of a particular Proton without version information, all
available versions of this Proton will be returned so that users can choose to use
a particular version of this Proton.

.. code-block:: bash

    $ curl http://192.168.59.103:2705/proton/net-l3vpn/
    {
    "default_version":
      { "status": "CURRENT",
        "proton_service": "net-l3vpn",
        "links":
          [
            { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0",
              "rel": "self"
            }
          ],
        "version_id": "v1.0"
      },
    "versions":
      [
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        }
      ]
    }

When accessing the root URL of a particular Proton with version information, all
available resources in this version of Proton will be returned.

.. code-block:: bash

    $ curl http://192.168.59.103:2705/proton/net-l3vpn/v1.0/
    {
    "resources":
      [
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "resource_name": "dataplanetunnels",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0/dataplanetunnels",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        },
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "resource_name": "bgppeerings",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0/bgppeerings",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        },
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "resource_name": "vpnafconfigs",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0/vpnafconfigs",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        },
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "resource_name": "vpns",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0/vpns",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        },
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "resource_name": "interfaces",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0/interfaces",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        },
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "resource_name": "vpnbindings",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0/vpnbindings",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        },
        { "status": "CURRENT",
          "proton_service": "net-l3vpn",
          "resource_name": "ports",
          "links":
            [
              { "href": "http://192.168.59.103:2705/proton/net-l3vpn/v1.0/ports",
                "rel": "self"
              }
            ],
          "version_id": "v1.0"
        }
      ]
    }
 
