#!/bin/bash

rm -rf output
python main.py
(cd output ; ls -1 *.xyz | sort > lqc.list)
