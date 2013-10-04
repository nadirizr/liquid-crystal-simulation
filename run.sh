#!/bin/bash

(rm -rf output &&
 PYTHONPATH=`pwd`:$PYTHONPATH &&
 python main.py $* &&
 (cd output ; ls -1 *.xyz | sort > lqs.list))
