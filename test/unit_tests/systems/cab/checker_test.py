'''
Created on 18.05.2012

@author: SIGIESEC
'''

from systems.cab.checker import CABRuleTools
import ntpath
import posixpath
import unittest


class CSProjTest(object):    
    def __init__(self, assembly_name, root_namespace, csproj_name):
        self.__root_namespace = root_namespace
        self.__assembly_name = assembly_name
        self.__csproj_name = csproj_name
    
    def get_root_namespace(self):
        return self.__root_namespace
        
    def get_assembly_name(self):
        return self.__assembly_name
    
    def get_filename(self):
        return self.__csproj_name
    
#class CSProjCheckerDefaultSmokeTest(unittest.TestCase):
#    def test_basic(self):
#        csproj = CSProjTest(assembly_name="A.B.C", root_namespace="A.B.C", csproj_name="A.B.C.csproj")
#        CSProjCheckerDefault(csproj=csproj)


class CABRuleToolsTest(unittest.TestCase):
    def test_get_rparts_1(self):
        self.assertEqual("", CABRuleTools.get_dirshort("a/BTC/Commons/Core", 0, pathmodule=posixpath))

    def test_get_rparts_2(self):
        self.assertEqual("Core", CABRuleTools.get_dirshort("a/BTC/Commons/Core", 1, pathmodule=posixpath))
    
    def test_get_rparts_3(self):
        self.assertEqual(posixpath.sep.join(("Commons", "Core")), CABRuleTools.get_dirshort("a/BTC/Commons/Core", 2, pathmodule=posixpath))
    
    def test_get_rparts_4(self):
        self.assertEqual("Core", CABRuleTools.get_dirshort("Core", 1, pathmodule=posixpath))
    
    def test_get_rparts_5(self):
        self.assertEqual("Core", CABRuleTools.get_dirshort("Core", 2, pathmodule=posixpath))
                    
    def test_check_path_longer_path(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core", "a/BTC/CAB/Commons/Core", pathmodule=posixpath))

    def test_check_path_longer_mixed_path(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core", "a/BTC/CAB/Commons.Core", pathmodule=posixpath))
 
    def test_check_path_longer_mixed_path_2(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core.TimeSeries", "a/BTC/CAB/Commons.Core.TimeSeries", pathmodule=posixpath))
 
    def test_check_path_longer_all_mixed_path(self):
        self.assertTrue(CABRuleTools.check_path("X.Y.Commons.Core", "a/X.Y.Commons.Core", pathmodule=posixpath))

    def test_check_path_longer_prefix_mixed_path(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core.TimeSeries", "a/BTC/CAB/Commons.Core/TimeSeries", pathmodule=posixpath))
         
    def test_check_path_2(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core", "BTC/CAB/Commons/Core", pathmodule=posixpath))                     
    
    def test_check_path_2_unicode(self):
        self.assertTrue(CABRuleTools.check_path(unicode("BTC.CAB.Commons.Core"), unicode("BTC/CAB/Commons/Core"), pathmodule=posixpath))                     

    def test_check_path_2b(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core", "BTC/CAB/Commons/Core/build", pathmodule=posixpath))                     
    
    def test_check_path_2c(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core", "Commons/Core/build", pathmodule=posixpath))                     
    
    def test_check_path_2d(self):
        self.assertTrue(CABRuleTools.check_path("BTC.CAB.Commons.Core", "Commons/Core", pathmodule=posixpath))                     
    
    def test_check_path_3(self):
        self.assertFalse(CABRuleTools.check_path("BTC.CAB.Commons.Core", "BTC/Commons/Corega", pathmodule=posixpath))                     
    
    def test_check_path_4(self):
        self.assertFalse(CABRuleTools.check_path("BTC.CAB.Commons.Core", "BTC/Commons/Core", pathmodule=posixpath))                     

    def test_check_path_4b(self):
        self.assertFalse(CABRuleTools.check_path("BTC.CAB.Commons.Core", "BTC/CAB/Core", pathmodule=posixpath))  
            
    def test_check_path_5(self):
        self.assertTrue(CABRuleTools.check_path("BTC.Application.Test", "BTC\Application\Test", strict=False, pathmodule=ntpath))
    
    def test_check_path_6(self):
        self.assertFalse(CABRuleTools.check_path("BTC.CAB.Commons.Core", "/Core", pathmodule=posixpath))
        
    def test_transform_project_file_name_1(self):
        # new guideline
        self.assertEquals("BTC.CAB.TimeSeries.NET.API", CABRuleTools.transform_project_file_name("BTC.CAB.TimeSeries.NET.API-net3.5.csproj"))

    def test_transform_project_file_name_2(self):
        # current variant 1
        self.assertEquals("BTC.CAB.TimeSeries.NET.API", CABRuleTools.transform_project_file_name("BTC.CAB.TimeSeries.NET.API.3.5.csproj"))

    def test_transform_project_file_name_3(self):
        # current variant 1
        self.assertEquals("BTC.CAB.TimeSeries.NET.API", CABRuleTools.transform_project_file_name("BTC.CAB.TimeSeries.NET.3.5.API.csproj"))
        
    def test_count_distinct_files_0(self):
        self.assertEquals(1, CABRuleTools.count_distinct_files(["BTC/TimeSeries/CommonsExtensions/BTC.CAB.TimeSeries.NET.CommonsExtensions.csproj"]))
        
    def test_count_distinct_files_1(self):
        self.assertEquals(1, CABRuleTools.count_distinct_files(["BTC/TimeSeries/CommonsExtensions/BTC.CAB.TimeSeries.NET.CommonsExtensions.csproj", 
        "BTC/TimeSeries/CommonsExtensions/BTC.CAB.TimeSeries.NET.CommonsExtensions.3.5.csproj"]))
        
    def test_count_distinct_files_2(self):
        self.assertEquals(2, CABRuleTools.count_distinct_files(["BTC\TimeSeries\API\Test\ObservableProvider\BTC.CAB.TimeSeries.NET.API.Test.ObservableProvider.csproj", 
        "BTC\TimeSeries\API\Test\DecoratorProvider\BTC.CAB.TimeSeries.NET.API.Test.DecoratorProvider.csproj"])) 

    def test_get_correct_directory_1(self):
        candidates = list(CABRuleTools.get_correct_directory("BTC.CAB.TimeSeries.NET.API"))
        self.assertTrue(len(candidates) > 0)
        self.assertEquals(0, len(filter(lambda x: x.find("BTC.CAB") >= 0, candidates)))
        

class FileMSVCDataSupplyTest(unittest.TestCase):
    def test_mine(self):
        # TODO test using temporary file
        pass
        #self.assertEqual("D:\\PRINS-Analyse", FileMSVCDataSupply.canonicalize_capitalization("D:\\prins-analyse"))
