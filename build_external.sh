#!/bin/bash
set -x -e

cd external/idep/src
sh configure
make
mkdir ../bin
cp adep cdep ldep ../bin

