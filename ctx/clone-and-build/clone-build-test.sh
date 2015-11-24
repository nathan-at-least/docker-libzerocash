#!/bin/bash

set -eux

ls -l /usr/local/include

git clone 'https://github.com/Electric-Coin-Company/libzerocash'
cd ./libzerocash

make CXXFLAGS='-c -MMD -g -Wall -Wextra -Werror -Wfatal-errors -Wno-unused-parameter -std=c++11 -fPIC -Wno-unused-variable -DUSE_ASM -DCURVE_ALT_BN128 -I/usr/local/include/libsnark -I.'

./tests/merkleTest
./tests/zerocashTest

