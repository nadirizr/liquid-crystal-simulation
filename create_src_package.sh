#!/bin/bash

# Prepare source directory.
rm -rf lc_simulation_src
svn export . lc_simulation_src
rm -rf lc_simulation_src/web
rm -rf lc_simulation_src/runs

# Create the source tar file.
tar -cvzf web/lc_simulation_src.tar.gz lc_simulation_src
rm -rf lc_simulation_src

# Prepare web directory.
rm -rf lc_simulation_src
mkdir lc_simulation_src
svn export ./web lc_simulation_src/web
svn export ./runs lc_simulation_src/runs
rm -f lc_simulation_src/web/lc_simulation_src.tar.gz lc_simulation_src/web/lc_simulation_web.tar.gz

# Create the web tar file.
tar -cvzf web/lc_simulation_web.tar.gz lc_simulation_src
rm -rf lc_simulation_src

# Commit the new file.
svn commit web/lc_simulation_src.tar.gz web/lc_simulation_web.tar.gz -m "New version of LCS sources and web."
