#!/bin/bash

LAST_RUN=`ls -t runs/ | grep -e "$1" | head -1`
echo "Running AVIZ for run: $LAST_RUN"
aviz -rm spin -vpm lqc.vpm -fl runs/$LAST_RUN/output/lqs.list
