#!/bin/bash

source $(dirname $0)/tools.lib.sh

# Mergen
for FILE in *sm.dot ; do
  $REVENGTOOLS_DIST/FindEdgeEquivalentPSMs.sh $FILE
done
# TR + Generieren
$REVENGTOOLS_DIST/processGraphviz.sh

# Mergen
SOURCEBASE="module_deps.OR"
SOURCEEXTS=".rwsm.tr.dot .execsm.tr.dot"

for EXT in $SOURCEEXTS ; do
	UNMERGEDNAME=${SOURCEBASE}${EXT}
	MERGEDNAME=$(basename $UNMERGEDNAME .dot).merged.dot
	
	$REVENGTOOLS_DIST/FindEdgeEquivalentPSMs.sh $UNMERGEDNAME

	# Generieren
	$REVENGTOOLS_DIST/processGraphviz.sh $MERGEDNAME
done
