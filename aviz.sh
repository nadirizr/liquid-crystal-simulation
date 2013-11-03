#!/bin/bash

LAST_RUN=`ls -t runs/ | head -1`
aviz -rm spin -vpm lqc.vpm -fl runs/$LAST_RUN/output/lqs.list
