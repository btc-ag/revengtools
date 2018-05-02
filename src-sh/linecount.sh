#!/bin/sh
for dir in `find . -maxdepth 1 -type d` ; do 
   echo -n "$dir:"
   cat $(echo /dev/null ; find $dir -name '*.py' -o -name '*.sh') | wc -l
done
