# -*- coding: UTF-8 -*-

'''
Created on 27.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.config_if import ConfigDependent
import os.path
import warnings

class GenericFilesTools(ConfigDependent):
    def __init__(self, basic_config=BasicConfig):
        self.__basic_config = basic_config()
    
    def get_results_dir_filename(self, basename):
        return os.path.join(self.__basic_config.get_results_directory(), basename)

    def get_module_link_deps_basename(self):
        return self.get_results_dir_filename("module_link_deps")

    def get_module_link_deps_csv_filename(self):
        warnings.warn("deprecated, use get_module_link_deps_basename", DeprecationWarning)
        return self.get_module_link_deps_basename() + ".csv"

    def get_module_link_deps_dot_filename(self):
        warnings.warn("deprecated, use get_module_link_deps_basename", DeprecationWarning)
        return self.get_module_link_deps_basename() + ".dot"
