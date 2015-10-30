#!/bin/bash

set -eux

git clone 'https://github.com/Electric-Coin-Company/libzerocash'
cd ./libzerocash
./get-libsnark
make
./tests/merkleTest
./tests/zerocashTest
