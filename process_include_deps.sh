#!/bin/bash

#if [ "$CONFIG" = "" ] ; then
#  echo "WARNING: CONFIG variable must be set"
#  exit
#fi


if [ "$IMGTYPE" = "" ] ; then IMGTYPE="pdf" ; fi

source $(dirname ${BASH_SOURCE[0]})/src-sh/configuration/config.lib.sh

SERVER_SOURCE_BASE_DIR_DOS=$(to_cmd_path $SERVER_SOURCE_BASE_DIR)
install -d $RESULTS_DIR/IncludeDeps
cd $RESULTS_DIR/IncludeDeps

Map() {
  local IN=$1
  while read FILE  ; do grep "$FILE" module_to_headerfiles_raw ; done >$IN.map <$IN
}

if [ "$1" != "quick" ] ; then 
  RemoveFilelists
  rm $RESULTS_DIR/module_to_implementationfiles 2>/dev/null
  rm $RESULTS_DIR/module_to_headerfiles_raw 2>/dev/null
  rm $RESULTS_DIR/module_to_vcprojfiles 2>/dev/null
  rm $RESULTS_DIR/module_to_txtfiles 2>/dev/null
  rm include_statements 2>/dev/null
  rm $RESULTS_DIR/module_to_headerfiles_linked 2>/dev/null
  rm $RESULTS_DIR/module_link_deps.csv 2>/dev/null
  rm $RESULTS_DIR/module_rootdirs 2>/dev/null
fi
Python generate_vcproj_list_run >$RESULTS_DIR/vcprojs-from-sln
  CreateFilelists
  if [ ! -f $RESULTS_DIR/module_to_implementationfiles \
       -o ! -f $RESULTS_DIR/module_to_headerfiles_raw \
       -o ! -f $RESULTS_DIR/module_to_vcprojfiles \
       -o ! -f $RESULTS_DIR/module_to_txtfiles ] ; then
    # TODO rename files vcproj->module 
  	echo Generating files module_to_implementationfiles, module_to_headerfiles_raw, module_to_vcprojfiles   
  	IMPL_EXT="c,cpp,cc"
  	HEADER_EXT="h,df,dh,dc,co"
  	$REVENGTOOLS_DIST/cpp/msvc/ListFilesPerVcproj-multi.sh "$IMPL_EXT,$HEADER_EXT,txt" >$RESULTS_DIR/module_to_allfiles
  	egrep "\.(h|dh|df|dc|co)$"  $RESULTS_DIR/module_to_allfiles > $RESULTS_DIR/module_to_headerfiles_raw 
	egrep "\.(cpp|c|cc)$" $RESULTS_DIR/module_to_allfiles > $RESULTS_DIR/module_to_implementationfiles 
	egrep "\.(vcproj|vcxproj)$" $RESULTS_DIR/module_to_allfiles > $RESULTS_DIR/module_to_vcprojfiles
	egrep "\.(txt)$" $RESULTS_DIR/module_to_allfiles > $RESULTS_DIR/module_to_txtfiles
	
	rm $RESULTS_DIR/module_to_allfiles
	rm duplicate_headers
  else
  	echo Using existing file $(stat -c "%n (%y)" $RESULTS_DIR/module_to_implementationfiles)
  	echo Using existing file $(stat -c "%n (%y)" $RESULTS_DIR/module_to_headerfiles_raw)
  	echo Using existing file $(stat -c "%n (%y)" $RESULTS_DIR/module_to_vcprojfiles)
  	echo Using existing file $(stat -c "%n (%y)" $RESULTS_DIR/module_to_txtfiles)
  fi
  if [ ! -f $RESULTS_DIR/module_rootdirs ] ; then
	echo Creating map of root directories to default modules
	# TODO rename file
	Python cpp.msvc.create_rootdir_to_vcproj_map_run >$RESULTS_DIR/module_rootdirs || exit 1
  else
  	echo Using existing file $(stat -c "%n (%y)" $RESULTS_DIR/module_rootdirs)
  fi
  
  if [ ! -f include_statements ] ; then
  	echo Generating file include_statements
    time Python determine_include_deps_run >include_statements || exit 1
  else
    echo Using existing file $(stat -c "%n (%y)" include_statements)
  fi
  
  if [ ! -f $RESULTS_DIR/module_to_headerfiles_linked ] ; then
    echo "Linking header files to modules"
    time Python cpp.link_headers_to_modules_run >$RESULTS_DIR/module_to_headerfiles_linked || exit 1
  else
    echo Using existing file $(stat -c "%n (%y)" $RESULTS_DIR/module_to_headerfiles_linked)
  fi

  if [ ! -f $RESULTS_DIR/module_link_deps.csv ] ; then
  	echo Generating file module_link_deps.csv
  	echo "Additional information for process_include_deps.sh:"
  	echo $1
  	$REVENGTOOLS_DIST/process_link_deps.sh --focus_on_each_group $1|| exit 1
  else
  	echo Using existing file $(stat -c "%n (%y)" $RESULTS_DIR/module_link_deps.csv)
  fi
  if [ ! -f duplicate_headers ] ; then
	echo "Creating list of duplicate headers (in more than one vcproj)"
	Python determine_duplicate_headers_run >duplicate_headers || exit 1
  else
  	echo Using existing file $(stat -c "%n (%y)" duplicate_headers)
  fi

if [ "$1" != "--rulesonly" ] ; then
	echo "Lifting include dependencies to module level"
	Python cpp.incl_deps.lift_include_links_run || exit 1

	echo "Creating link/include dependency consistency report"
	export FLAVORS=toplevel
	Python check_include_link_dep_consistency_run || exit 1
	#Temporarily deactivated and activated --focus_on_each_group for link deps (see above)
	#Python check_include_link_dep_consistency_run --focus_on_each_group || exit 1
	unset FLAVORS

	echo "Creating file-level include dependency check report"
	Python jenkins_check_include_rules_run || exit 1

	echo -n "Generating graphs"
	#dot -T$IMGTYPE -O module_include_deps.dot && echo -n "."
	$GRAPHVIZ_BIN_DIR/tred module_include_deps.dot > module_include_deps.tr.dot && echo -n "."
	echo ",tr,module-level include dependencies,,IncludeDeps/module_include_deps.tr.dot.svg" >>$RESULTS_DIR/generated_graphs.csv
	$GRAPHVIZ_BIN_DIR/dot -T$IMGTYPE -O module_include_deps.tr.dot && echo -n "."

	#dot -T$IMGTYPE -O module_include_deps-consistency.dot && echo -n "."
	#dot -T$IMGTYPE -O module_include_deps-impl-except.dot && echo -n "."
	#dot -T$IMGTYPE -O module_include_deps-impl-except-overview.dot && echo -n "."

	echo
else
	echo "Not Lifting include dependencies to module level and further processing"
fi
echo "Done. Output written to $RESULTS_DIR"

exit

# TODO Folgendes ist nur sinnvoll, ohne nicht existierende Module in *_mapping_exceptions zu verarbeiten
#Python cast.generator.generate_stylesheet >$PROJECTFILEBASEDIR/add_missing_deps.xsl
