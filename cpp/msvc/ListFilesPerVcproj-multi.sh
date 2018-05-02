#!/bin/bash

source $(dirname ${BASH_SOURCE[0]})/../../src-sh/configuration/config.lib.sh

if [ "$PROJECTFILEBASEDIR" = "" ] ; then
	Log ERROR "PROJECTFILEBASEDIR is not set!"
	exit 1
fi

EXTENSION_LIST="$1" 

if [ "$EXTENSION_LIST" = "" ] ; then
	Log ERROR "call with parameter extension list, e.g.: c,cpp"
	exit 1
fi

PROJECTFILEBASEDIR_DOS=$(to_cmd_path $PROJECTFILEBASEDIR)

cd $PROJECTFILEBASEDIR
  XSLTransform $(to_cmd_path $REVENGTOOLS_DIST/cpp/msvc/call.xml) $(to_cmd_path $REVENGTOOLS_DIST/cpp/msvc/files-multi.xsl) \
	absolute_source_base_path="$(to_cmd_path $LOCAL_SOURCE_BASE_DIR)" \
	extension_list="$EXTENSION_LIST" \
	file_list="$(while read file ; do echo -n "$file," ; done <$RESULTS_DIR/vcprojs-from-sln)" \
	projectfile_base_path=$PROJECTFILEBASEDIR_DOS
#	relative_vcproj_base_path="$(dirname $VCPROJ)" \
	