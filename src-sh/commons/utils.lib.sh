# detect OS
UNAME=$(uname)
IS_CYGWIN=$(expr "$UNAME" : 'CYGWIN')
if [ $IS_CYGWIN -eq 0 ] ; then 
  CMD_PATH_SEP=":"
else
  CMD_PATH_SEP=";"
fi 

function to_jobgen_path () {
  echo $1 | sed s/[/]cygdrive[/]\\\(.\\\)/\\\1:/ | sed s/[/]/\\\\\\\\/g
}
function to_cmd_path () {
  # converts a path to a OS-specific path
  # needed to convert cygwin-paths to windows-paths, does nothing on unix
  if [ $IS_CYGWIN -eq 0 ] ; then
    echo $1
  else 
    echo $1 | sed s/[/]cygdrive[/]\\\(.\\\)/\\\1:/ | sed s/[/]/\\\\/g
  fi 
}
function to_unix_path () {
  # converts a OS-specific path to a unix path
  if [ $IS_CYGWIN -eq 0 ] ; then
    echo $1
  else 
    echo $1 | sed -e "s#^\(.\)\:#/cygdrive/\1#"  -e "s#\\\\#/#g"
  fi
}
function today() {
  date +%Y%m%d
}
function CreateFilelists() {
	pushd $LOCAL_SOURCE_BASE_DIR >/dev/null
	if [ ! -f filelist ] ; then find . >filelist ; rm headerlist impllist ; fi
	if [ ! -f headerlist ] ; then egrep "\.(h|dh|df|dc|co)$" filelist > headerlist ; fi
	if [ ! -f impllist ] ; then egrep "\.(cpp|c)$" filelist > impllist ; fi
	popd >/dev/null
	#Python parse_link_dependencies_generic_run $SOLUTIONFILE
#	pushd $PROJECTFILEBASEDIR >/dev/null
#	# TODO Die Ausnahme bzgl. build ist PRINS-spezifisch
#	if [ ! -f vcprojs.list ] ; then find . -name "*.vcproj" -and -not -path './build/*' > vcprojs.list ; fi
#	popd >/dev/null
}
function RemoveFilelists() {
	pushd $LOCAL_SOURCE_BASE_DIR >/dev/null
	rm filelist headerlist impllist 2>/dev/null
	popd >/dev/null
}

FirstExistingFile() {
  for FILE in $* ; do
    if [ -f $FILE ] ; then echo $FILE ; return 0 ; fi
  done
  return 1
}
Log() {
	local LOGLEVEL="$1" # DEBUG/INFO/WARNING/ERROR/FATAL
	local LOGTEXT="$2"
	declare +i LOGLEVEL_NUM
	
	case $LOGLEVEL in
	DEBUG) LOGLEVEL_NUM=1 ;;
	INFO) LOGLEVEL_NUM=2 ;;
	WARNING) LOGLEVEL_NUM=3 ;;
	ERROR) LOGLEVEL_NUM=4 ;;
	FATAL) LOGLEVEL_NUM=5 ;;	
	*) Log FATAL "Internal error: "; exit 1 ;;
	esac
	
	if [ $LOGLEVEL_NUM -ge $MINLOGLEVEL ] ; then
	  echo "$LOGLEVEL" "$(caller)" "$LOGTEXT" >&2
	  if [ $LOGLEVEL_NUM -ge 4 -a $MINLOGLEVEL -eq 1 ] ; then
		  for VAR in $ALL_PARAMETERS ; do declare -p $VAR >&2 ; done
		  #declare -p >&2
	  fi
	fi
}
Python() {
	PYMOD=$1
	shift
	( cd $REVENGTOOLS_DIST ; "$PYTHON_BINARY" -m $PYMOD $* )
}

