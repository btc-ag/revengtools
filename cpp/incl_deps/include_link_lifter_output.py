# -*- coding: UTF-8 -*-
'''
Created on 13.10.2010

@author: SIGIESEC
'''
# TODO das hier ist eigentlich so überflüssig. Man müsste epm.cpp.PhysicalModuleDescriber 
# entsprechend anpassen, dass auch C++-spezifische Modultypen für Includes unterstützt werden. 
from base.dependency.dependency_base import BaseDependencyFilterConfiguration
from base.dependency.dependency_if import (NodeColorer, 
    DependencyFilterConfiguration, DependencyFilter)
from base.dependency.dependency_output_util import (
    DependencyFilterOutputterTools, NodeSizeScalingDecorator, NodeSizeLabelDecorator)
from base.modules_if import ModuleListSupply
from commons.config_if import ConfigDependent
from commons.graph.attrgraph_if import Colors
from commons.graph.output_if import DecoratorSet
from cpp.cpp_if import VirtualModuleTypes
from cpp.incl_deps.include_link_lifter_if import ModuleLinks

class LiftIncludeLinksOutputterConfiguration(BaseDependencyFilterConfiguration):
    def __init__(self, combined_modules, modules):
        self.combined_modules = combined_modules
        BaseDependencyFilterConfiguration.__init__(self, modules)

    def skip_module(self, _module):
        return BaseDependencyFilterConfiguration.skip_module(self, _module)

    def skip_module_as_source(self, _source):
        return BaseDependencyFilterConfiguration.skip_module_as_source(self, _source)

    def skip_module_as_target(self, _target):
        return BaseDependencyFilterConfiguration.skip_module_as_target(self, _target)

    def skip_edge(self, _source, _target):
        return BaseDependencyFilterConfiguration.skip_edge(self, _source, _target)

    def get_edge_color(self, from_node, _to_node):
        if self.combined_modules and not from_node.endswith(VirtualModuleTypes.DeclarationModule.suffix()) and not from_node.endswith(VirtualModuleTypes.HeaderModule.suffix()):
            return Colors.GREEN
        else:
            return Colors.RED

class LiftIncludeLinksNodeColorer(NodeColorer):
    def get_node_color(self, module):
        if module.endswith(VirtualModuleTypes.DeclarationModule.suffix()):
            return "orange"
        elif module.endswith(VirtualModuleTypes.HeaderModule.suffix()):
            return "yellow"
        elif module.endswith(VirtualModuleTypes.CombinedModule.suffix()):
            return "green"
        elif module.endswith(VirtualModuleTypes.ExtensionSubmodule.suffix()):
            return Colors.RED
        else:
            return Colors.WHITE
        
config_module_list_supply = ModuleListSupply()
config_filter_config_class = DependencyFilterConfiguration
config_filter = DependencyFilter

# TODO diese Klasse sollte entfernt werden
class ModuleLinksOutputter(ConfigDependent):
    @staticmethod     
    def output(module_links, 
               decorator_config, 
               module_group_conf,
               description):
        assert isinstance(module_links, ModuleLinks)
        assert isinstance(decorator_config, DecoratorSet)
        
        dep_filter = config_filter(config=config_filter_config_class(modules=config_module_list_supply.get_module_list()),
                                   module_list=config_module_list_supply.get_module_list())
        assert isinstance(dep_filter, DependencyFilter)
        module_links.universal_output(dep_filter)
        graph = dep_filter.graph()
        # TODO this is not good
        graph.delete_unconnected_nodes()
        my_decorator_config = DecoratorSet()
        my_decorator_config.add_decorator_set(decorator_config)
        incoming_link_counts = module_links.get_incoming_link_counts()
        my_decorator_config.add_node_label_decorators( \
            [NodeSizeScalingDecorator(size_func=lambda node: incoming_link_counts[node] 
                                                if node in incoming_link_counts else None,
                                      min_render_size=2, max_render_size=8)])
#        my_decorator_config.add_node_label_decorators( \
#            [NodeSizeLabelDecorator(size_func=lambda node: incoming_link_counts[node])])
        DependencyFilterOutputterTools.\
            output_detail_and_overview_graph(graph=graph, 
                                             decorator_config=my_decorator_config, 
                                             module_group_conf=module_group_conf,
                                             description=description)
        #return dep_filter
