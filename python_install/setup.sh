#!/bin/bash

PREFIX=`pwd`/install
SOURCE_DIR=$PREFIX/usr/src/redhat/SOURCES
INSTALL_DIR=$PREFIX/usr/local

# Cleanup old installations.
rm -rf $PREFIX

# Extract the sources.
mkdir -p $SOURCE_DIR
rpm --root $PREFIX -i python2.4-2.4-1pydotorg.src.rpm

# Unpack the sources.
(cd $SOURCE_DIR &&
 tar -xjvf Python-2.4.tar.bz2)

# Configure and compile Python 2.4.
(cd $SOURCE_DIR/Python-2.4 &&
 ./configure --enable-shared --prefix=$INSTALL_DIR &&
 make &&
 make install)

# Create a soft link for the correct lib.
(cd $INSTALL_DIR/lib &&
 ln -s libpython2.4.so libpython.so)
