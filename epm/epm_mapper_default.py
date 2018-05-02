# -*- coding: UTF-8 -*-

'''
Created on 29.09.2010

@author: SIGIESEC
'''
from epm.epm_logical_if import LogicalEntityTypes
from epm.epm_mapper_if import PhysicalToLogicalMapper
from epm.epm_physical_if import PhysicalModuleTypes, PhysicalModuleDescriber

class DefaultPhysicalToLogicalMapper(PhysicalToLogicalMapper):
    physical_to_logical_type_map = \
        dict({PhysicalModuleTypes.Interface: LogicalEntityTypes.Interface,
              PhysicalModuleTypes.Implementation: LogicalEntityTypes.Component,
              PhysicalModuleTypes.Configurator: LogicalEntityTypes.Configurator,
              PhysicalModuleTypes.Configuration: LogicalEntityTypes.Configurator,
              PhysicalModuleTypes.InterfaceUtility: LogicalEntityTypes.Interface,
              PhysicalModuleTypes.InterfaceBaseImplementation: LogicalEntityTypes.Component,
              PhysicalModuleTypes.InterfaceDefaultImplementation: LogicalEntityTypes.Component,
              PhysicalModuleTypes.InterfaceTest: LogicalEntityTypes.Interface,
              PhysicalModuleTypes.ImplementationTest: LogicalEntityTypes.Component,
              PhysicalModuleTypes.Marshaling: None,
              # TODO Eventuell auch bei LogicalElementTypes Basis- und Default-Implementierungen 
              # unterscheiden. Vererbungsbeziehungen über Komponenten sollten hierauf 
              # beschränkt werden.
              })

class NullModuleDescriber(PhysicalModuleDescriber):
    def get_physical_module_types(self, module):
        return (PhysicalModuleTypes.Framework,)

