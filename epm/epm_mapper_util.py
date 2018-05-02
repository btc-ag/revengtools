'''
Created on 26.09.2010

@author: SIGIESEC
'''
from base.dependency.module.graph_util import ModuleListHelper
from base.modules_if import ModuleListSupply
from commons.core_util import IterTools, isinstance_or_duck
from epm.epm_physical_if import PhysicalModuleDescriber, PhysicalModuleTypes

class ModuleTypesTools(object):
    @staticmethod
    def any_in_list(module_types, possible_types):
        return any(module_type in possible_types for module_type in module_types)

    @staticmethod
    def all_in_list(module_types, allowed_types):
        return all(module_type in allowed_types for module_type in module_types)

    @staticmethod
    def get_regular_type(module_types):
        """
        Returns the single module type if a list of module types contains only one element 
        (i.e. the module has a regular type), or None if the module has no or a mixed type.  
        
        @param module_types: a collection of instances of PhysicalModuleType
        """
        # TODO convert into CollectionTools.get_single_or_default
        if len(module_types) == 1:
            return module_types[0]
        else:
            return None

    @staticmethod
    def get_omitted_modules_by_type(physical_module_describer, module_list_supply, dependency_filter_config_class):
        assert isinstance_or_duck(physical_module_describer, PhysicalModuleDescriber)
        assert isinstance_or_duck(module_list_supply, ModuleListSupply)
        key_func = lambda (module, size):tuple(PhysicalModuleTypes.names(physical_module_describer.get_physical_module_types(module)))
        grouped_modules = IterTools.sort_and_group(key_func, 
                                                   ModuleListHelper.get_omitted_modules_with_size(module_list_supply, dependency_filter_config_class))
        return ((x, tuple(y)) for (x,y) in grouped_modules)
