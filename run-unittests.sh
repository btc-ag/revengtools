#!/bin/bash
source $(dirname ${BASH_SOURCE[0]})/src-sh/configuration/config.lib.sh

set -e

# TODO integrate with the the unit tests below
{
  # TODO fix setting PYTHONPATH in config.lib.sh, or maybe remove it entirely
  unset PYTHONPATH
  # TODO make these tests work again
  TEMP_IGNORE_TESTS="--ignore=test/unit_tests/base/diagnostics_util_test.py --ignore=test/unit_tests/infrastructure/ctags/ctag_class_mapper_test.py --ignore=commons/config_util.py --ignore=test/unit_tests/cpp/incl_deps/include_list_generator_test.py --ignore=test/integration_tests/os_util_long_test.py --ignore=systems/cab/header_linker.py --ignore=systems/cab/dependency_output_experimental.py --ignore=systems/cab/dependency_output.py --ignore=cpp/idep/threaded_cdep_include_deps.py --ignore=configuration/config_base.py --ignore=clustering/clustering_graphviz.py --ignore=base/basic_config_default.py --ignore=test/integration_tests/cabCsharp_tests/cab_csharp_test.py --ignore=cpp/incl_deps/include_list_generator.py --ignore=python/python_util.py --ignore=clustering/clustering.py --ignore=cpp/idep/dirwise_cdep_include_deps.py --ignore=test/unit_tests/cpp/incl_deps/include_resolver_util_test.py"
  py.test --doctest-modules --cov=./ --ignore=site-packages --ignore=pydep_run.py --ignore=independent_part_run.py --ignore=infrastructure/graph_layout/zest --verbose $TEMP_IGNORE_TESTS

  # TODO do this as a unit test?
  LOCAL_SOURCE_BASE_DIR=$(pwd) LANGUAGE=python coverage run -a pydep_run.py | dot
  exit
}

#"${PYTHON_BINARY}" -c "__requires__ = 'unittest2' ; import pkg_resources ; pkg_resources.run_script('unittest2', 'unit2.py')" discover -v -s test -t . -p *_test.py

if [ "$1" = "--xml" ] ; then
  "${PYTHON_BINARY}" -c "from unittest2 import TestLoader ; suite = TestLoader().discover(start_dir='test', pattern='*_test.py', top_level_dir='.') ; import junitxml; import sys;  result = junitxml.JUnitXmlResult(open('$2', 'w')) ; result.startTestRun() ; suite.run(result) ; result.stopTestRun()"
else 
  "${PYTHON_BINARY}" site-packages/unittest2/scripts/unit2.py discover -v -s test -t . -p *_test.py
fi


