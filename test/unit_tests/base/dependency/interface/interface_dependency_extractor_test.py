import unittest
import os.path
from base.dependency.interface.interface_dependency_extraction import InterfaceDependencyExtractor,\
    TypeInformation

class TestAnalyserAdapter():
    def __init__(self):
        path = os.path.dirname(__file__) 
        self.xmlResult = {}
        self.xmlResult["BTC.Arch.Modularity.ProblemShowCase.Core.dll"] = open(os.path.join(path,"Core.json"),"r").read()
        self.xmlResult["BTC.Arch.Modularity.ProblemShowCase.ProductComp1.dll"] = open(os.path.join(path,"ProductComp1.json"),"r").read()
        self.xmlResult["BTC.Arch.Modularity.ProblemShowCase.ProductComp2.dll"] = open(os.path.join(path,"ProductComp2.json"),"r").read()
        
    def analyse_dll(self, dllFile):
        return self.xmlResult[dllFile]

class InterfaceDependendencyExtratorTest(unittest.TestCase):
    def setUp(self):
        self.analyser = InterfaceDependencyExtractor(TestAnalyserAdapter())
        self.interfaceDepsMyInt = set(['BTC.Arch.Modularity.ProblemShowCase.ProductComp2.MyDatastore', 'BTC.Arch.Modularity.ProblemShowCase.ProductComp1.MyCalculator'])
    def testAnalyseExportedClasses(self):
        res = self.analyser.analyse_exported_classes("BTC.Arch.Modularity.ProblemShowCase.Core.dll")
        #MyInt wird von Core exportiert
        if not TypeInformation("BTC.Arch.Modularity.ProblemShowCase.Core.MyInt","BTC.Arch.Modularity.ProblemShowCase.Core, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null") in res:
            self.fail()
    def testLeftRightCompareWithoutFilter(self):
        res = self.analyser.left_right_compare(["BTC.Arch.Modularity.ProblemShowCase.ProductComp1.dll", "BTC.Arch.Modularity.ProblemShowCase.ProductComp2.dll"], None)
        res = dict(res)
        
        
        
        #All Target deps should be visible
        self.assertEqual(self.interfaceDepsMyInt, res[TypeInformation("BTC.Arch.Modularity.ProblemShowCase.Core.MyInt","BTC.Arch.Modularity.ProblemShowCase.Core, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null")])
        self.assertEqual(2, len(res[TypeInformation("System.Void","mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089")]))
        self.assertEqual(2, len(res[TypeInformation("System.Type","mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089")]))
    def testLeftRightCompareWithFilter(self):
        res = self.analyser.left_right_compare(["BTC.Arch.Modularity.ProblemShowCase.ProductComp1.dll", "BTC.Arch.Modularity.ProblemShowCase.ProductComp2.dll"], ["BTC.Arch.Modularity.ProblemShowCase.Core.dll"])
        res = dict(res)
        
        #Only two types should be defined
        self.assertEqual(self.interfaceDepsMyInt, res[TypeInformation("BTC.Arch.Modularity.ProblemShowCase.Core.MyInt","BTC.Arch.Modularity.ProblemShowCase.Core, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null")])
        self.assertEqual(0, len(res[TypeInformation("BTC.Arch.Modularity.ProblemShowCase.Core.UnusedType","BTC.Arch.Modularity.ProblemShowCase.Core, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null")]))
        self.assertFalse(any(typeInfo.TypeName == "System.Void" for typeInfo in res.iterkeys()))
        
if __name__ == "__main__":
    unittest.main()
    