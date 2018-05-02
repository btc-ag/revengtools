#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 22.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class FileIncludeDepsSupply(AutoConfigurable):
    def get_file_include_deps(self):
        """
        @return: file-level include dependencies 
        @rtype: collection of tuples of source and destination paths (relative to project root)
        """
        raise NotImplementedError

class ModuleIncludeDepsSupply(AutoConfigurable):
    def get_module_include_deps(self):
        raise NotImplementedError
    
# TODO align interface with FileIncludeDepsSupply...
class IncludeDependencyGenerator(AutoConfigurable):
    # TODO document...
    
    def generate(self):
        raise NotImplementedError
    
    def incremental_generate(self):
        raise NotImplementedError
