#!/bin/bash

export PYTHONPATH=`pwd`:$PYTHONPATH
export LD_LIBRARY_PATH=`pwd`/cpp/potentials:$LD_LIBRARY_PATH
python statistics/runner.py $*
