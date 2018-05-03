#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 24.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import (DependencyFilterConfiguration, 
    DependencyFilter)
from base.dependency.dependency_if_deprecated import DependencyParser
from base.dependency.module.linkdeps_if import ModuleLinkDepsSupply
from base.modules_if import ModuleListSupply
from commons.config_if import ConfigDependent
import logging
import warnings

config_link_dependency_parser = DependencyParser
config_outputter_config = DependencyFilterConfiguration()
config_dependency_filter_class = DependencyFilter
config_module_list = ModuleListSupply()

class OnTheFlyModuleLinkDepsSupply(ModuleLinkDepsSupply, ConfigDependent):
    def __init__(self, outputter_config=None, link_dependency_parser=None):
        ModuleLinkDepsSupply.__init__(self)
        self.__logger = logging.getLogger(self.__class__.__module__)
        if link_dependency_parser == None:
            self.__link_dependency_parser = config_link_dependency_parser()
        else:
            assert isinstance(link_dependency_parser, DependencyParser) 
            self.__link_dependency_parser = link_dependency_parser
            
        if outputter_config == None:
            self.__outputter_config = config_outputter_config
        else:
            assert isinstance(outputter_config, DependencyFilterConfiguration)    
            self.__outputter_config = outputter_config
        
        self.__module_link_deps_graph = None
    
    def __create_module_link_deps_graph(self):
        self.__logger.info("Determine module link dependencies")
        
        self.__link_dependency_parser.process()
        dependency_filter = config_dependency_filter_class(config=self.__outputter_config, module_list=config_module_list.get_module_list())
        self.__link_dependency_parser.output(dependency_filter)
        module_link_deps_graph = dependency_filter.graph()
        self.__link_dependency_parser = None
        self.__outputter_config = None
        return module_link_deps_graph
    
#    def __get_module_link_deps(self):
#        warnings.warn("use get_module_link_deps_graph instead", DeprecationWarning)
#        if self.__module_link_deps_graph == None:
#            self.__module_link_deps_graph = self.__create_module_link_deps_graph()
#        return [(edge.get_from_node(),edge.get_to_node()) 
#                for edge in self.__module_link_deps_graph.edges()]

    def get_module_link_deps_graph(self):
        if self.__module_link_deps_graph == None:
            self.__module_link_deps_graph = self.__create_module_link_deps_graph()
        return self.__module_link_deps_graph.immutable()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
