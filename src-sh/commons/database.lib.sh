# TODO this is specific to MS SQL Server!

SQLCMD='sqlcmd -S '${DBHOST}' -U '${DBUSER}' -P '${DBPWD}' -d '${KBNAME}' -b -r 1 -h -1 -W  '
SQLCMD_CENTRAL='sqlcmd -S '${DBHOST}' -U '${DBUSER}' -P '${DBPWD}' -d '${CENTRALNAME}' -b -r 1 -h -1 -W  '

SQLQuery() {
	Log INFO "$1"
	set -o pipefail
	if [ "$NOSQL" = "1" ] ; then 
	  echo "$1" >>sql.log
	else
	  time $SQLCMD -s "," -Q "$1" | tr "~" "\"" || {
	  Log FATAL "SQL Query failed, call stack [$(caller 0) <- $(caller 1)]"
	  exit 1 ; }
	fi
	set +o pipefail
	return 0
}

SQLQueryPara() {
	# Wie SQLQuery aber mit ? statt ~ als Ersatzzeichen f�r Anf�hrungszeichen
	Log INFO "$1"
	set -o pipefail
	[ "$NOSQL" = "1" ] || time $SQLCMD -s "," -Q "$1" | tr "?" "\"" || {
	  Log FATAL "SQL Query failed, call stack [$(caller 0) <- $(caller 1)]"
	  exit 1 ; }
	set +o pipefail
	return 0
}

