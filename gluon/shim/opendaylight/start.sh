#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
set -e
export PYTHONPATH=$PYTHONPATH:$DIR
python ./proton-shim-layer-opendaylight.py $@