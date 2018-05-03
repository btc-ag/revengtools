#!/bin/bash

PARAMETERS="$PARAMETERS
Parameters used by tools.lib.sh:
  CONFIG=[*config.default*/...]
  NOSQL=[*0*/1]
  MINLOGLEVEL=[1/2/*3*/4/5]

"
TryConfig() {
	local LOCAL_CONFIG_FILE=$1 LOGLEVEL=$2
	if [ -f $LOCAL_CONFIG_FILE ] ; then 
	  source $LOCAL_CONFIG_FILE
	else
	  Log $2 "No config file $LOCAL_CONFIG_FILE"
	fi
}
ParseConfig() {
	local CONFIG=$1
	CONFIG_DIR=$REVENGTOOLS_DIST/configuration
	TryConfig $CONFIG_DIR/$CONFIG FATAL 
	TryConfig $CONFIG_DIR/config.local INFO
	TryConfig $CONFIG_DIR/config.local.$SYSTEM INFO
	TryConfig $CONFIG_DIR/config.local.$VERSION INFO

	local MISSINGPARAMETERS=""
	[ "$SERVER_SOURCE_BASE_DIR" = "" ] && MISSINGPARAMETERS="$MISSINGPARAMETERS SERVER_SOURCE_BASE_DIR"
	[ "$DBHOST" = "" ] && MISSINGPARAMETERS="$MISSINGPARAMETERS DBHOST"
	[ "$DBUSER" = "" ] && MISSINGPARAMETERS="$MISSINGPARAMETERS DBUSER"
	[ "$DBPWD" = "" ] && MISSINGPARAMETERS="$MISSINGPARAMETERS DBPWD"
	[ "$KBNAME" = "" ] && MISSINGPARAMETERS="$MISSINGPARAMETERS KBNAME"
	[ "$VERSION" = "" ] && MISSINGPARAMETERS="$MISSINGPARAMETERS VERSION"
	[ "$LOCAL_SOURCE_BASE_DIR" = "" ] && MISSINGPARAMETERS="$MISSINGPARAMETERS LOCAL_SOURCE_BASE_DIR"
	
	if [ "$IMGTYPE" = "" ] ; then
	  IMGTYPE=pdf
	fi
	
	if [ "$MISSINGPARAMETERS" != "" ] ; then
	  Log WARNING "Config files (base config = $CONFIG) do not contain parameters $MISSINGPARAMETERS"
	  #exit 1
	fi
	
	if [ "$LANGUAGE" = "" ] ; then  LANGUAGE="cpp" ; fi
	TryConfig $CONFIG_DIR/config.language.$LANGUAGE WARNING
	 
	if [ "$RESULTS_BASE_DIR" = "" ] ; then
		if [ "$RESULTS_DIR" = "" ] ; then
			echo "RESULTS_BASE_DIR or RESULTS_DIR must be set"
			exit 1
		fi
		# TODO das geht so nicht, muss in absoluten Pfad konvertiert werden
  		RESULTS_BASE_DIR=$REVENGTOOLS_DIST/../Results
	fi
	
	if [ ! -d "$SERVER_SOURCE_BASE_DIR" ] ; then
	  Log WARNING "Source base directory $SERVER_SOURCE_BASE_DIR does not exist"
	fi
	
	if [ "$PYTHON_BINARY" = "" ] ; then
	  PYTHON_BINARY=$(which python)
	fi
	
	if [ "$GRAPHVIZ_BIN_DIR" = "" ] ; then
	  GRAPHVIZ_BIN_DIR=${REVENGTOOLS_DIST}/external/graphviz/bin
	fi
	
}

REVENGTOOLS_DIST=$(cd $(dirname ${BASH_SOURCE[0]})/../.. ; pwd)

export REVENGTOOLS_DIST REVENGTOOLS_DIST_HOST CONFIG_DIR PYTHON_BINARY GRAPHVIZ_BIN_DIR

source $REVENGTOOLS_DIST/src-sh/commons/utils.lib.sh
REVENGTOOLS_DIST_HOST=$(to_cmd_path $REVENGTOOLS_DIST)

if [ "$CONFIG" = "" ] ; then
  CONFIG=config.default
fi
if [ "$MINLOGLEVEL" = "" ] ; then
  MINLOGLEVEL=2
fi

ParseConfig $CONFIG

Log INFO "Using PYTHON_BINARY=${PYTHON_BINARY}"
export PYTHONPATH="$(cd $REVENGTOOLS_DIST/site-packages ; for a in *.egg ; do echo -n $REVENGTOOLS_DIST_HOST/site-packages/$a${CMD_PATH_SEP} ; done)$REVENGTOOLS_DIST_HOST/site-packages"


if [ "$PROJECTFILEBASEDIR" = "" ] ; then
  Log INFO "PROJECTFILEBASEDIR is not set, using LOCAL_SOURCE_BASE_DIR=$LOCAL_SOURCE_BASE_DIR" 
  PROJECTFILEBASEDIR=$LOCAL_SOURCE_BASE_DIR
fi 
export PROJECTFILEBASEDIR

SERVER_SOURCE_BASE_DIR_DOS=$(to_cmd_path $SERVER_SOURCE_BASE_DIR)
if [ "$RESULTS_DIR" = "" ] ; then RESULTS_DIR=$RESULTS_BASE_DIR/$VERSION ; fi

if [ ! -d $RESULTS_DIR ] ; then
  install -d $RESULTS_DIR
fi

#[ -f D:/Program\ Files\ \(x86\)/saxonhe9-2-1-2n/bin/Transform.exe ] && XSLT_PROGRAM=D:/Program\ Files\ \(x86\)/saxonhe9-2-1-2n/bin/Transform.exe
#[ -f D:/Programme/saxonhe9-2-1-2n/bin/Transform.exe ] && XSLT_PROGRAM=D:/Programme/saxonhe9-2-1-2n/bin/Transform.exe
#[ -f C:/Programme/saxonhe9-2-1-2n/bin/Transform.exe ] && XSLT_PROGRAM=C:/Programme/saxonhe9-2-1-2n/bin/Transform.exe
[ -f $REVENGTOOLS_DIST/external/saxon/Transform.exe ] && XSLT_PROGRAM=$REVENGTOOLS_DIST/external/saxon/Transform.exe
export XSLT_PROGRAM

XSLTransform() {
  if [ "$XSLT_PROGRAM" = "" ] ; then
    Log FATAL "No XSLT processor found, download Saxon HE from http://sourceforge.net/projects/saxon/files/Saxon-HE/9.2/saxonhe9-2-1-2n.zip/download and unzip to [CD]:/Programme/saxonhe9-2-1-2n" ]
    exit 1
  fi
  $XSLT_PROGRAM $*
}

source $REVENGTOOLS_DIST/src-sh/commons/database.lib.sh

Log DEBUG "Environment at end of config.lib.sh: $(set)"
