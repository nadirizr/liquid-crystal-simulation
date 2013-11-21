#!/bin/bash

(PYTHONPATH=`pwd`:$PYTHONPATH &&
 LD_LIBRARY_PATH=`pwd`/cpp/potentials:$LD_LIBRARY_PATH &&
 (python statistics/runner.py $*))
