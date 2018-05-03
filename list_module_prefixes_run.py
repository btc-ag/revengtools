#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.dependency.dependency_if import ModuleGrouper
from base.modules_if import ModuleListSupply
from commons.configurator import Configurator
from commons.config_util import ClassLoader
import logging
import sys

config_module_list_supply = ModuleListSupply()
config_module_grouper = ModuleGrouper

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
    Configurator().default()
    
    if len(sys.argv) > 1:
        module_grouper_class = ClassLoader.get_class(qualified_class_name = sys.argv[1])
    else:
        module_grouper_class = config_module_grouper
    module_grouper = module_grouper_class(config_module_list_supply.get_module_list())
    for prefix in sorted(module_grouper.node_group_prefixes()):
        print "%s (%s)" % (prefix, list(module for module in config_module_list_supply.get_module_list() if prefix==module_grouper.get_node_group_prefix(module)))


if __name__ == "__main__":
    main()
