#!/bin/bash

(cd cpp/potentials &&
 swig -classic -c++ -python gb_potential_impl.swig &&
 g++ -shared gb_potential_impl.cc gb_potential_impl_wrap.cxx \
     -I/usr/include/python2.4 -I/usr/include/python2.7 \
     -I/usr/local/include/python2.4 -I/usr/local/include/python2.7 \
     -I. -fPIC -o _gb_potential_impl.so -lpython)
