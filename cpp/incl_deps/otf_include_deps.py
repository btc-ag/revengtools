#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 24.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_default import DefaultDependencyFilter
from commons.config_if import ConfigDependent
from cpp.cpp_if import FileToModuleMapSupply
from cpp.incl_deps.include_deps_if import (ModuleIncludeDepsSupply, 
    FileIncludeDepsSupply)
from cpp.incl_deps.include_link_lifter_if import IncludeLinkLifter
import logging
import warnings
from base.modules_if import ModuleListSupply

config_include_link_lifter = IncludeLinkLifter
config_file_include_deps_supply = FileIncludeDepsSupply()
config_module_list = ModuleListSupply()

class OnTheFlyModuleIncludeDepsSupply(ModuleIncludeDepsSupply, ConfigDependent):
    def __init__(self, outputter_config, file_to_module_map_supply = FileToModuleMapSupply()):
        ModuleIncludeDepsSupply.__init__(self)
        self.__module_include_deps_graph = None
        self.__outputter_config = outputter_config
        self.__file_to_module_map_supply = file_to_module_map_supply
        self.__logger = logging.getLogger(self.__class__.__module__)
        
    def __create_module_include_deps_graph(self):
        #    Write to file TODO
        
        dep_filter = DefaultDependencyFilter(config=self.__outputter_config, module_list=config_module_list.get_module_list())
        self.__get_link_lifter().get_module_links().universal_output(dep_filter)
        self.__outputter_config = None

        return dep_filter.graph()

    def get_module_include_deps(self):
        warnings.warn("use get_module_include_deps_graph instead", DeprecationWarning)
        # Check if file exists TODO
        if self.__module_include_deps_graph == None:
            self.__module_include_deps_graph = self.__create_module_include_deps_graph()
        return self.__module_include_deps_graph.edges()

    def get_module_include_deps_graph(self):
        # Check if file exists TODO
        if self.__module_include_deps_graph == None:
            self.__module_include_deps_graph = self.__create_module_include_deps_graph()
        return self.__module_include_deps_graph

    def __get_link_lifter(self):
        self.__logger.info("Lifting file include dependencies to module level")
        lifter = config_include_link_lifter(file_to_module_map_supply=self.__file_to_module_map_supply,
                                            file_include_deps_supply=config_file_include_deps_supply)
        lifter.process(use_mapping_exceptions=False)
        # TODO progress control
        self.__file_to_module_map_supply = None
        
        return lifter
    
#    def get_module_links(self):
#        return self.__get_link_lifter().get_module_links()
     

if __name__ == "__main__":
    import doctest
    doctest.testmod()
