'''
Created on 20.02.2012

@author: SIGIESEC
'''
import unittest
from systems.cab.dependency_output import CABFinestLevelModuleGrouper,\
    CABTopLevelModuleGrouper


class CABFinestLevelModuleGrouperTest(unittest.TestCase):


    def test1(self):
        modules = ["BTC.CAB.TimeSeries.API", "BTC.CAB.TimeSeries.API.TestSupport", "BTC.CAB.TimeSeries.API.Test"]
        testee = CABFinestLevelModuleGrouper(modules=modules, internal_modules=modules)
        self.assertEquals(["BTC.CAB.TimeSeries.API"], sorted(testee.node_group_prefixes()))        

class CABTopLevelModuleGrouperTest(unittest.TestCase):


    def test1(self):
        modules = ["BTC.CAB.TimeSeries.API", "BTC.CAB.TimeSeries.API.TestSupport", "BTC.CAB.TimeSeries.API.Test"]
        testee = CABTopLevelModuleGrouper(modules=modules, internal_modules=modules)
        self.assertEquals(["BTC.CAB.TimeSeries"], sorted(testee.node_group_prefixes()))        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()