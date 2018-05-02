# -*- coding: UTF-8 -*-

'''
Created on 26.09.2010

@author: SIGIESEC
'''
from commons.core_util import SuffixMapper
from epm.dependency_output import EPMDependencyFilterConfiguration
from epm.epm_physical_if import PhysicalModuleTypes, PhysicalModuleDescriber

class PythonPhysicalModuleDescriber(PhysicalModuleDescriber):
    module_type_suffix_mapper = SuffixMapper(dict({'_if': (PhysicalModuleTypes.Interface, ),
                                     '_run': (PhysicalModuleTypes.Configurator, ),
                                     '_util': (PhysicalModuleTypes.InterfaceUtility, ),
                                     '_base': (PhysicalModuleTypes.InterfaceBaseImplementation, ),
                                     '_default': (PhysicalModuleTypes.InterfaceDefaultImplementation, ),
                                     '_test': (PhysicalModuleTypes.ImplementationTest, ),
                                     '': (PhysicalModuleTypes.Implementation, )}))
    physical_type_exceptions = dict()
        
    def get_physical_module_types(self, module):
        if module.startswith('configuration.'):
            return (PhysicalModuleTypes.Configuration, )
        elif module in self.physical_type_exceptions:
            return self.physical_type_exceptions[module]        
        else:
            return self.module_type_suffix_mapper.get_value(module)

# TODO Kann man prüfen, ob der deklarierte Modultyp stimmt? Vermutlich geht das nur
# in einigen FÄllen. Man könnte bei einem Interface prüfen, ob alle Methoden abstrakt sind;
# bei einem Test, ob eine Testklasse enthalten ist.

class PythonEPMDependencyOutputterConfiguration(EPMDependencyFilterConfiguration):
    # TODO class can be removed
    pass
