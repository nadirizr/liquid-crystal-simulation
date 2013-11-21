#!/bin/bash

(PYTHONPATH=`pwd`:$PYTHONPATH &&
 LD_LIBRARY_PATH=`pwd`/cpp/potentials:$LD_LIBRARY_PATH
 (python -u main.py $* 2>&1 | tee run.log) &&
 (cd runs/`ls -t runs | head -1`/output && ls -1 *.xyz | sort > lqs.list))
cp run.log runs/`ls -t runs | head -1`/run.log
echo && echo "Data saved in: runs/`ls -t runs | head -1`"
