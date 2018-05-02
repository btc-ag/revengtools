#!/bin/bash

# call: $0 [--focus_on_each_group]

if [ "$CONFIG" = "" ] ; then
  echo "WARNING: CONFIG variable should be set"
fi
export CONFIG

if [ "$IMGTYPE" = "" ] ; then IMGTYPE="pdf" ; fi

source $(dirname ${BASH_SOURCE[0]})/src-sh/configuration/config.lib.sh

SERVER_SOURCE_BASE_DIR_DOS=$(to_cmd_path $SERVER_SOURCE_BASE_DIR)
install -d $RESULTS_DIR

if [ "$2" == "--rulesonly" ] ; then
	echo "process_links_deps with only rules"
	echo "Parsing link dependencies..."
	Python parse_link_dependencies_generic_run -l --no_graphs|| exit 1
else
	echo "process_links_deps with all graphs"
	echo "Parsing link dependencies..."
	Python parse_link_dependencies_generic_run -l $1 || exit 1
	# TODO das ist so sehr umständlich
	export SECTION_PREFIX=ifonly FLAVORS=ifonly 
	Python parse_link_dependencies_generic_run  || exit 1
	unset SECTION_PREFIX FLAVORS
	export SECTION_PREFIX=wraponly FLAVORS=wraponly 
	Python parse_link_dependencies_generic_run  || exit 1
	unset SECTION_PREFIX FLAVORS
	# TODO nur sinnvoll, wenn system=CAB
	export SECTION_PREFIX=toplevel FLAVORS=toplevel
	Python parse_link_dependencies_generic_run || exit 1
	unset SECTION_PREFIX FLAVORS
	echo "Checking EPM rules..."
	Python epm_checker_run

	echo -n "Generating graphs"
	pushd $RESULTS_DIR >/dev/null
	#dot -T$IMGTYPE -O module_link_deps.dot && echo -n "."
	$GRAPHVIZ_BIN_DIR/tred module_link_deps.dot > module_link_deps.tr.dot
	$GRAPHVIZ_BIN_DIR/dot -T$IMGTYPE -O module_link_deps.tr.dot && echo -n "."
	echo ",tr,module-level link dependencies,,module_link_deps.tr.dot.svg" >>$RESULTS_DIR/generated_graphs.csv
	#dot -T$IMGTYPE -O module_link_deps-overview.dot && echo -n "."
	#dot -T$IMGTYPE -O module_link_deps-epm-rules.dot && echo -n "."
	#dot -T$IMGTYPE -O module_link_deps-epm-rules-overview.dot && echo -n "."
	echo

	popd >/dev/null
fi