'''
Created on 26.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_base import NullModuleGrouper
from base.dependency.module.graph_util import ModuleListHelper
from epm.cabstyle.dependency_output import (
    CABStyleFinestLevelModuleGrouperInternal)
from epm.csharp.mapper import CSharpPhysicalModuleDescriber
from epm.dependency_output import EPMDependencyFilterConfigurationInternal
from test.unit_tests.test_helper import DefaultModuleListSupply
import unittest


class EPMDependencyFilterConfigurationInternalTest(unittest.TestCase):
    def test_no_focus_on(self):
        testee = EPMDependencyFilterConfigurationInternal(focus_on=None, 
                                                          module_grouper_class=NullModuleGrouper, 
                                                          physical_module_describer=CSharpPhysicalModuleDescriber(),
                                                          modules=("A.Test",))
        self.assertTrue(testee.skip_module_as_source("A.Test"))        
        self.assertEquals(["A.Test"], sorted(ModuleListHelper.filter_omitted(["A.Test", "A.Impl"], testee)))
        
    def test_skip_module_as_source(self):
        testee = EPMDependencyFilterConfigurationInternal(focus_on=None, 
                                                          module_grouper_class=NullModuleGrouper, 
                                                          physical_module_describer=CSharpPhysicalModuleDescriber(),
                                                          modules=("A.Test",))
        self.assertTrue(testee.skip_module_as_source("A.Test"))
        self.assertTrue(testee.skip_module_as_source("A.B.C.Test"))
        self.assertTrue(testee.skip_module_as_source("A.B.C.Mock"))
          
    def test_donot_skip_modules_as_source(self):
        testee = EPMDependencyFilterConfigurationInternal(focus_on=None, 
                                                          module_grouper_class=NullModuleGrouper, 
                                                          physical_module_describer=CSharpPhysicalModuleDescriber(),
                                                          modules=("A.Test",))
        self.assertFalse(testee.skip_module_as_source("A.Impl"))
        self.assertFalse(testee.skip_module_as_source("A.API"))
        self.assertFalse(testee.skip_module_as_source("A.Common"))
        self.assertFalse(testee.skip_module_as_source("A.B.C.Util"))
              
    def test_integration_get_omitted_modules(self):
        self.assertEquals(["A.Test.Mine"], sorted(ModuleListHelper.get_omitted_modules(DefaultModuleListSupply(["A.Test.Mine", "B.Impl"]),
                                                lambda modules: EPMDependencyFilterConfigurationInternal(focus_on=None, 
                                                                        module_grouper_class=NullModuleGrouper, 
                                                                        physical_module_describer=CSharpPhysicalModuleDescriber(),
                                                                        modules=modules))))


test_class = CABStyleFinestLevelModuleGrouperInternal

class CABStyleFinestLevelModuleGrouperInternalTest(unittest.TestCase):
    def setUp(self):
        pass        

    def tearDown(self):
        pass

    def testX(self):
        modules = ["A.B", "A.C", "B.C"]
        testee = test_class(modules=modules, internal_modules=modules)
        self.assertEquals(["A", "B"], sorted(testee.node_group_prefixes()))
        self.assertEquals("A", testee.get_node_group_prefix("A.B"))
        self.assertEquals("B", testee.get_node_group_prefix("B.C"))
        
    def testModuleIsModuleGroup(self):
        modules = ["A.B", "A.C", "B.C", "B.C.D"]
        testee = test_class(modules=modules, internal_modules=modules)
        self.assertEquals(["A", "B"], sorted(testee.node_group_prefixes()))
        self.assertEquals("A", testee.get_node_group_prefix("A.B"))
        self.assertEquals("B", testee.get_node_group_prefix("B.C"))
        self.assertEquals("B", testee.get_node_group_prefix("B.C.D"))
        
    def testY(self):
        modules = ["A.B.C.D.1.Suffix", 
                   "A.B.C.D.2.Suffix",
                   "A.B.C.D.3.Suffix",
                   "A.B.C.E.1.Suffix",
                   "A.B.C.E.2.Suffix",
                   "A.B.C.E.3.Suffix",
                   "A.B.C.E.4.Suffix",
                   "A.B.C.F.1.Suffix",
                   "A.B.C.G.Suffix"]
        testee = test_class(modules=modules, internal_modules=modules)
        self.assertEquals("A.B.C.D", testee.get_node_group_prefix("A.B.C.D.1.Suffix"))
        self.assertEquals("A.B.C", testee.get_node_group_prefix("A.B.C.F.1.Suffix"))
        self.assertEquals("A.B.C", testee.get_node_group_prefix("A.B.C.G.Suffix"))
        self.assertEquals(["A.B.C", "A.B.C.D", "A.B.C.E"], sorted(testee.node_group_prefixes()))
        
    def testZ(self):
        modules = ["BTC.CAB.TimeSeries.API", "BTC.CAB.TimeSeries.API.TestSupport", "BTC.CAB.TimeSeries.API.Test"]
        testee = test_class(modules=modules, internal_modules=modules)
        self.assertEquals(["BTC.CAB.TimeSeries.API"], sorted(testee.node_group_prefixes()))

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    