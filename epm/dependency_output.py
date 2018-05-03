#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 23.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_base import BaseDependencyFilterConfiguration
from base.dependency.dependency_if import NodeColorer, ModuleGrouper
from commons.core_util import CollectionTools
from commons.graph.attrgraph_if import Colors, NodeAttributes
from commons.graph.attrgraph_util import NodeGroup
from commons.graph.output_base import BaseNodeDecorator, BaseEdgeDecorator
from epm.epm_mapper_util import ModuleTypesTools
from epm.epm_physical_if import (PhysicalModuleTypes, PhysicalModuleDescriber, 
    PhysicalModuleTypeConstants)
from base.modules_if import ModuleListSupply

config_physical_module_describer = PhysicalModuleDescriber()
config_module_grouper = ModuleGrouper

class EPMModuleTypeDecoratorBase(object):
    def types_of_single_module(self, node):
        return (PhysicalModuleTypes.name(ptype) 
                for ptype in config_physical_module_describer.get_physical_module_types(node))

    
    def types_of_all_modules(self, node):
        if isinstance(node, NodeGroup):
            modules = self._graph().node_attr(node, NodeAttributes.GROUPED_NODES)
            types = CollectionTools.union_all(self.types_of_single_module(module) for module in modules)
        else:
            types = self.types_of_single_module(node)
        return types

class EPMModuleTypeNodeDecorator(BaseNodeDecorator, EPMModuleTypeDecoratorBase):

    def decorate(self, node):
        types = self.types_of_all_modules(node)
        return "(%s)" % (",".join(types),)

class EPMModuleTypeEdgeDecorator(BaseEdgeDecorator, EPMModuleTypeDecoratorBase):

    def decorate(self, edge):
        from_types = self.types_of_all_modules(edge.get_from_node())
        to_types = self.types_of_all_modules(edge.get_to_node())
        return ["(%s->%s)" % (",".join(from_types), ",".join(to_types))]

class EPMDependencyFilterConfigurationInternal(BaseDependencyFilterConfiguration):
    def __init__(self, module_grouper_class, physical_module_describer, focus_on=None, *args, **kwargs):
        self.__module_grouper_class = module_grouper_class
        self.__physical_module_describer = physical_module_describer
        self.__focus_on = focus_on
        BaseDependencyFilterConfiguration.__init__(self, *args, **kwargs)

    def _create_module_grouper(self, modules):
        return self.__module_grouper_class(modules)

    def skip_module(self, module):
        return module.startswith("_")

    def get_skip_module_types_as_source(self):
        return CollectionTools.union_all((PhysicalModuleTypeConstants.WRAPPER_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.IRRELEVANT_MODULE_TYPES))

    focus_on_node_groups = None

    def skip_module_as_source(self, source):
        module_types = self.__physical_module_describer.get_physical_module_types(source)

        type_skip = ModuleTypesTools.all_in_list(module_types, self.get_skip_module_types_as_source())

        return type_skip

    def skip_module_as_target(self, target):
        return False

    def skip_edge(self, source, target):
        if self.__focus_on:
            group_skip = self.get_module_grouper().get_node_group_prefix(source) not in self.__focus_on \
                and self.get_module_grouper().get_node_group_prefix(target) not in self.__focus_on
        else:
            group_skip = False
        return group_skip

    def get_edge_color(self, source, target):
        #if self.__
        return Colors.BLACK
    
config_module_list_supply = ModuleListSupply()

class EPMDependencyFilterConfiguration(EPMDependencyFilterConfigurationInternal):
    def __init__(self, focus_on=None, module_grouper_class=None, physical_module_describer=None, modules=None, *args, **kwargs):
        if module_grouper_class==None:
            module_grouper_class = config_module_grouper
        if physical_module_describer==None:
            physical_module_describer = config_physical_module_describer
        if modules==None:
            modules = config_module_list_supply.get_module_list()
        EPMDependencyFilterConfigurationInternal.__init__(self, focus_on=focus_on,
                                                          modules=modules,
                                                          module_grouper_class=module_grouper_class, 
                                                          physical_module_describer=physical_module_describer, 
                                                          *args, **kwargs)

class EPMInterfaceOnlyDependencyFilterConfiguration(BaseDependencyFilterConfiguration):
    def get_skip_module_types_as_source(self):
        return CollectionTools.union_all((PhysicalModuleTypeConstants.IMPLEMENTATION_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.WRAPPER_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.IRRELEVANT_MODULE_TYPES))

class EPMWrapperOnlyDependencyFilterConfiguration(BaseDependencyFilterConfiguration):
    def get_skip_module_types_as_source(self):
        return CollectionTools.union_all((PhysicalModuleTypeConstants.IMPLEMENTATION_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.INTERFACE_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.IRRELEVANT_MODULE_TYPES))

class EPMTestOnlyDependencyFilterConfiguration(BaseDependencyFilterConfiguration):
    def get_skip_module_types_as_source(self):
        return CollectionTools.union_all((PhysicalModuleTypeConstants.IMPLEMENTATION_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.INTERFACE_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.WRAPPER_MODULE_TYPES,
                                          PhysicalModuleTypeConstants.IRRELEVANT_MODULE_TYPES)) - PhysicalModuleTypeConstants.TEST_MODULE_TYPES


class EPMNodeColorer(NodeColorer):
    def get_node_color(self, node):
        module_types = config_physical_module_describer.get_physical_module_types(node)
        module_type = ModuleTypesTools.get_regular_type(module_types)
        if module_type == None:
            return Colors.PURPLE
        else:
            # TODO use a map  
            if module_type in [PhysicalModuleTypes.ImplementationTest, PhysicalModuleTypes.InterfaceTest]:
                return Colors.SALMON
            elif module_type == PhysicalModuleTypes.Configurator:
                return Colors.YELLOW
            elif module_type == PhysicalModuleTypes.Configuration:
                return Colors.RED
            elif module_type in [PhysicalModuleTypes.Interface]:
                return Colors.DARKGREEN
            elif module_type in [PhysicalModuleTypes.InterfaceUtility]:
                return Colors.GREEN
            elif module_type in [PhysicalModuleTypes.InterfaceBaseImplementation, PhysicalModuleTypes.InterfaceDefaultImplementation]:
                return Colors.GREENYELLOW
            elif module_type in [PhysicalModuleTypes.Marshaling, PhysicalModuleTypes.InterfaceWrapper, PhysicalModuleTypes.ImplementationWrapper]:
                return Colors.RED
            return Colors.WHITE


if __name__ == "__main__":
    import doctest
    doctest.testmod()
