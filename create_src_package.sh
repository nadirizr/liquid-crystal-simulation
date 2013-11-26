#!/bin/bash

# Prepare source directory.
rm -rf lc_simulation_src
svn export . lc_simulation_src
rm -f lc_simulation_src/web/lc_simulation_src.tar.gz

# Create the source tar file.
tar -cvzf web/lc_simulation_src.tar.gz lc_simulation_src
rm -rf lc_simulation_src

# Commit the new file.
svn commit web/lc_simulation_src.tar.gz -m "New version of LCS sources."
