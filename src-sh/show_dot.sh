#!/bin/bash
source $(dirname ${BASH_SOURCE[0]})/configuration/config.lib.sh
source $REVENGTOOLS_DIST/commons/graph/graphviz/graphviz.lib.sh
ShowDOTFile $1
