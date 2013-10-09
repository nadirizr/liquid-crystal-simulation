#!/bin/bash

(rm -rf output &&
 PYTHONPATH=`pwd`:$PYTHONPATH &&
 LD_LIBRARY_PATH=`pwd`/cpp/potentials:$LD_LIBRARY_PATH
 python main.py $* &&
 (cd output ; ls -1 *.xyz | sort > lqs.list))
