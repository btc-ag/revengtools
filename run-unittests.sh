#!/bin/bash
source $(dirname ${BASH_SOURCE[0]})/src-sh/configuration/config.lib.sh

# TODO integrate with the the unit tests below
{
  # TODO fix setting PYTHONPATH in config.lib.sh, or maybe remove it entirely
  unset PYTHONPATH
  py.test --doctest-modules --cov=./ --ignore=site-packages --ignore=pydep_run.py --ignore=independent_part_run.py --ignore=infrastructure/graph_layout/zest --ignore=commons/config_util.py --verbose
  exit
}

#"${PYTHON_BINARY}" -c "__requires__ = 'unittest2' ; import pkg_resources ; pkg_resources.run_script('unittest2', 'unit2.py')" discover -v -s test -t . -p *_test.py

if [ "$1" = "--xml" ] ; then
  "${PYTHON_BINARY}" -c "from unittest2 import TestLoader ; suite = TestLoader().discover(start_dir='test', pattern='*_test.py', top_level_dir='.') ; import junitxml; import sys;  result = junitxml.JUnitXmlResult(open('$2', 'w')) ; result.startTestRun() ; suite.run(result) ; result.stopTestRun()"
else 
  "${PYTHON_BINARY}" site-packages/unittest2/scripts/unit2.py discover -v -s test -t . -p *_test.py
fi


