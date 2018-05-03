# -*- coding: UTF-8 -*-

'''
Created on 29.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import ModuleGrouper
from base.dependency.module.linkdeps_if import ModuleLinkDepsSupply
from base.modules_if import ModuleListSupply
from epm.epm_checker_if import EPMArchitecturalStyleChecker
from epm.epm_mapper_util import ModuleTypesTools
from epm.epm_physical_if import PhysicalModuleDescriber, PhysicalModuleTypes
import logging

config_physical_module_describer = PhysicalModuleDescriber()
config_module_list_supply = ModuleListSupply()
config_module_grouper = ModuleGrouper

class DefaultEPMArchitecturalStyleChecker(EPMArchitecturalStyleChecker):
    allowed_targets_for_source = \
        dict({PhysicalModuleTypes.Configuration: set(PhysicalModuleTypes.values()) - set([PhysicalModuleTypes.InterfaceTest, PhysicalModuleTypes.ImplementationTest]),
              PhysicalModuleTypes.Configurator: set(PhysicalModuleTypes.values()) - set([PhysicalModuleTypes.InterfaceTest, PhysicalModuleTypes.ImplementationTest]),
              PhysicalModuleTypes.Interface: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.Framework),
              PhysicalModuleTypes.InterfaceBaseImplementation: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.InterfaceUtility, PhysicalModuleTypes.Framework),
              PhysicalModuleTypes.InterfaceDefaultImplementation: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.InterfaceUtility, PhysicalModuleTypes.Framework),
              PhysicalModuleTypes.Implementation: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.InterfaceBaseImplementation, PhysicalModuleTypes.InterfaceDefaultImplementation, PhysicalModuleTypes.InterfaceUtility, PhysicalModuleTypes.Framework),
              PhysicalModuleTypes.ImplementationTest: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.InterfaceUtility, PhysicalModuleTypes.Framework),
              PhysicalModuleTypes.InterfaceTest: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.InterfaceUtility, PhysicalModuleTypes.Framework),
              PhysicalModuleTypes.InterfaceWrapper: (PhysicalModuleTypes.Framework,),
              PhysicalModuleTypes.ImplementationWrapper: (PhysicalModuleTypes.InterfaceWrapper, PhysicalModuleTypes.Framework,),
              PhysicalModuleTypes.InterfaceUtility: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.InterfaceUtility, PhysicalModuleTypes.Framework,),
              PhysicalModuleTypes.Marshaling: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.Framework, ),
              PhysicalModuleTypes.Framework: (PhysicalModuleTypes.Framework, ),
              })
    additional_allowed_targets_for_source_within_module_group_boundaries = \
        dict({PhysicalModuleTypes.Configuration: (),
              PhysicalModuleTypes.Configurator: (),
              PhysicalModuleTypes.Interface: (),
              PhysicalModuleTypes.InterfaceBaseImplementation: (),
              PhysicalModuleTypes.InterfaceDefaultImplementation: (PhysicalModuleTypes.InterfaceBaseImplementation,),
              PhysicalModuleTypes.Implementation: (PhysicalModuleTypes.Implementation,),
              PhysicalModuleTypes.ImplementationTest: (PhysicalModuleTypes.Implementation, PhysicalModuleTypes.ImplementationTest),
              PhysicalModuleTypes.InterfaceTest: (PhysicalModuleTypes.Interface, PhysicalModuleTypes.Implementation, PhysicalModuleTypes.InterfaceTest),
              PhysicalModuleTypes.InterfaceWrapper: (PhysicalModuleTypes.Interface,),
              PhysicalModuleTypes.ImplementationWrapper: (PhysicalModuleTypes.Implementation, ),
              PhysicalModuleTypes.InterfaceUtility: (PhysicalModuleTypes.Implementation, PhysicalModuleTypes.InterfaceBaseImplementation, PhysicalModuleTypes.InterfaceDefaultImplementation),
              PhysicalModuleTypes.Marshaling: (PhysicalModuleTypes.Implementation, ),
              PhysicalModuleTypes.Framework: (),
              })
        
    def __init__(self, module_grouper = None):
        if module_grouper == None:
            # TODO das sollte nicht vorkommen
            module_grouper = config_module_grouper(())
        self.__module_grouper = module_grouper
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def allowed_target_types(self, source_type, same_module_group):
        allowed = set(PhysicalModuleTypes.map(self.allowed_targets_for_source, source_type))
        if same_module_group:
            allowed.update(PhysicalModuleTypes.map(self.additional_allowed_targets_for_source_within_module_group_boundaries, source_type))
        return allowed

    def _is_legal_dependency(self, source, target):
        
        if not config_module_list_supply.is_external_module(target):
            source_types = config_physical_module_describer.get_physical_module_types(source)
            target_types = config_physical_module_describer.get_physical_module_types(target)
            
            # TODO Modulgruppen von source und target bestimmen und vergleichen
            # und zwar die Ebene bestimmen, auf der sie sich unterscheiden
            same_module_group = self.__module_grouper.get_node_group_prefix(source) == self.__module_grouper.get_node_group_prefix(target)             
            is_legal = any(map(lambda source_type:
                    ModuleTypesTools.any_in_list(target_types, 
                        self.allowed_target_types(source_type, same_module_group)), 
                    source_types))
            self.__logger.debug("%s(%s)->%s(%s):%s", source, PhysicalModuleTypes.names(source_types), 
                         target, PhysicalModuleTypes.names(target_types), is_legal)
            return is_legal
        else:
            self.__logger.info("%s->%s (external)", source, target)
            return True
        

    def physical_rule_violations(self, module_deps_supply = ModuleLinkDepsSupply()):
        '''
        
        @param module_deps_supply:
        @type module_deps_supply: ModuleLinkDepsSupply
        '''
        return [edge 
                for edge in module_deps_supply.get_module_link_deps_graph().edges()
                if not self._is_legal_dependency(edge.get_from_node(), edge.get_to_node())]
            