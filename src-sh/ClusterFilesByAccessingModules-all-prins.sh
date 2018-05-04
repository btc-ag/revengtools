#!/bin/bash

source $(dirname $0)/tools.lib.sh
source $REVENGTOOLS_DIST/commons/graph/graphviz/graphviz.lib.sh

process() {
	[ -d $OUTPUTDIR ] || mkdir $OUTPUTDIR

	for MODULE in dyn prio4dyn prid4dyn top prid4mfc prid4dynmfclib ; do 
	  echo MODULE=$MODULE
	  OUTPUT=TEXT ./ClusterFilesByAccessingModules-Postprocess.py $RESULTS_DIR/files_modules.$MODULE \
		$POSTPROCESS >$OUTPUTDIR/files_modules.$MODULE.clustered
	  OUTPUT=DOT ./ClusterFilesByAccessingModules-Postprocess.py $RESULTS_DIR/files_modules.$MODULE \
		$POSTPROCESS >$OUTPUTDIR/files_modules.$MODULE.dot
	done
}

echo "Processing with PostprocessModuleClusters-nojoin.config"

POSTPROCESS=PostprocessModuleClusters-nojoin.config
OUTPUTDIR=$RESULTS_DIR/no_join_modules

process

echo "Processing with PostprocessModuleClusters.config"

POSTPROCESS=PostprocessModuleClusters.config
OUTPUTDIR=$RESULTS_DIR/with_join_modules

process

