#!/bin/sh

. $(dirname $0)/tools.lib.sh

MODULE=$1

$(dirname $0)/ClusterFilesByAccessingFiles-Postprocess.py $RESULTS_DIR/files_internal.$MODULE >$RESULTS_DIR/files_internal.$MODULE.dot
dot -Temf $RESULTS_DIR/files_internal.$MODULE.dot >$RESULTS_DIR/files_internal.$MODULE.dot.emf
circo -Temf $RESULTS_DIR/files_internal.$MODULE.dot >$RESULTS_DIR/files_internal.$MODULE.circo.emf
