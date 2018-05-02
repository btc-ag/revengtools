# -*- coding: UTF-8 -*-
'''
Created on 17.06.2011

@author: SIGIESEC
'''
from commons.core_util import SuffixMapper
from epm.epm_physical_if import PhysicalModuleTypes, PhysicalModuleDescriber
import re

class CSharpPhysicalModuleDescriber(PhysicalModuleDescriber):
    """
    >>> map(PhysicalModuleTypes.name, CSharpPhysicalModuleDescriber().get_physical_module_types("BTC.AMM.Test.Server"))
    ['ImplementationTest', 'InterfaceTest']
    """
    module_type_suffix_mapper = SuffixMapper(dict({
                                # Appeared in CoreAssetBase.Net
                                 'Api': (PhysicalModuleTypes.Interface, ),
                                 'Impl': (PhysicalModuleTypes.Implementation, ),
                                 'Common': (PhysicalModuleTypes.Framework, ),                                 
                                 'API': (PhysicalModuleTypes.Interface, ),
                                # Appeared in AMM
                                 'WinS': (PhysicalModuleTypes.ImplementationWrapper, ),
                                 'WebS': (PhysicalModuleTypes.ImplementationWrapper, ),
                                # Other
                                 'Process': (PhysicalModuleTypes.Configurator, ),
                                 'Configurator': (PhysicalModuleTypes.Configurator, ),
                                 'Util': (PhysicalModuleTypes.InterfaceUtility, ),
                                 'Base': (PhysicalModuleTypes.InterfaceBaseImplementation, ),
                                 'Default': (PhysicalModuleTypes.InterfaceDefaultImplementation, ),
                                 'Test': (PhysicalModuleTypes.ImplementationTest, ),
                                 'Mock': (PhysicalModuleTypes.ImplementationTest, ),
                                 'Playground': (PhysicalModuleTypes.ImplementationTest, ),
                                 'Sandbox': (PhysicalModuleTypes.ImplementationTest, ),
                                 'KomStub': (PhysicalModuleTypes.Marshaling, ),
                                 'KomDispatcher': (PhysicalModuleTypes.Marshaling, ),
                                 'Service': (PhysicalModuleTypes.ImplementationWrapper, ),
                                 'Proxy': (PhysicalModuleTypes.Marshaling, ),
                                 'ServiceAPI': (PhysicalModuleTypes.InterfaceWrapper, ),
                                 'DemoCPP': (PhysicalModuleTypes.Configurator, ),
                                 'DemoApp': (PhysicalModuleTypes.Configurator, ),
                                 'Demo': (PhysicalModuleTypes.Configurator, ),
                                 }))
    regex_map = ((re.compile('[.]Test[.]'), 
                  (PhysicalModuleTypes.ImplementationTest, PhysicalModuleTypes.InterfaceTest, ),),
                 )
    physical_type_exceptions = dict()
    
    def __init__(self, default_types=(PhysicalModuleTypes.Implementation, )):
        self.__default_types = default_types

    def get_physical_module_types(self, module):
        if module in self.physical_type_exceptions:
            return self.physical_type_exceptions[module]        
        else:
            suffix_mapper_result = self.module_type_suffix_mapper.get_value(module)
            if suffix_mapper_result:
                return suffix_mapper_result 
            else:
                for (regex, types) in self.regex_map:
                    if regex.search(module):
                        return types
                return self.__default_types


if __name__ == "__main__":
    import doctest
    doctest.testmod()
