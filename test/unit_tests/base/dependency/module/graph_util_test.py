'''
Created on 01.05.2012

@author: SIGIESEC
'''
from base.dependency.dependency_default import NullDependencyFilterConfiguration
from base.dependency.dependency_if import DependencyFilterConfiguration
from base.dependency.module.graph_util import ModuleListHelper
from test.unit_tests.test_helper import DefaultModuleListSupply
import unittest

class AllDependencyFilterConfiguration(DependencyFilterConfiguration):
    def __init__(self, modules=None):
        pass
    
    def skip_module(self, _module):
        return True

    def skip_module_as_source(self, _source):
        return True

    def skip_module_as_target(self, _target):
        return True

    def skip_edge(self, _source, _target):
        return True

    def get_edge_color(self, _source, _target):
        raise NotImplementedError(self.__class__)

    def get_module_grouper(self):
        raise NotImplementedError(self.__class__)

    def clone(self, modules):
        raise NotImplementedError(self.__class__)

class ModuleListHelperTest(unittest.TestCase):
    
    def test_filter_omitted_null_no_modules(self):
        self.assertEqual([], list(ModuleListHelper.filter_omitted(modules=[], filter_config=NullDependencyFilterConfiguration())))

    def test_filter_omitted_null_some_modules(self):
        self.assertEqual([], list(ModuleListHelper.filter_omitted(modules=["a", "b"], filter_config=NullDependencyFilterConfiguration())))

    def test_filter_omitted_all_no_modules(self):
        self.assertEqual([], list(ModuleListHelper.filter_omitted(modules=[], filter_config=AllDependencyFilterConfiguration())))

    def test_filter_omitted_all_some_modules(self):
        self.assertEqual(["a", "b"], list(ModuleListHelper.filter_omitted(modules=["a", "b"], filter_config=AllDependencyFilterConfiguration())))

    def test_get_omitted_modules_with_size_some(self):
        self.assertEqual([("A",0),("B",0)], list(ModuleListHelper.get_omitted_modules_with_size(DefaultModuleListSupply(modules=["A","B"]), AllDependencyFilterConfiguration)))
    