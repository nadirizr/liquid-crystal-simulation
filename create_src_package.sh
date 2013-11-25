#!/bin/bash

rm -rf lc_simulation_src
svn export . lc_simulation_src
rm -f lc_simulation_src/web/lc_simulation_src.tar.gz
tar -cvzf web/lc_simulation_src.tar.gz lc_simulation_src
svn commit web/lc_simulation_src.tar.gz -m "New version of LCS sources."
