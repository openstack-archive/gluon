import click
import types
from gluon.common.particleGenerator.cli import proc_model
import sys

sys.tracebacklimit=0

def dummy():
    pass

def main():
    cli = types.FunctionType(dummy.func_code, {})
    cli = click.group()(cli)
    proc_model(cli,
              package_name = "gluon",
              model_dir = "models/proton/net-l3vpn",
              hostenv = "OS_PROTON_HOST",
              portenv = "OS_PROTON_PORT",
              hostdefault = "127.0.0.1",
              portdefault = 2705)
    cli()
