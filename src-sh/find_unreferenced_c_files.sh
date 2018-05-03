#!/bin/sh
# 2009-12-11 SGi Nur vollständige Dateinamen matchen!
# 2009-12-07 SGi Erstellung

SOURCEDIR=D:/SOURCE/C++/FOO
VCPROJDIR=$SOURCEDIR
FILTER='grep -o "FOO/.*"'


SOURCENAMES=`find $SOURCEDIR -iname '*.c' -o -iname '*.cpp' | tr "[a-z]" "[A-Z]" | eval $FILTER`
VCPROJS=`find $VCPROJDIR -name '*.vcproj'`

for SOURCEPATH in $SOURCENAMES ; do 
  SOURCEFILE=`basename $SOURCEPATH`
  grep -iq "[\\\"]$SOURCEFILE\"" $VCPROJS || echo $SOURCEPATH 
done
