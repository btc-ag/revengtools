# -*- coding: UTF-8 -*-

'''
Created on 26.09.2010

@author: SIGIESEC
'''
from commons.core_util import SuffixMapper
from epm.epm_physical_if import PhysicalModuleTypes, PhysicalModuleDescriber

class CppPhysicalModuleDescriber(PhysicalModuleDescriber):
    module_type_suffix_mapper = SuffixMapper(dict({
                                 'API': (PhysicalModuleTypes.Interface, ),
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
                                 '': (PhysicalModuleTypes.Implementation, )}))
    physical_type_exceptions = dict()

    def get_physical_module_types(self, module):
        if module in self.physical_type_exceptions:
            return self.physical_type_exceptions[module]        
        else:
            return self.module_type_suffix_mapper.get_value(module)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
