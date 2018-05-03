#!/bin/bash

source $(dirname ${BASH_SOURCE[0]})/../../src-sh/configuration/config.lib.sh

cd $PROJECTFILEBASEDIR

# TODO this is very slow

CreateFilelists

while read VCPROJ ; do
  echo "$(dirname $VCPROJ)"
done <$RESULTS_DIR/vcprojs-from-sln | sort -u | while read VCPROJDIR ; do 
  TOPVCPROJ=$(du -b $VCPROJDIR/*.vcproj | sort -nr | head -1 | cut -f 2 -d "	")
  echo "$VCPROJDIR:$(basename $TOPVCPROJ .vcproj)"
done

