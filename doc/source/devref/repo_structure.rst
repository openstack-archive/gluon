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

This document describes the repository structure that is currently used in the
development of Gluon.

Current Repository Structure
----------------------------

- **doc**
  - samples     # Sample policy.json and proton.conf files
  - source      # All documentation
    - devref    # Developer Guides
    - testcase  # Test Case proposals

- **etc**       # Config options for model handlers and backends
  - proton      # Config options for Protons
  - shim        # Config options for Shims

- **gluon**     # Gluon code base
  - api         # Proton API model and control
  - backends    # Proton backend handlers, including ``net_l3vpn`` model handler
  - cmd         # CLI API generator and other tools
  - common      # Common libraries
  - db          # Database handler
  - managers    # API manager, including ``net_l3vpn`` API manager
  - models      # Proton data model, including base model and ``net_l3vpn`` model
  - particleGenerator # Particle Generator to generate APIs from YAML
  - plugin      # Extended ML2 Plugin for Gluon, a.k.a. Gluon Wrapper Plugin
  - shim        # Shim Layer, including ``net-l3vpn`` model, sample backend and ODL backend
  - sync_etcd   # Make hosts of ``etcd`` configurable
  - tests       # Unit tests

- **releasenotes** # Enable release notes translation. Initiated by cookiecutter when repo was created

- **scripts**   # Proton Server script and configuration

Notes
-----

- A script should be created to help with the creation of new API endpoints.
  The script should create the directory tree, default files and skeleton code
  needed to support the API.

