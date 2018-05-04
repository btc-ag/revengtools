#!/bin/bash
source $(dirname ${BASH_SOURCE[0]})/src-sh/configuration/config.lib.sh

set -e -x

# TODO integrate with the the unit tests below
{
  # TODO fix setting PYTHONPATH in config.lib.sh, or maybe remove it entirely
  unset PYTHONPATH

  coverage erase

  # TODO make these tests work again
  TEMP_IGNORE_DOCTESTS="--ignore=commons/config_util.py --ignore=systems/cab/header_linker.py --ignore=systems/cab/dependency_output_experimental.py --ignore=systems/cab/dependency_output.py --ignore=configuration/config_base.py --ignore=clustering/clustering_graphviz.py --ignore=base/basic_config_default.py --ignore=cpp/incl_deps/include_list_generator.py --ignore=python/python_util.py --ignore=clustering/clustering.py "
  TEMP_IGNORE_UNITTESTS="--ignore=test/unit_tests/base/diagnostics_util_test.py --ignore=test/unit_tests/infrastructure/ctags/ctag_class_mapper_test.py --ignore=test/unit_tests/cpp/incl_deps/include_list_generator_test.py --ignore=test/unit_tests/cpp/incl_deps/include_resolver_util_test.py"
  TEMP_IGNORE_INTEGRATIONTESTS="--ignore=test/integration_tests/os_util_long_test.py --ignore=test/integration_tests/cabCsharp_tests/cab_csharp_test.py "
  py.test --doctest-modules --cov=./ --cov-report= --ignore=site-packages --ignore=pydep_run.py --ignore=independent_part_run.py --ignore=infrastructure/graph_layout/zest --ignore=test --verbose $TEMP_IGNORE_DOCTESTS
  py.test --doctest-modules --cov=./ --cov-append test/unit_tests $TEMP_IGNORE_UNITTESTS --verbose
  if [ "$TRAVIS" == "true" ] ; then
    coverage xml -o coverage.xml
    codecov --flags unit
  fi
  coverage erase

  # TODO currently all integration tests are ignored, which causes py.test to return 5
  #py.test --doctest-modules --cov=./ --cov-append test/integration_tests $TEMP_IGNORE_INTEGRATIONTESTS --verbose
  #if [ "$TRAVIS" == "true" ] ; then
  #  coverage xml -o coverage.xml
  #  codecov --flags integration
  #fi
  #coverage erase

  # TODO currently there are no real tests in test/system_tests
  #py.test --doctest-modules --cov=./ --cov-append test/system_tests --verbose
  # TODO do this with the test framework?
  LOCAL_SOURCE_BASE_DIR=$(pwd) LANGUAGE=python coverage run -a pydep_run.py | dot
  coverage report

  if [ "$TRAVIS" == "true" ] ; then
    coverage xml -o coverage.xml
    codecov --flags system
  fi
  coverage erase

  # TODO currently there are no real tests in test/perf_tests
  #py.test --doctest-modules --cov=./ --cov-append test/perf_tests --verbose

  #if [ "$TRAVIS" == "true" ] ; then
  #  coverage xml -o coverage.xml
  #  codecov --flags perf
  #fi
  #coverage erase

  exit
}

#"${PYTHON_BINARY}" -c "__requires__ = 'unittest2' ; import pkg_resources ; pkg_resources.run_script('unittest2', 'unit2.py')" discover -v -s test -t . -p *_test.py

if [ "$1" = "--xml" ] ; then
  "${PYTHON_BINARY}" -c "from unittest2 import TestLoader ; suite = TestLoader().discover(start_dir='test', pattern='*_test.py', top_level_dir='.') ; import junitxml; import sys;  result = junitxml.JUnitXmlResult(open('$2', 'w')) ; result.startTestRun() ; suite.run(result) ; result.stopTestRun()"
else 
  "${PYTHON_BINARY}" site-packages/unittest2/scripts/unit2.py discover -v -s test -t . -p *_test.py
fi


