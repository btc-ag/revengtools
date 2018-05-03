#!/bin/bash
#echo "Deprecated, use ListFilesPerVcproj-multi instead (it is much faster)"
#exit 1 


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

for VCPROJ in $(cat $RESULTS_DIR/vcprojs-from-sln) ; do
  BASENAME="$(basename $VCPROJ .vcxproj)"
  XSLTransform $PROJECTFILEBASEDIR/$VCPROJ $(to_cmd_path $REVENGTOOLS_DIST/cpp/msvc/files.xsl) \
	relative_vcproj_base_path="$(dirname $VCPROJ)" \
	absolute_source_base_path="$(to_cmd_path $LOCAL_SOURCE_BASE_DIR)" extension_list="$EXTENSION_LIST" base_name="$BASENAME"
done 
