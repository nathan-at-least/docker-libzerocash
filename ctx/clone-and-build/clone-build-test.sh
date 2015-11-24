#!/bin/bash

set -eux

ls -l /usr/local/include

git clone 'https://github.com/Electric-Coin-Company/libzerocash'
cd ./libzerocash

CXXFLAGS='-I. -I/usr/local/include/libsnark -DCURVE_ALT_BN128 -DBOOST_SPIRIT_THREADSAFE -DHAVE_BUILD_INFO -D__STDC_FORMAT_MACROS -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=2 -std=c++11 -pipe -O2 -O0 -g -Wstack-protector -fstack-protector-all -fPIE -fvisibility=hidden -fPIC'

make all \
     DEPINST='/usr/local/' \
     CXXFLAGS="$CXXFLAGS" \
     STATIC=1 \
     MINDEPS=1 \
     USE_MT=1 \
     LINK_RT=1

./tests/full-test-suite.sh

