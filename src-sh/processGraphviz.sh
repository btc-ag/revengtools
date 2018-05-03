#!/bin/sh
TYPES="emf svg"
#TYPES="emf pdf png"
#SOURCES="module_deps.DR.dot module_deps.OR.dot module_deps.CAB."
#CABSOURCEBASE=module_deps.CAB

if [ "$#" -lt 1 ] ; then
	SOURCEBASES="module_deps.DR module_deps.OR module_deps.CAB"
	SOURCEEXTS=".sm.merged.dot .execsm.merged.dot .rwsm.merged.dot .rwsm.dot .execsm.dot .exec.dot .rw.dot .all.dot"
	SOURCES=

	if [ -f module_deps.CAB.all.dot ] ; then
	  CAB=1  
	else 
	  CAB=0
	fi

	for y in $SOURCEEXTS ; do
	  for x in $SOURCEBASES ; do
		 if [ -f $x$y ] ; then
		   SOURCES="$SOURCES $x$y"
		   if [ "$CAB" -eq 1 ] ; then
			CABSOURCE=$x$y
			CABSOURCE_WO_TEST=$(basename $CABSOURCE .dot).wo_test.dot
			grep -v Test $CABSOURCE>$CABSOURCE_WO_TEST
			SOURCES="$SOURCES $CABSOURCE_WO_TEST"
		   fi
		 fi
	  done
	done
else
	SOURCES="$*"
fi

for SRCNAME in $SOURCES ; do
   DESTNAME=$(basename $SRCNAME .dot).tr.dot
   $GRAPHVIZ_BIN_DIR/tred $SRCNAME >$DESTNAME
   for F in $SRCNAME $DESTNAME ; do 
     for T in $TYPES ; do 
	   echo "$F->$F.$T: dot ..."
	   dot -O -T$T $F
	 done
   done
done

