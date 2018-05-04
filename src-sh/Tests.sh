#!/bin/bash

source $(dirname $0)/../Generator/tools.lib.sh

if [ "$BASHSYNTAX" = "" ] ; then BASHSYNTAX=0 ; fi
if [ "$LOCAL" = "" ] ; then LOCAL=1 ; fi
if [ "$VERBOSE" = "" ] ; then VERBOSE=1 ; fi
if [ "$REMOTE" = "" ] ; then REMOTE=1 ; fi

TestCase() {
	[ "$VERBOSE" = "1" ] && echo "  EXECUTE $*"
	if $* ; then 
		echo "  SUCCESS $*" ; return 0
	else
		echo "  FAILED $*" ; return 1
	fi
}

GraphvizTestCase() {
	declare -x DOTFILE=$TEMP/test.dot
	rm $DOTFILE 2>/dev/null
	TestCase "$*" || return 1
	if [ "$NOSQL" != "1" ] ; then
		if $GRAPHVIZ_BIN_DIR/dot -Tplain $(to_cmd_path $DOTFILE) >/dev/null ; then
			echo "  GRAPHVIZ PARSE SUCCESS $*"
		else
			echo "  GRAPHVIZ PARSE FAILED $*" 
		fi
	fi
	unset DOTFILE
}

TestSuite() {
	GraphvizTestCase ./CreateIncludeHierarchy-both.sh PROCESS.H
	GraphvizTestCase ./CreateInheritanceHierarchy-both.sh CStsAnlBild
	GraphvizTestCase ./CreateCallHierarchyForFunctionOrMethod-both.sh GetOptiName
	export MAX_UP=0 ; GraphvizTestCase ./CreateCallHierarchyForFunctionOrMethod-both.sh GetOptiName ; unset MAX_UP
}

if [ "$BASHSYNTAX" = "1" ] ; then
	echo "Checking all shell scripts for syntax errors..."
	for FILE in *.sh ; do bash -n $FILE || echo $FILE has syntax errors ; done
fi

if [ "$LOCAL" = "1" ] ; then
	echo "Performing local tests..."
	declare -x NOSQL=1 NOSHOW=1 MINLOGLEVEL=4
	TestSuite
	unset NOSQL NOSHOW MINLOGLEVEL
else
	echo "Skipping local tests!"
fi

if [ "$REMOTE" = "1" ] ; then
	echo "Performing remote tests..."
	declare -x NOSQL=0 NOSHOW=1 MINLOGLEVEL=4
	TestSuite
	unset NOSQL NOSHOW MINLOGLEVEL
else
	echo "Skipping remote tests!"
fi

