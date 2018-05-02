'''
Created on 29.09.2012

@author: CHBEST
'''
import unittest
import process_jenkins
import os
from xml.dom.minidom import parseString

class CABCSharpIntegrationTest(unittest.TestCase):
# TODO the package should be renamed according to the naming convention
    """
    This tests validates the results for a minimal example of a CAB dotnet system check.
    """
    # If it turns out, that the xsd changes too often, it may be nice to use some validators like
    # http://pypi.python.org/pypi/XSV or http://pypi.python.org/pypi/pyxsd But they both do not seem
    # to be under maintenance at the moment.
    @classmethod
    def setUpClass(cls):
        """
        This method is invoked before all other tests. It provides the results for the tests.
        """
        cls.basedir = os.path.dirname(__file__)
        os.environ["CONFIG"] = os.path.join(cls.basedir, "config.TEST-CAB-CSHARP")
        os.environ["RESULTS_DIR"] = os.path.join(cls.basedir,"result")
        os.environ["LOCAL_SOURCE_BASE_DIR"]=os.path.join(cls.basedir,"SmallCABDotNetExample")
        process_jenkins_file = process_jenkins.__file__
        process_jenkins.runPythonSkript(["%s"%process_jenkins_file, "--rulesonly"])
        xmlFile = open(os.path.join(cls.basedir,"result/revengtools_result.xml"),"r")
        data = xmlFile.read()
        xmlFile.close()
        cls.__dom = parseString(data)
        
    # TODO delete results directory in tearDown
    
    def testSystemCabSharpValidateXMLDocType(self):
        self.assertEqual(self.__dom.documentElement.tagName, "revengtools")
        
    def testSystemCabSharpValidateXMLTopLevelStructure(self):
        self.assertEqual(self.__dom.documentElement.tagName, "revengtools")
        topLevelNodes = self.__dom.firstChild
        first_top_level_node = topLevelNodes.firstChild
        last_top_level_node = topLevelNodes.lastChild
        self.assertEqual(first_top_level_node.tagName, "ruleDescriptions")
        self.assertEqual(last_top_level_node.tagName, "results")
        self.assertEqual(first_top_level_node.nextSibling, last_top_level_node)

    def testSystemCabSharpValidateXMLRuleDescriptionHasOnlyRules(self):
        topLevelNodes = self.__dom.firstChild
        rule_description_node = topLevelNodes.firstChild
        for child in rule_description_node.childNodes:
            self.assertEqual(child.tagName, "rule")

    def testSystemCabSharpValidateXMLAllRulesAreCorrect(self):
        topLevelNodes = self.__dom.firstChild
        rule_descriptions_node = topLevelNodes.firstChild
        for child in rule_descriptions_node.childNodes:
            self.assertTrue(child.hasAttribute("id"))
            self.assertTrue(child.hasAttribute("description"))
            self.assertTrue(child.hasAttribute("severity"))
    
    def testSystemCabCSharpValidateXMLAlldiagnosticResults(self):
        topLevelNodes = self.__dom.firstChild
        results_node = topLevelNodes.lastChild
        for child in results_node.childNodes:
            self.assertEqual(child.tagName, "diagnosticResults")
            self.assertTrue(child.hasAttribute("subject"))
        
    def testSystemCabSharpRightNumberOfResults(self):
        expected_number_of_results = 30
        self.assertEqual(expected_number_of_results, len(self.__dom.getElementsByTagName("diagnosticResult")),
            "The expected number of diagnosticResults (%i) differs from the actual "
            "number of found diagnosticResults (%i). This is okay, if there were any new rules added "
            "or any changes to rules which may have influenced the number of results"%(expected_number_of_results,len(self.__dom.getElementsByTagName("diagnosticResult"))))
        
    def testExistAllResultTypes(self):
        checked_rules_list = set()
        for element in self.__dom.getElementsByTagName("diagnosticResult"):
            checked_rules_list.add(element.getAttribute("ruleID"))
        xmlRuleDescriptions = self.__dom.getElementsByTagName("ruleDescriptions")        
        for ruleDescription in xmlRuleDescriptions[0].childNodes:
            self.assertTrue(ruleDescription.getAttribute("id") in checked_rules_list,
                            "rule %s was never positive. To be a good test example the minimal example should hold at least one positive case."%ruleDescription.getAttribute("id"))
        
    def testExistAllProjectsInSolutionFilesRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "ExistAllProjectsInSolutionFilesRule"
        subject = os.path.normpath("BTC\\TimeSeries\\build\\BTC.CAB.TimeSeries.bigbuildVS2010.sln")
        message_content = "BTC.CAB.TimeSeries.Not.Existing.Module.csproj"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))  
    
    def testDefaultParameterMatchRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "DefaultParameterMatchRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\Test\\BTC.CAB.TimeSeries.API.TestDepricated.csproj")
        message_content = "BTC.CAB.TimeSeries.API.TestDepricated"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))  
    
    def testDirectoryRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "DirectoryRule"
        subject = os.path.normpath("BTC\\TimeSeries\\inconsistent.rootdir\\scr\\belowRootdir\\BTC.CAB.TimeSeries.inconsistent.rootdir.csproj")
        message_content = "BTC.CAB.TimeSeries.inconsistent.rootdir"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))  
    
    def testHasRootNamespaceNameRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "HasRootNamespaceNameRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\Test\\Support\\inconsistentRootdir\\BTC.CAB.TimeSeries.API.Test.Support.csproj")
        message_content = ""
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))  
 
    def testPrefixRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "PrefixRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\Test\\Support\\inconsistentRootdir\\BTC.CAB.TimeSeries.API.Test.Support.csproj")
        message_content = ""
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))  
 
    def testSourceFilesOutOfRepositoryRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "SourceFilesOutOfRepositoryRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\BTC.CAB.TimeSeries.API.csproj")
        message_content = "sourceFileOutOfRepository.cs"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))  
 
    def testSourceFileOutOfProjectsRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "SourceFileOutOfProjectsRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\Test\\src\\SourceFileNotInAnySolution.cs")
        message_content = "SourceFileNotInAnySolution.cs"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          

    def testRedundantModulesInSolutionFilesRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "RedundantModulesInSolutionFilesRule"
        subject = os.path.normpath("BTC\\TimeSeries\\build\\BTC.CAB.TimeSeries.smallbuildVS2010.sln")
        message_content = "BTC.CAB.TimeSeries.API.csproj"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          
                
    def testExistAllSourceFilesInProjectsRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "ExistAllSourceFilesInProjectsRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\Test\\BTC.CAB.TimeSeries.API.Test.csproj")
        message_content = "NotExistingSourceFile.cs"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          
        
    def testHasAssemblyNameRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "HasAssemblyNameRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\Test\\Support\\inconsistentRootdir\\BTC.CAB.TimeSeries.API.Test.Support.csproj")
        message_content = ""
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          
                       
    def testHierarchicalNameRule(self):                   
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "HierarchicalNameRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\Test\\Support\\inconsistentRootdir\\BTC.CAB.TimeSeries.API.Test.Support.csproj")
        message_content = ""
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          

    def testSourceFilesOutOfModuleRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "SourceFilesOutOfModuleRule"
        subject = os.path.normpath("BTC\\TimeSeries\\API\\BTC.CAB.TimeSeries.API.csproj")
        message_content = "sourceFileOutOfModule.cs"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          
            
    def testModuleOutOfSolutionRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "ModuleOutOfSolutionRule"
        subject = os.path.normpath("BTC.CAB.TimeSeries.API.Test")
        message_content = "BTC.CAB.TimeSeries.API.TestDepricated.csproj"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          
            
    def testDuplicatedModulesRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "DuplicatedModulesRule"
        subject = os.path.normpath("BTC.CAB.TimeSeries.API.Test")
        message_content = "BTC.CAB.TimeSeries.API.TestDepricated.csproj"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          
                    
    def testDirectoryHierarchyRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "DirectoryHierarchyRule"
        subject = os.path.normpath("BTC.CAB.Timeseries.API.Test.Forbidden, BTC.CAB.TimeSeries.API.Test")
        message_content = "Test.Forbidden"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))          

    def testModuleGroupNameRule(self):
        diagnostic_results = self.__dom.getElementsByTagName("diagnosticResult")
        ruleID = "ModuleGroupNameRule"
        subject = os.path.normpath("BTC.CAB.Timeseries.API.Test.Forbidden")
        message_content = "Test.Forbidden"
        self.assertTrue(self.__checkExistenceOfRuleDiagnosticResults(diagnostic_results, ruleID, subject, message_content),
                  self.__getRuleDebuggingMessage(diagnostic_results, ruleID, subject, message_content))  
                
    def __checkExistenceOfRuleDiagnosticResults(self, diagnostic_results, ruleID, subject, message_content):
        return any(diagnostic_result.getAttribute("ruleID") == ruleID and
                  os.path.normpath(diagnostic_result.parentNode.getAttribute("subject")) == subject and
                  message_content in diagnostic_result.getAttribute("message")
                  for diagnostic_result in diagnostic_results)
        
    def __getRuleDebuggingMessage(self, diagnostic_results, ruleID, subject, message_content):
        results_for_rule_id = "; ".join(("(message: "+diagnostic_result.getAttribute("message")+" and subject: "+diagnostic_result.parentNode.getAttribute("subject")+")") for diagnostic_result in diagnostic_results if diagnostic_result.getAttribute("ruleID") == ruleID)
        results_for_subject = "; ".join(("(ruleID: "+diagnostic_result.getAttribute("ruleID")+" and message: " +diagnostic_result.getAttribute("message")+")") for diagnostic_result in diagnostic_results if diagnostic_result.parentNode.getAttribute("subject") == subject)
        results_for_message_content = "; ".join(("(ruleID: "+diagnostic_result.getAttribute("ruleID")+" and subject: "+diagnostic_result.parentNode.getAttribute("subject")+")") for diagnostic_result in diagnostic_results if message_content in diagnostic_result.getAttribute("message"))
        
        return """There was no result for the rule "%s" with the subject "%s" and "%s" in the message.
                  results for the rule "%s": %s
                  results for the subject "%s": %s
                  results with "%s" in the message: %s
        """%(ruleID, subject,message_content,
             ruleID, results_for_rule_id or "None",
             subject, results_for_subject or "None",
             message_content, results_for_message_content or "None")
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()