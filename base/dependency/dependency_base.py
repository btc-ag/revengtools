'''
Created on 08.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import (ModuleGrouper, 
    DependencyFilterConfiguration)
from commons.core_util import PrefixMapper, CollectionTools
from commons.graph.attrgraph_base import NullNodeGrouper
from commons.graph.attrgraph_if import Colors
import logging

class NullModuleGrouper(NullNodeGrouper, ModuleGrouper):
    pass

class BaseSuffixModuleGrouper(ModuleGrouper):    
    def __init__(self, modules=None):
        ModuleGrouper.__init__(self, modules)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__prefix_mapper = None
        self.__prefixes = None
        if modules != None:
            self.configure_nodes(modules)

    def _determine_node_group_prefixes(self, nodes):
        raise NotImplementedError(self.__class__)

    def configure_nodes(self, nodes):
        self.__prefixes = set(self._determine_node_group_prefixes(nodes))
        self.__prefix_mapper = PrefixMapper(CollectionTools.identity_dict(self.__prefixes))
    
    def get_node_group_prefix(self, module):
        return self.__prefix_mapper.get_value(module)
    
    def node_group_prefixes(self):
        if self.__prefixes == None:
            self.__logger.warning("Using unconfigured module grouper")
        return self.__prefixes

class BaseDependencyFilterConfiguration(DependencyFilterConfiguration):
    focus_on_node_groups = []

    def __init__(self, modules, *args, **kwargs):
        DependencyFilterConfiguration.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__module_grouper = self._create_module_grouper(modules)
    
    def get_skip_module_types_as_source(self):
        return ()

    def skip_module(self, _module):
        return False
    
    def skip_module_as_source(self, _source):
        return False
    
    def skip_module_as_target(self, _target):
        return False
    
    def skip_edge(self, _source, _target):
        return False
    
    def get_node_color(self, _node):
        return Colors.WHITE

    def get_edge_color(self, _source, _target):
        return Colors.BLACK
    
    def _create_module_grouper(self, modules):
        return NullModuleGrouper()
    
    def get_module_grouper(self):
        return self.__module_grouper
    
    def clone(self, modules):
        return self.__class__(modules=modules)
