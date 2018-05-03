# -*- coding: UTF-8 -*-

'''
Created on 29.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.core_if import EnumerationItem, Enumeration

class _PhysicalModuleType(EnumerationItem):
    pass

# TODO braucht man nicht vielleicht eine Hierarchie von Modultypen?
class PhysicalModuleTypes(Enumeration):
    _type = _PhysicalModuleType
    Interface = _PhysicalModuleType()
    Implementation = _PhysicalModuleType()
    Framework = _PhysicalModuleType()
    Configurator = _PhysicalModuleType()
    Configuration = _PhysicalModuleType()
    InterfaceUtility = _PhysicalModuleType()
    InterfaceBaseImplementation = _PhysicalModuleType()
    InterfaceDefaultImplementation = _PhysicalModuleType()
    InterfaceTest = _PhysicalModuleType()
    ImplementationTest = _PhysicalModuleType()
    Marshaling = _PhysicalModuleType()
    InterfaceWrapper = _PhysicalModuleType()
    ImplementationWrapper = _PhysicalModuleType()
    
class PhysicalModuleTypeConstants(object):    
    IMPLEMENTATION_MODULE_TYPES = set([PhysicalModuleTypes.Implementation,
                                       PhysicalModuleTypes.InterfaceUtility,
                                       PhysicalModuleTypes.InterfaceDefaultImplementation,
                                       PhysicalModuleTypes.InterfaceBaseImplementation,
                                       ])
    INTERFACE_MODULE_TYPES = set([
                                   PhysicalModuleTypes.Framework,
                                   PhysicalModuleTypes.Interface,
                               ])
    WRAPPER_MODULE_TYPES = set([
                                   PhysicalModuleTypes.ImplementationWrapper,
                                   PhysicalModuleTypes.InterfaceWrapper,
                               ])
    TEST_MODULE_TYPES = set([PhysicalModuleTypes.ImplementationTest,
                             PhysicalModuleTypes.InterfaceTest])
    IRRELEVANT_MODULE_TYPES = set([PhysicalModuleTypes.ImplementationTest,
                                   PhysicalModuleTypes.InterfaceTest,
                                   PhysicalModuleTypes.Configuration,
                                   PhysicalModuleTypes.Configurator,
                                   PhysicalModuleTypes.Marshaling,
                                   ])
    
    
class PhysicalModuleDescriber(AutoConfigurable):
    def get_physical_module_types(self, module):
        '''
        @rtype: tuple of PhysicalModuleType values
        '''
        raise NotImplementedError        

