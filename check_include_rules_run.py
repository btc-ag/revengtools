#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.basic_config_if import BasicConfig
from commons.configurator import Configurator
from cpp.incl_deps.include_deps_if import FileIncludeDepsSupply
from cpp.incl_deps.include_rule_checker_if import IncludeRulesFactory
from cpp.incl_deps.include_rule_checker_util import (IncludeRuleCheckerProcessor, 
    IncludeRuleCheckerOutputter)
import csv
import logging
import sys

config_basic = BasicConfig()
config_checker = IncludeRulesFactory()
config_file_include_deps_supply = FileIncludeDepsSupply()

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
    Configurator().default()
    
    if len(sys.argv) > 1:
        file_links = csv.reader(open(sys.argv[1]), delimiter=',')
    else:        
        file_links = config_file_include_deps_supply.get_file_include_deps()
    
    illegal_links, total_count, rule_violations = IncludeRuleCheckerProcessor().check_links(file_links, config_checker.get_include_rules())
    IncludeRuleCheckerOutputter().output(sys.stdout, illegal_links, total_count, rule_violations)

if __name__ == "__main__":
    main()
