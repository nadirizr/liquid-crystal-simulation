#!/bin/bash

LAST_RUN=`ls -t runs/ | grep -e "$1" | head -1`
echo "Running AVIZ for run: $LAST_RUN"
aviz -vpm 3d.vpm -fl runs/$LAST_RUN/output/lqs.list
