#!/bin/bash
source $(dirname ${BASH_SOURCE[0]})/configuration/config.lib.sh
source $REVENGTOOLS_DIST/commons/graph/graphviz/graphviz.lib.sh

if [ $LANGUAGE != "python" ] ; then
   echo "Call with CONFIG set to a Python configuration"
   exit 1
fi

pushd $LOCAL_SOURCE_BASE_DIR >/dev/null
find . -name '*.py' -and -not -name 'Cluster*' -and -not -name 'List*' -and -not -path './configuration/*' >$RESULTS_DIR/python-modules
popd >/dev/null

DOTFILE=D:/Temp/depgraph.dot

PYTHONPATH=$(to_cmd_path $REVENGTOOLS_DIST) Python -m pydep_run $(cat $RESULTS_DIR/python-modules) >$DOTFILE
ShowDOTFile $DOTFILE

