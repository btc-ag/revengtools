# -*- coding: UTF-8 -*-

'''
Created on 30.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.modules_if import ModuleListSupply
from commons.metric_util import PlainLinesOfCodeMetric
from commons.os_util import AbsoluteFileMetricProcessor, ResourceUnresolvable
from commons.resource_if import ResourceAccessError
import logging
import warnings

config_basic = BasicConfig

class BaseModuleListSupply(ModuleListSupply):

    def __init__(self, resource_resolver=None, file_length_calculator=None, *args, **kwargs):
        ModuleListSupply.__init__(self, *args, **kwargs)
        self.__module_size_map = dict()
        self.__logger = logging.getLogger(self.__class__.__module__ )
#        self.__min_module_size = None
#        self.__max_module_size = None
        if resource_resolver:
            self.__resource_resolver = resource_resolver
        else:
            warnings.warn("Parameter resource_resolver should be set in BaseModuleListSupply constructor", DeprecationWarning)
            self.__resource_resolver = config_basic().get_local_source_resolver()
        if file_length_calculator:
            assert isinstance(file_length_calculator, AbsoluteFileMetricProcessor)
            self.__metric = file_length_calculator
        else:
            warnings.warn("Parameter file_length_calculator should be set in BaseModuleListSupply constructor", DeprecationWarning)
            self.__metric = PlainLinesOfCodeMetric()
    
    def __size_of_rel_to_root(self, rel_to_root_name, module):
        # TODO use consistent terminology for "rel_to_root" and "source_base_dir"
        try:
            resource = self.__resource_resolver.resolve(rel_to_root_name, True)
            size = self.__metric.apply_metric(resource.open())
        except (ResourceUnresolvable, ResourceAccessError), exc:
            self.__logger.warning("Resource %s in module %s cannot be found or read" % (rel_to_root_name, module) )
            self.__logger.info("Reason for previous warning: %s", exc)
            size = 0

        return size

    def get_module_size(self, module):
        """
        Returns the size (or any other measured attributed) according to the configured file_length_calculator 
        of the given module.
        
        Never throws.
        
        @param module:        
        """
        if self.is_external_module(module):
            return 0
        
        if module in self.__module_size_map:
            return self.__module_size_map[module]
        else:
            total_size = 0
            for basename in self.get_files_for_module(module):
                size = self.__size_of_rel_to_root(basename, module=module)
                total_size += size
                                
            self.__module_size_map[module] = total_size
            return total_size
        
#    def get_max_module_size(self, modules = None):
#        if modules == None:
#            modules = self.get_module_list()
#        if self.__max_module_size == None:
#            self.__max_module_size = max(map(self.get_module_size, modules))
#        self.release_file_list()
#        return self.__max_module_size
#
#    def get_min_module_size(self, modules = None):
#        if modules == None:
#            modules = self.get_module_list()
#        if self.__min_module_size == None:
#            self.__min_module_size = min(map(self.get_module_size, modules))
#        self.release_file_list()
#        return self.__min_module_size 
#    
#    def release_file_list(self):
#        pass

    def is_external_module(self, module):
        return module not in self.get_module_list()

    
    