#!/bin/bash

python main.py
(cd output ; ls -1 *.xyz | sort > lqc.list)
