#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 23.09.2010

@author: SIGIESEC
'''

from base.basic_config_if import BasicConfig
from base.dependency.dependency_util import GraphDescriptionImpl
from base.dependency.generation_log_if import GenerationLogGenerator
from commons.configurator import Configurator
from cpp.incl_deps.include_deps_if import FileIncludeDepsSupply
from cpp.incl_deps.include_rule_checker_if import IncludeRulesFactory
from cpp.incl_deps.include_rule_checker_util import (IncludeRuleCheckerProcessor, 
    IncludeRuleCheckerOutputter)
import logging
import os.path
import sys

config_basic = BasicConfig()
config_checker = IncludeRulesFactory()
config_file_include_deps_supply = FileIncludeDepsSupply()
config_generation_log = GenerationLogGenerator()

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
    Configurator().default()
    
    file_links = config_file_include_deps_supply.get_file_include_deps()
    
    report_filename = os.path.join(config_basic.get_results_directory(),
                                   "IncludeDeps",
                                   "include_rule_report.txt")
    
    illegal_links, total_count, rule_violations = IncludeRuleCheckerProcessor().check_links(file_links, config_checker.get_include_rules())
    IncludeRuleCheckerOutputter().output(open(report_filename, "w"), illegal_links, total_count, rule_violations)

    description = GraphDescriptionImpl(description="file-level include deps",
                                       category="report")
    config_generation_log.add_generated_file(description=description,
                                             filename=report_filename)


if __name__ == '__main__':
    main()
