"""
Created on 29.09.2012

@author: CHBEST
"""

from __future__ import absolute_import
from os import path
from base.modules_if import ModuleListSupply

class TestDirectoryHelper(object):
    
    @staticmethod
    def getTestmodulesPrefix():
        return "test.unit_tests"
    
    @staticmethod
    def getTestmoduleDirectory():
        return path.normpath("test\\unit_tests")

class DefaultModuleListSupply(ModuleListSupply):
    def __init__(self, modules):
        self.__modules = list(modules)

    def get_module_list(self):
        return iter(self.__modules)

    def get_files_for_module(self, module):
        # TODO: ?
        return ()

    def is_external_module(self, module):
        return module not in self.__modules

    def get_module_size(self, module):
        return 0

    def get_max_module_size(self):
        return 0

    def get_min_module_size(self):
        return 0
