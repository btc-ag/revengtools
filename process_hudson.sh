#!/bin/bash

source $(dirname ${BASH_SOURCE[0]})/src-sh/configuration/config.lib.sh

if [ "$RESULTS_DIR" = "" ] ; then
	Log ERROR "RESULTS_DIR must be set"
	exit 1
fi

rm $RESULTS_DIR/generated_graphs.csv >/dev/null

export RESULTS_DIR
if [ "$1" != "--rulesonly" ] ; then
	echo "All outputs are activated."
	if [ "$LANGUAGE" = "cpp" ] ; then
		./process_include_deps.sh
	else
		./process_link_deps.sh --focus_on_each_group
	fi
else 
    echo "Rules only activated."
	if [ "$LANGUAGE" = "cpp" ] ; then
		./process_include_deps.sh --rulesonly
	else
		./process_link_deps.sh --focus_on_each_group --rulesonly
	fi
fi

cp -r $REVENGTOOLS_DIST/configuration/hudson/* $RESULTS_DIR
Python generate_hudson_index_page_run
