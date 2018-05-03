#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 25.09.2010

@author: SIGIESEC
'''
from commons.configurator import Configurator
from commons.core_util import CollectionTools
from cpp.cpp_if import FileToModuleMapSupply
import logging
import sys

config_file_to_module_map_supply = FileToModuleMapSupply

def determine_duplicates():
    header_to_module_map = config_file_to_module_map_supply().get_module_to_header_file_map()
    duplicates = CollectionTools.find_duplicate_values(header_to_module_map)
    return duplicates

def print_duplicate_headers(duplicates):
    for file, modules in sorted(duplicates.iteritems()):
        print "%s:%s" % (file, ",".join(sorted(modules)))

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.INFO)
    Configurator().default()

    duplicates = determine_duplicates()
    logging.info("%i duplicate (i.e. in more than than module spec) headers found" % (len(duplicates)))
    print_duplicate_headers(duplicates)
        

if __name__ == "__main__":
    main()
