# Copyright (c) 2015 Cisco Systems, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import click
import sys
import types

from gluon.common.particleGenerator.cli import proc_model

sys.tracebacklimit = 0


def dummy():
    pass


def main():
    cli = types.FunctionType(dummy.func_code, {})
    cli = click.group()(cli)
    proc_model(cli,
               package_name="gluon",
               model_dir="models/proton/net-l3vpn",
               hostenv="OS_PROTON_HOST",
               portenv="OS_PROTON_PORT",
               hostdefault="127.0.0.1",
               portdefault=2705)
    cli()
