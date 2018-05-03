#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.dependency.module.linkdeps_if import ModuleLinkDepsSupply
from base.module_lister import HTMLModuleLister
from base.modules_if import ModuleListSupply
from commons.configurator import Configurator
from commons.core_util import SetValuedDictTools
from optparse import OptionParser
import logging
import sys

config_module_list_supply = ModuleListSupply()
config_module_link_deps_supply = ModuleLinkDepsSupply()

class UnreferencedModuleListSupply(ModuleListSupply):

    
    def __init__(self, module_list_supply):
        self.__module_list_supply = module_list_supply
    

    def get_module_list(self):
        link_deps = config_module_link_deps_supply.get_module_link_deps_graph()
        referenced_modules = set(edge.get_to_node() for edge in link_deps.edges())
        return (module 
                for module in self.__module_list_supply.get_module_list()
                if module not in referenced_modules) 


    def get_files_for_module(self, module):
        return self.__module_list_supply.get_files_for_module( module)


    def is_external_module(self, module):
        return self.__module_list_supply.is_external_module( module)


    def get_module_size(self, module):
        return self.__module_list_supply.get_module_size(module)


    def get_max_module_size(self):
        return self.__module_list_supply.get_max_module_size()


    def get_min_module_size(self):
        return self.__module_list_supply.get_min_module_size()
    
    def get_module_descriptors(self):
        return ((descriptor_file, module_name) 
                for (descriptor_file, module_name) in self.__module_list_supply.get_module_descriptors()
                if module_name in self.get_module_list()) 

class ListModulesRunner(object):
    # TODO add option to output the count of incoming and outgoing dependencies per module 
    # TODO add option to query dependencies 

    
    def __init__(self, module_list_supply):
        self.__module_list_supply = module_list_supply
    
    
    @classmethod
    def __create_option_parser(cls):
        parser = OptionParser(usage="usage: %prog [options]", 
                              description="List modules.", 
                              add_help_option=False)
        parser.add_option("", "--html", action="store_true", dest="output_html", help="Output as HTML (text/CSV otherwise)")
        parser.add_option("-a", "--all", action="store_true", dest="all", help="Output all modules")
        parser.add_option("-d", "--duplicates", action="store_true", dest="duplicates", help="Output duplicate module names")
        parser.add_option("-u", "--unreferenced", action="store_true", dest="unreferenced", help="Output unreferenced modules (warning: this considers the active DependencyFilterConfiguration!!!)")
        parser.add_option("-h", "--help", action="store_true", dest="help", help="Print this help and exit.")
        return parser
    
    @staticmethod
    def get_module_list(module_list_supply):
        return sorted(module_list_supply.get_module_descriptors())
    
    def __output(self, module_list_supply, html):
        
        if html:
            HTMLModuleLister(output_file=sys.stdout, analysis_info=(1,2,3), module_list_supply=module_list_supply).write()
        else:
            for (descriptor_file, module_name) in self.get_module_list(module_list_supply):
                print "%s,%s" % (descriptor_file, module_name)
    
    
    def process(self, args):
        parser = self.__create_option_parser()
        (options, args) = parser.parse_args(args=args)
        
        if options.all:
            self.__output(module_list_supply=self.__module_list_supply, html=options.output_html)
        
        if options.duplicates:            
            if hasattr(config_module_list_supply, "get_module_descriptors"):
                print "Duplicate module names:"
                name_to_descriptors = SetValuedDictTools.convert_from_itemiterator((y,x) for (x,y) in self.get_module_list(self.__module_list_supply))
                for (module_name, descriptor_files) in name_to_descriptors.iteritems():
                    if len(descriptor_files) > 1:
                        print module_name

        if options.unreferenced:
            self.__output(module_list_supply=UnreferencedModuleListSupply(module_list_supply=self.__module_list_supply), html=options.output_html)
        

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
    Configurator().default()
    
    ListModulesRunner(module_list_supply=config_module_list_supply).process(sys.argv)
    

if __name__ == "__main__":
    main()
