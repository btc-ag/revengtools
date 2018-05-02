#!/bin/sh
source $(dirname ${BASH_SOURCE[0]})/../../configuration/config.lib.sh

echo Muss bzgl. Include-Path-Datei angepasst werden!
exit 1

CreateFilelists

cd $LOCAL_SOURCE_BASE_DIR
(cat headerlist ; cut -f 2 -d ":" $RESULTS_DIR/IncludeDeps/module_to_implementationfiles) | while read FILENAME ; do
	DIRNAME=$(dirname $FILENAME)
	$REVENGTOOLS_DIST/cpp/idep/cdep -I. -I$DIRNAME -I$DIRNAME/../include -i$CONFIG_DIR/config.local.$SYSTEM.includepaths $FILENAME -x
done
 
