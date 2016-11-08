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

==========================
Gluon Repository Structure
==========================
This document describes the repository structure that was used in the initial
development of Gluon and a proposed structure going forward.

Current Repository Structure
----------------------------
- **gluon-nova**

  - Networking plugin code for nova

    - Currently only supports Gluon.
    - All Neutron-releated code is stripped out.

  - Uses gluonclient module in gluonlib to communicate to the gluon-server
    via REST API

- **gluon**

  - Gluon core library

    - Particle generator, CLI generator, sync-etcd and other common code

  - gluon-server code

    - Main entry point for gluon-server process
    - Uses particle generator to generate the REST API from model files
      (like a proton)
    - Uses particle generator to generate sqlalchemy database classes fro
      model files (like a proton)
    - Has a manager class to support API request processing behavior
    - Supports multiple backends to process messages to/from individua
      protons (using stevedore plugin mechanism)

  - gluonclient code

    - Main entry point for CLI script

      - Contains custom extensions for bind/unbind operations (i.e. no
        generated)
    - Uses CLI common code from Gluon core library
    - Parses model files to generate commands and argument processing o
      the fly

- **gluonlib**

  - Contains gluonclient module that is used by gluon-nova
  - Contains old CLI code that is currently not used.

- **proton**

  - proton-server code

    - Main entry point for proton-server process
    - Uses particle generator from gluon package to generate the REST API
      from model files
    - Uses particle generator from gluon package to generate sqlalchemy database
      classes from model files
    - Has a manager class to support API request processing behavio
      (generic and could be generated )
    - Uses sync-etcd module in Gluon core to synchronize database update
      with etcd backend
    - Currently only supports one set of model files (l3vpn)
  - protonclient code

    - Main entry point for CLI script
    - Uses CLI common code from Gluon core library
    - Parses model files to generate commands and argument processing on
      the fly


Proposed Repository Structure
-----------------------------
- **gluon-lib**

  - Gluon core library

    - Particle generator, CLI generator, sync-etcd and other common code

- **gluon-nova**

  - Networking plugin code for nova

    - Needs to be updated to support Gluon and Neutron

  - Uses gluonclient module in python-gluonclient to communicate to the
    gluon-server via REST API

- **gluon**

  - gluon-server code

    - Main entry point for gluon-server process
    - Uses particle generator from gluon-core to generate the REST
      API from model files (like a proton)
    - Uses particle generator from gluon-core to generate sqlalchemy database
      classes from model files (like a proton)
    - Has a manager class to support API request processing
    - Supports multiple backends to process messages to/from individual
      protons (using stevedore plugin mechanism)

- **proton**

  - proton-server code

    - Main entry point for proton-server process
    - Uses sync-etcd module in Gluon core to synchronize database updates
      with etcd backend
    - Supports one or more API endpoints

      - Each API will have a unique namespace and subdirectory
      - The configuration file will have a field to specify the list of
        APIs the proton should serve
      - For example, suppose we have two APIs defined (l3vpn and evpn)

        - \http://<ipaddress>:2704/l3vpn/baseport
        - \http://<ipaddress>:2704/evpn/baseport
    - For each API subdirectory

      - Model files for the API
      - Uses particle generator from gluon-core to generate the REST
        API from model files
      - Uses particle generator from gluon-core to generate sqlalchemy
        database classes from model files
      - Has a manager class to support API request processing behavior
        (generic and could be generated )

- **python-gluonclient**

  - Main entry point for CLI script
  - Uses CLI common code from Gluon core library
  - Parses model files to generate commands and argument processing on the
    fly
  - Contains gluonclient module that is used by gluon-nova

- **python-protonclient**

  - Main entry point for CLI script
  - Uses CLI common code from Gluon core library
  - Supports one or more API endpoints

    - Each API will have a unique namespace
    - A command argument will identify which API (i.e. model files) to process

      - For example, suppose we have two APIs defined (l3vpn and evpn)

        - proton —api l3vpn baseport-create ….
        - proton —api evpn baseport-create  ...
  - Parses model files to generate commands and argument processing on the
    fly

Notes
-----

- Right now the gluon-server uses a model file to generate its API and database
  classes.  This may not be the best approach.  The API between Nova and Gluon
  should be fairly stable and may benefit from not being constrained to the
  limitations of the particle generator.
- The proton code was not originally designed to handle multiple API endpoints
  .  A substantial amount of rework will be needed to support this.
- A script should be created to help with the creation of new API endpoints.
  The script should create the directory tree, default files and skeleton code needed to support the API.

