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
  - doc/samples             # Sample policy.json.sample and proton.conf.sample files
  - doc/source              # All documentation
  - doc/source/devref       # Developer Guides
  - doc/source/installation # Installation Guides
  - doc/source/testcase     # Test Case proposals

- **etc**           # Config options for model handlers and backends
  - etc/proton      # Config options for Protons
  - etc/shim        # Config options for Shims

- **gluon**                 # Gluon code base
  - gluon/api               # Proton API model and control
  - gluon/api/hooks         # Policy enforcement is included here
  - gluon/backends          # Proton backend handlers, including ``net_l3vpn`` model handler
  - gluon/cmd               # CLI API generator and other tools
  - gluon/conf              # Handling configuration options in /etc/proton/proton.conf
  - gluon/common            # Common libraries
  - gluon/db                # Database handler, e.g. managing database /opt/proton/gluon.sqlite
  - gluon/managers          # API and model manager, including ``net_l3vpn`` API manager
  - gluon/models            # Proton data model, including base model ``net_l3vpn`` model, and ``ietf-sfc`` model
  - gluon/particleGenerator # Particle Generator to generate APIs from YAML
  - gluon/plugin            # Extended ML2 Plugin for Gluon, a.k.a. Gluon Wrapper Plugin
  - gluon/policies          # Default rules definition at system level
  - gluon/shim              # Shim Layer, including ``net-l3vpn`` model, sample backend and ODL backend
  - gluon/sync_etcd         # Make hosts of ``etcd`` configurable
  - gluon/tests             # Unit tests

- **releasenotes** # Enable release notes translation. Initiated by cookiecutter when repo was created

- **scripts**   # Proton Server script and configuration

Notes
-----

- A script should be created to help with the creation of new API endpoints.
  The script should create the directory tree, default files and skeleton code
  needed to support the API.

