'''
Created on 01.05.2012

@author: SIGIESEC
'''
from epm.epm_mapper_util import ModuleTypesTools
from epm.epm_physical_if import PhysicalModuleDescriber, PhysicalModuleTypes
from test.unit_tests.base.dependency.module.graph_util_test import (
    AllDependencyFilterConfiguration)
from test.unit_tests.epm.cabstyle.dependency_output_test import DefaultModuleListSupply
import unittest

class TestPhysicalModuleDescriber(PhysicalModuleDescriber):
    def __init__(self, map, default):
        self.__map = map
        self.__default = default 

    def get_physical_module_types(self, module):
        if module in self.__map:
            return self.__map[module]
        else:
            return self.__default

class ModuleTypesToolsTest(unittest.TestCase):
    def test_null(self):
        self.assertEquals([], sorted(ModuleTypesTools.get_omitted_modules_by_type(TestPhysicalModuleDescriber(map=dict(), default=PhysicalModuleTypes.Framework), 
                                                 DefaultModuleListSupply(modules=[]), 
                                                 AllDependencyFilterConfiguration)))

    def test_some(self):
        result = dict(ModuleTypesTools.get_omitted_modules_by_type(TestPhysicalModuleDescriber(map=dict({"A": (PhysicalModuleTypes.Implementation,)}), default=(PhysicalModuleTypes.Framework,)), 
                                                 DefaultModuleListSupply(modules=["B", "A", ]), 
                                                 AllDependencyFilterConfiguration))
        self.assertEquals(set([("Implementation",), ("Framework",)]), set(result.keys()))
        self.assertEquals([("A", 0)], sorted(result[("Implementation", )]))
        self.assertEquals([("B", 0)], sorted(result[("Framework", )]))

    def test_some_irregular_types(self):
        result = dict(ModuleTypesTools.get_omitted_modules_by_type(TestPhysicalModuleDescriber(map=dict({"A": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,)}), default=(PhysicalModuleTypes.Framework,)), 
                                                 DefaultModuleListSupply(modules=["B", "A", ]), 
                                                 AllDependencyFilterConfiguration))
        self.assertEquals(set([("Implementation","Interface"), ("Framework",)]), set(result.keys()))
        self.assertEquals([("A", 0)], sorted(result[("Implementation", "Interface")]))
        self.assertEquals([("B", 0)], sorted(result[("Framework", )]))

    def test_some_more_irregular_types(self):
        result = dict(ModuleTypesTools.get_omitted_modules_by_type(TestPhysicalModuleDescriber(map=dict({"A": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,PhysicalModuleTypes.Configuration,)}), default=(PhysicalModuleTypes.Framework,)), 
                                                 DefaultModuleListSupply(modules=["B", "A", ]), 
                                                 AllDependencyFilterConfiguration))
        self.assertEquals(set([("Implementation","Interface","Configuration"), ("Framework",)]), set(result.keys()))
        self.assertEquals([("A", 0)], sorted(result[("Implementation", "Interface","Configuration")]))
        self.assertEquals([("B", 0)], sorted(result[("Framework", )]))

    def test_some_more_of_a_type(self):
        result = dict(ModuleTypesTools.get_omitted_modules_by_type(TestPhysicalModuleDescriber(map=dict({"A": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,PhysicalModuleTypes.Configuration,),
                                                                                                        "B": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,PhysicalModuleTypes.Configuration,)}),
                                                                                                default=(PhysicalModuleTypes.Framework,)), 
                                                 DefaultModuleListSupply(modules=["B", "A",]), 
                                                 AllDependencyFilterConfiguration))
        self.assertEquals(set([("Implementation","Interface","Configuration"),]), set(result.keys()))
        self.assertEquals([("A", 0),("B", 0)], sorted(result[("Implementation", "Interface","Configuration")]))

    def test_module_not_in_default_module_list_supply(self):
        result = dict(ModuleTypesTools.get_omitted_modules_by_type(TestPhysicalModuleDescriber(map=dict({"A": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,PhysicalModuleTypes.Configuration,),
                                                                                                        "B": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,PhysicalModuleTypes.Configuration,)}),
                                                                                                default=(PhysicalModuleTypes.Framework,)), 
                                                 DefaultModuleListSupply(modules=["B",]), 
                                                 AllDependencyFilterConfiguration))
        self.assertEquals(set([("Implementation","Interface","Configuration"),]), set(result.keys()))
        self.assertEquals([("B", 0)], sorted(result[("Implementation", "Interface","Configuration")]))
        
    def test_disjunct_subgroups(self):
        result = dict(ModuleTypesTools.get_omitted_modules_by_type(TestPhysicalModuleDescriber(map=dict({"A": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,),
                                                                                                        "B": (PhysicalModuleTypes.Implementation,PhysicalModuleTypes.Interface,PhysicalModuleTypes.Configuration,)}),
                                                                                                default=(PhysicalModuleTypes.Framework,)), 
                                                 DefaultModuleListSupply(modules=["A","B",]), 
                                                 AllDependencyFilterConfiguration))
        self.assertEquals(set([("Implementation","Interface","Configuration"), ('Implementation', 'Interface')]), set(result.keys()))
        self.assertEquals([("B", 0)], sorted(result[("Implementation", "Interface","Configuration")])) 
        self.assertEquals([("A", 0)], sorted(result[("Implementation", "Interface",)])) 
