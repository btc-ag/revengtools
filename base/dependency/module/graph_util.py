#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 21.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import (NodeColorer, 
    DependencyFilterConfiguration, ModuleGrouper)
from base.dependency.dependency_output_util import (NodeSizeLabelDecorator, 
    NodeSizeScalingDecorator, DependencyFilterOutputter, 
    FileRevisionNodeAndGraphDecorator, ScalingTypes, ModuleColorNodeDecorator, 
    TerminalNodeDecorator, NodeWeightedDepsScalingDecorator)
from base.modules_if import ModuleListSupply
from commons.config_if import ConfigDependent
from commons.core_util import isinstance_or_duck
from commons.graph.output_if import DecoratorSet
from itertools import ifilter
import logging
import sys

class ModuleListHelper(object):
    @staticmethod
    def filter_omitted(modules, filter_config):
        assert isinstance_or_duck(filter_config, DependencyFilterConfiguration)
        return ifilter(lambda module:filter_config.skip_module(module) 
                       or filter_config.skip_module_as_source(module) 
                       or filter_config.skip_module_as_target(module), modules)

    @staticmethod
    def get_omitted_modules(module_list_supply, dependency_filter_config_class):
        assert isinstance_or_duck(module_list_supply, ModuleListSupply)
        modules = list(module_list_supply.get_module_list())
        filter_config = dependency_filter_config_class(modules=modules)
        return ModuleListHelper.filter_omitted(modules, filter_config)
    
    @staticmethod
    def get_omitted_modules_with_size(module_list_supply, dependency_filter_config_class):
        assert isinstance_or_duck(module_list_supply, ModuleListSupply)
        omitted_modules = ModuleListHelper.get_omitted_modules(module_list_supply, dependency_filter_config_class)
        return ((module, module_list_supply.get_module_size(module)) 
                for module in omitted_modules)
        
    @staticmethod
    def filter_ungrouped(modules, module_grouper):
        assert isinstance_or_duck(module_grouper, ModuleGrouper)
        return (module for module in modules if not module_grouper.get_node_group_prefix(module))

    @staticmethod
    def get_ungrouped_modules(module_list_supply, module_grouper_class):
        assert isinstance_or_duck(module_list_supply, ModuleListSupply)
        modules = list(module_list_supply.get_module_list())
        module_grouper = module_grouper_class(modules)
        return ModuleListHelper.filter_ungrouped(modules, module_grouper)

config_module_list_supply = ModuleListSupply()

class ModuleSizer(ConfigDependent):
    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)

    def get_module_size(self, node):
        if config_module_list_supply.is_external_module(node):
            self.__logger.debug("is external module, ignoring: %s", node)
            return None
        else:
            return config_module_list_supply.get_module_size(node)
    
class ModuleSizeLabelDecorator(NodeSizeLabelDecorator, ModuleSizer):
    def __init__(self, *args, **kwargs):
        NodeSizeLabelDecorator.__init__(self, 
                                        size_func=self.get_module_size, 
                                        *args, **kwargs)
        ModuleSizer.__init__(self)
        
    
class ModuleSizeScalingDecorator(NodeSizeScalingDecorator, ModuleSizer):
    def __init__(self, *args, **kwargs):
        NodeSizeScalingDecorator.__init__(self, 
                                          size_func=self.get_module_size, 
                                          *args, **kwargs)
        ModuleSizer.__init__(self)

class ModuleWeightedDepsScalingDecorator(NodeWeightedDepsScalingDecorator, ModuleSizer):
    def __init__(self, *args, **kwargs):
        NodeWeightedDepsScalingDecorator.__init__(self, 
                                          size_func=self.get_weighted_module_deps, 
                                          elementary_node_size_func = self.get_module_size,
                                          *args, **kwargs)
        ModuleSizer.__init__(self)
                           
config_node_colorer = NodeColorer()

class DefaultModuleDependencyFilterOutputter(DependencyFilterOutputter, ConfigDependent):

    def __init__(self, decorator_config=None, *args, **kwargs):
        if decorator_config == None:
            decorator_config = DecoratorSet()
        decorator_config.add_graph_decorators([FileRevisionNodeAndGraphDecorator()])
        decorator_config.add_node_label_decorators \
            ([ModuleSizeLabelDecorator(),
              ModuleSizeScalingDecorator(3, 8, ScalingTypes.RADICAL),
              ModuleColorNodeDecorator(config_node_colorer),
              TerminalNodeDecorator(),
              ])
        DependencyFilterOutputter.__init__(self,
                                           decorator_config=decorator_config,
                                           *args, **kwargs)


