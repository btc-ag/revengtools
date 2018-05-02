#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 31.05.2012

@author: SIGIESEC
'''
import unittest
from base.diagnostics_if import CheckerRule, ModuleCheckerParameterKeys, CheckerParameterKeys
from base.diagnostics_util import (SourceFilesOutOfRepositoryRule, SourceFilesOutOfModuleRule,
                                   ParametersMatchRule, HierarchicalNameRule, ModuleSpecBelowSourceRootRule,
                                   ContainedModulesOutOfRepositoryRule, HasParameterRule, HasAssemblyNameRule,
                                   HasRootNamespaceNameRule, DefaultParameterMatchRule, ModuleOutOfSolutionRule,
                                   DuplicatedModulesRule, RedundantModulesInSolutionFilesRule, ExistAllProjectsInSolutionFilesRule,
                                   DirectoryHierarchyRule, ExistAllSourceFilesInProjectsRule, SourceFileOutOfProjectsRule,
                                   CheckerRunner, CheckerRuleFactoryDefault, PrefixRule, ModuleGroupNameRule,
    RuleUtil)
import logging

#def load_tests(loader, tests, pattern):
#   return BasicRulesTests()

class RuleTestSubject(object):
    def create_testsubject(self):
        raise NotImplementedError(self.__class__)
    
    def create_successful_testdata(self):
        raise NotImplementedError(self.__class__)

    def create_unsuccessful_testdata(self):
        raise NotImplementedError(self.__class__)

    
class ContainedModulesOutOfRepositoryRuleTestSubject(RuleTestSubject):
    def create_testsubject(self):
        return ContainedModulesOutOfRepositoryRuleTestSubject()
    
    def create_successful_testdata(self):
        raise NotImplementedError(self.__class__)

    def create_unsuccessful_testdata(self):
        raise NotImplementedError(self.__class__)

    
class BasicRulesTests(unittest.TestSuite):
    class RuleTest(unittest.TestCase):
        def __init__(self, test_subject):
            self.__test_subject = test_subject
    
        def testCreate(self):
            test_subject = self.__test_subject.create_testsubject()
            self.assertTrue(test_subject)
            self.assertTrue(isinstance(test_subject, CheckerRule))
            
        def testCheckNull(self):
            test_subject = self.__test_subject.create_testsubject()
            self.assertEquals([], len(test_subject.check(data=dict())))

    TestSubjectClasses = [ContainedModulesOutOfRepositoryRuleTestSubject]

    def __init__(self):
        unittest.TestSuite.__init__(self, tests=(BasicRulesTests.RuleTest(test_subject=x()) for x in self.TestSubjectClasses))

        
class BasicRulesTestExecutor(unittest.TestCase):
    def __call__(self, result=None, *args, **kwds):
        return self.run(result)

    def run(self, result=None):
        if not result:
            result = self.defaultTestResult()
        BasicRulesTests().run(result)
        
    def debug(self):
        BasicRulesTests().debug()

class DifferenceHighlighter(unittest.TestCase):
    
    def testIdentical(self):
        self.assertEquals(("BTC.CAB.A", "BTC.CAB.A"), RuleUtil.highlight("BTC.CAB.A", "BTC.CAB.A"))
    
    def testCompletePartDifferent(self):
        self.assertEquals(("BTC.CAB.{b}A{/b}", "BTC.CAB.{b}B{/b}"), RuleUtil.highlight("BTC.CAB.A", "BTC.CAB.B"))

    def testPartialPartDifferent(self):
        self.assertEquals(("BTC.CAB.A{b}xx{/b}", "BTC.CAB.A{b}yy{/b}"), RuleUtil.highlight("BTC.CAB.Axx", "BTC.CAB.Ayy"))

    def testPartialPartDifferentNonContinguous(self):
        # TODO this might be merged into a single difference, but this is optional
        self.assertEquals(("BTC.CAB.{b}A{/b}x{b}x{/b}", "BTC.CAB.{b}B{/b}x{b}y{/b}"), RuleUtil.highlight("BTC.CAB.Axx", "BTC.CAB.Bxy"))

    def testPartialPartRemoved(self):
        # TODO It is not really required that the second . is in the highlighted difference
        self.assertEquals(("BTC.CAB.Y", "BTC.CAB.{b}X.{/b}Y"), RuleUtil.highlight("BTC.CAB.Y", "BTC.CAB.X.Y"))
        

class HasParameterRuleTest(unittest.TestCase):
    def testCABOkaySet(self):
        rule = HasParameterRule(parameter_user_names=dict(),parameter_key=ModuleCheckerParameterKeys.IGNORED_FILES)
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.IGNORED_FILES: 'SharedAssemblyInfo.cs',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(0, len(result))

    def testCABFailureNotSet(self):
        rule = HasParameterRule(parameter_user_names=dict(),parameter_key=ModuleCheckerParameterKeys.IGNORED_FILES)
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1, len(result))
        #print ('HasParameterRuleTest:')
        #print str(result[0]) 
                
    def testCABFailureEmpty(self):
        rule = HasParameterRule(parameter_user_names=dict(),parameter_key=ModuleCheckerParameterKeys.IGNORED_FILES)
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.IGNORED_FILES: '',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1, len(result))
        
        
class HasAssemblyNameRuleTest(unittest.TestCase):
    def testCABOkaySet(self):
        rule = HasAssemblyNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'btc.timeSeries.api',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(0, len(result))

    def testCABFailureNotSet(self):
        rule = HasAssemblyNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1, len(result))
        #print ('HasAssemblyNameRuleTest:')
        #print str(result[0]) 
                
    def testCABFailureEmpty(self):
        rule = HasAssemblyNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: '',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1, len(result))
        #print ('HasAssemblyNameRuleTest:')
        #print str(result[0])         
        

class HasRootNamespaceNameRuleTest(unittest.TestCase):
    def testCABOkaySet(self):
        rule = HasRootNamespaceNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.ROOT_NAMESPACE: 'btc.timeSeries.api',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(0, len(result))
        
    def testCABFailureNotSet(self):
        rule = HasRootNamespaceNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1, len(result))
        #print ('HasRootNamespaceNameRuleTest:')
        #print str(result[0]) 
                
    def testCABFailureEmpty(self):
        rule = HasRootNamespaceNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.ROOT_NAMESPACE: '',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1, len(result))
        #print ('HasRootNamespaceNameRuleTest:')
        #print str(result[0])  
        
                
class ParametersMatchRuleTest(unittest.TestCase):
    def testCABOkayWithoutTransforms(self):
        rule = ParametersMatchRule(parameter_user_names=dict(),key_transform_pairs=())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(0, len(result))

    def testCABOkayMinimal(self):
        rule = ParametersMatchRule(parameter_user_names=dict(),key_transform_pairs=((ModuleCheckerParameterKeys.SOURCE_FILES, lambda x: x),
                                                                (ModuleCheckerParameterKeys.IGNORED_FILES, lambda x: x)))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.IGNORED_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(0,len(result))
 
    def testCABOkayOnlyOneSet(self):
        rule = ParametersMatchRule(parameter_user_names=dict(),key_transform_pairs=((ModuleCheckerParameterKeys.SOURCE_FILES, lambda x: x),
                                                                (ModuleCheckerParameterKeys.IGNORED_FILES, lambda x: x)))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(0,len(result))   
        

    #TODO: Is this the expected behavior?
    def testCABOkayCrossedParameters(self):
        rule = ParametersMatchRule(parameter_user_names=dict(),key_transform_pairs=((ModuleCheckerParameterKeys.SOURCE_FILES, lambda x: x),
                                                                (ModuleCheckerParameterKeys.IGNORED_FILES, lambda x: x)))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs', ''],
                                                   ModuleCheckerParameterKeys.IGNORED_FILES: ['','BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1,len(result))
        #print ('ParametersMatchRuleTest:')
        #print str(result[0])   
                      
    def testCABFailureEmpty(self):
        rule = ParametersMatchRule(parameter_user_names=dict(),key_transform_pairs=((ModuleCheckerParameterKeys.SOURCE_FILES, lambda x: x),
                                                                (ModuleCheckerParameterKeys.IGNORED_FILES, lambda x: x)))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.IGNORED_FILES: [''],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1,len(result))
        #print ('ParametersMatchRuleTest:')
        #print str(result[0])  

    def testCABTwoEqualOneDifferent(self):
        rule = ParametersMatchRule(parameter_user_names=dict(),key_transform_pairs=((ModuleCheckerParameterKeys.SOURCE_FILES, lambda x: x),
                                                                (ModuleCheckerParameterKeys.IGNORED_FILES, lambda x: x),
                                                                (ModuleCheckerParameterKeys.EXPLICIT_MODULE_NAME, lambda x: x)))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.IGNORED_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.EXPLICIT_MODULE_NAME: 'btc.timeSeries.api',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(2,len(result))
        #print ('ParametersMatchRuleTest:')
        #print str(result[0])
        #print str(result[1])     
            

    #TODO: More practical example        
class DefaultParameterMatchRuleTest(unittest.TestCase): 
    # TODO ".cs" is not a valid extension, but ".csproj" is... this could be checked in DefaultParameterMatchRule
    
    def testCABOkay(self):
        rule = DefaultParameterMatchRule(parameter_user_names=dict(),module_specification_file_extensions=list(['.csproj']))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API',
                                                   ModuleCheckerParameterKeys.ROOT_NAMESPACE: 'BTC.TimeSeries.API',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj'
                                                   })})})))
        self.assertEqual(0,len(result))
    

    #TODO: Is this the expected behavior?
    #      Or should there be a message that the precondition was not
    #      fulfilled?    
    def testCABOkayPerException(self):
        rule = DefaultParameterMatchRule(parameter_user_names=dict(),module_specification_file_extensions=list(['.csproj']))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API.Test',
                                                   ModuleCheckerParameterKeys.ROOT_NAMESPACE: 'BTC.TimeSeries.API.Test',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'SomeIrrelevantString',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(0,len(result))
    
    def testCABWarningPreconditionNotFullfilled(self):
        rule = DefaultParameterMatchRule(parameter_user_names=dict(),module_specification_file_extensions=list(['.csproj']))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API.Test',
                                                   ModuleCheckerParameterKeys.ROOT_NAMESPACE: 'BTC.TimeSeries.API.Test',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSerie.test.cs',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'                
                                                   })})})))
        self.assertEqual(0,len(result))
            
    def testCABFailure(self):
        rule = DefaultParameterMatchRule(parameter_user_names=dict(),module_specification_file_extensions=list(['.csproj']))
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API.Test',
                                                   ModuleCheckerParameterKeys.ROOT_NAMESPACE: 'BTC.TimeSeries.API.Test',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSerie.test.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(2,len(result))
        #print ('DefaultParametersMatchRuleTest:')
        #print str(result[0])
        #print str(result[1])  
        
                           
class HierarchicalNameRuleTest(unittest.TestCase):
    def testCABOkay(self):
        rule = HierarchicalNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.BINARY_BASENAME:'BTC.TimeSeries.API',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(0, len(result))
        
    def testCABFailure(self):
        rule = HierarchicalNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.BINARY_BASENAME:'BTC.API',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(1, len(result))
        #print ('HierachicalNameRuleTest:')
        #print str(result[0])  
        
    def testCABFailureZero(self):
        rule = HierarchicalNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.BINARY_BASENAME:'',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: '',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: ''
                                                   })})})))
        self.assertEqual(0, len(result))
        #self.assertEqual(logging.WARNING, result[0].get_level())
        #print ('HierachicalNameRuleTest:')
        #print str(result[0])       
        
        
class ModuleSpecBelowSourceRootRuleTest(unittest.TestCase):
    def testCABOkayEqualVeryGood(self):
        # this is the default setting
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/build',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: 'BTC/TimeSeries/API/src',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API'
                                                   })})})))
        self.assertEqual(0, len(result))
        
    def testCABOkayEqualAcceptable1(self):
        # this is okay for C#
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: 'BTC/TimeSeries/API/src',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(0, len(result))
        
    def testCABOkayEqualAcceptable2(self):
        # also this is okay for c#
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/build',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(0, len(result))
        
    def testCABOkayEqualAcceptable3(self):
        # also this is okay for c#
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(0, len(result))

    def testCABOkayEqual(self):
        # this is kind of okay for all
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\TimeSeries\\API',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(0, len(result))
    
    def testCABFailureBesides(self):
        # TODO das sollte fehlschlagen
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: 'BTC/TimeSeries/Root',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(1, len(result))
        self.assertEqual(logging.WARNING, result[0].get_level())
        #print result[0]

    def testCABFailureGreater(self):
        # das sollte fehlschlagen
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: 'BTC/TimeSeries',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(1, len(result))
        self.assertEqual(logging.WARNING, result[0].get_level())
         
    def testCABFailureLess(self):
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(1, len(result))
        self.assertEqual(logging.WARNING, result[0].get_level())
        
    def testCABFailureEmpty(self):
        rule = ModuleSpecBelowSourceRootRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: '',
                                                   ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: '',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: '',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(1, len(result))
        self.assertEqual(logging.WARNING, result[0].get_level())
        #print ('ModuleSpecBelowSourceRootRuleTest:')
        #print str(result[0])
        

class SourceFilesOutOfModuleRuleTest(unittest.TestCase):  
    def testCABOkay(self):
        rule = SourceFilesOutOfModuleRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj'
                                                   })})})))
        self.assertEqual(0, len(result))
    
    def testCABFailure(self):
        rule = SourceFilesOutOfModuleRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/Test',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj'
                                                   })})})))
        self.assertEqual(1, len(result))
        self.assertEqual(logging.ERROR, result[0].get_level())
        #print ('SourceFileOutOfModuleRuleTest:')
        #print str(result[0])
     
    def testCABIgnored(self):
        rule = SourceFilesOutOfModuleRule(parameter_user_names=dict(), exceptions=["SharedAssemblyInfo.cs"])
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/Test',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj'
                                                   })})})))
        self.assertEqual(0, len(result))        


class SourceFilesOutOfRepositoryRuleTest(unittest.TestCase):
    def testCABOkay(self):
        rule = SourceFilesOutOfRepositoryRule(parameter_user_names=dict())
        result = list(rule.check(
                                 dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                                dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                      ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC/TimeSeries/API'],
                                                      ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj'
                                                })})})))
        self.assertEqual(0, len(result))
        
    def testCABFailure(self):
        #print(self.__class__)
        #print(self.__call__())
        rule = SourceFilesOutOfRepositoryRule(parameter_user_names=dict())
        result = list(rule.check(
                                 dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC/TimeSeries/API/Test'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API'
                                                   })})})))
        self.assertEqual(1, len(result))
        self.assertEqual(logging.ERROR, result[0].get_level())
        #print ('SourceFileOutOfRepositoryRuleTest:')
        #print str(result[0])

    def testCABIgnored(self):
        rule = SourceFilesOutOfRepositoryRule(parameter_user_names=dict(), exceptions=["SharedAssemblyInfo.cs"])
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.SOURCE_FILES: ['BTC\\TimeSeries\\API\\Properties\\SharedAssemblyInfo.cs'],
                                                   ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC/TimeSeries/API/Test'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj'
                                                   })})})))
        self.assertEqual(0, len(result))


class ContainedModulesOutOfRepositoryRuleTest(unittest.TestCase):
    def testCABOkay(self):
        rule = ContainedModulesOutOfRepositoryRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                             dict({'BTC.TimeSeries.API':
                                                   dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/Properties',
                                                         ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC/TimeSeries/API'],
                                                         ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                         ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                         })})})))
        self.assertEqual(0, len(result))
        
    def testCABFailure(self):
        rule = ContainedModulesOutOfRepositoryRule(parameter_user_names=dict())
        result = list(rule.check(dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                       dict({'BTC.TimeSeries.API':
                                             dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/Properties',
                                                   ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC/TimeSeries/API/Test'],
                                                   ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.TimeSeries.API.csproj',
                                                   ModuleCheckerParameterKeys.BINARY_BASENAME: 'BTC.TimeSeries.API'
                                                   })})})))
        self.assertEqual(1, len(result))
        self.assertEqual(logging.ERROR, result[0].get_level())
        #print ('SourceFileOutOfRepositoryRuleTest:')
        #print str(result[0])


class ModuleOutOfSolutionRuleTest(unittest.TestCase):
    def testEmptyFailure(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'':
                    dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: '',
                          ModuleCheckerParameterKeys.BINARY_BASENAME: u'',  
                          ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: '', 
                     })}), 
                 CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({'': [''], 
            })})))
        self.assertEquals(1, len(result))
        
    def testOneModuleInNoSolutionFailure(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.TIMESERIES.API':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/',
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.TimeSeries',                                
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:"BTC.CAB.TIMESERIES.API.csproj"})}),
                 CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({})})))
        self.assertEquals(1, len(result))
        self.assertEqual(logging.WARNING, result[0].get_level())
    
    def testNoModuleInOneSolutionOkay(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER: dict(), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                     })})))
        self.assertEquals(0, len(result))    
    
    def testOneModuleInOneSolutionOkay(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.CAB.Commons.LoggingWrapper':
                          dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}), 
                     CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({'BTC\\Commons\\build\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                          'BTC\\AssemblyInfoManager\\build\\BTC.CAB.AssemblyInfoManager.VS2010.sln': ['../FileWalker/BTC.CAB.AssemblyInfoManager.FileWalker.csproj', '../FileWalker/Test/BTC.CAB.AssemblyInfoManager.FileWalker.Test.csproj', '../CommandLineInterface/BTC.CAB.AssemblyInfoManager.CLI.csproj', 
                                                                                                                            '../Commons/BTC.CAB.AssemblyInfoManager.Commons.csproj', '../Checker/BTC.CAB.AssemblyInfoManager.Checker.csproj', '../Checker/Test/BTC.CAB.AssemblyInfoManager.Checker.Test.csproj', 
                                                                                                                            '../Modifier/BTC.CAB.AssemblyInfoManager.Modifier.csproj', '../Modifier/Test/BTC.CAB.AssemblyInfoManager.Modifier.Test.csproj', '../Merge/BTC.CAB.AssemblyInfoManager.Merge.csproj', 
                                                                                                                            '../CommandLineInterface/Test/BTC.CAB.AssemblyInfoManager.CLI.Test.csproj', '../FileWriter/BTC.CAB.AssemblyInfoManager.FileWriter.csproj', '../FileReader/BTC.CAB.AssemblyInfoManager.FileReader.csproj', 
                                                                                                                            '../FileReader/Test/BTC.CAB.AssemblyInfoManager.FileReader.Test.csproj', '../FileWriter/Test/BTC.CAB.AssemblyInfoManager.FileWriter.Test.csproj']
                          })})))
        self.assertEquals(0, len(result))  
        
    def testOneModuleInOneSolutionOneFailure(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.TIMESERIES.API':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/TimeSeries/API/',
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.TimeSeries', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:"BTC.CAB.TIMESERIES.API.csproj"})}),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                     })})))
        self.assertEquals(1, len(result))
        #print result[0]
        
    def testSomeModuleInOneSolutionOkay(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoggingWrapper.csproj'}),
                      'BTC.CAB.Commons.LoginWrapper.Test':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/test',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapperTest.csproj'})
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\build\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                     })})))
        self.assertEquals(0, len(result))  
        
    def testSomeModuleInOneSolutionOneFailure(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/',
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoggingWrapper.csproj'}),
                      'BTC.CAB.Commons.LoginWrapper.Test':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoginWrapper/test',
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper.Test', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoginWrapperTest.csproj'})
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\build\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                     })})))
        self.assertEquals(1, len(result)) 
        
    def testSomeModuleInOneSolutionSomeFailure(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoginWrapper/',
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoginWrapper.csproj'}),
                      'BTC.CAB.Commons.LoginWrapper.Test':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoginWrapper/test',
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper.Test', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoginWrapperTest.csproj'})
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                     })})))
        self.assertEquals(2, len(result))         

    def testOneModuleInSomeSolutionsOkay(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoggingWrapper.csproj'})
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\build\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                    'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                     })})))
        self.assertEquals(0, len(result))  
    
    def testOneModuleInSomeSolutionsOkayRedundant(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoggingWrapper.csproj'})
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\build\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                    'BTC\\build\\BTC.CAB.Commons.VS2010.sln': ['../Commons/BTC.CAB.Commons.LoggingWrapper.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                     })})))
        self.assertEquals(0, len(result)) 
        
    def testOneModuleInSomeSolutionsFailure(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoginWrapper/',
                                ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoginWrapper.csproj'})
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                    'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                     })})))
        self.assertEquals(1, len(result)) 
        
    def testSomeModuleInSomeSolutionsAllInOneOkay(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoggingWrapper.csproj'}),
                      'BTC.CAB.Commons':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/test',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoggingWrapperTest.csproj'})
                      
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\build\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                    'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                     })})))
        self.assertEquals(0, len(result))

    def testSomeModuleInSomeSolutionsDistributedOkay(self):
        rule = ModuleOutOfSolutionRule(parameter_user_names=dict())
        result = list(rule.check(dict({
            CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                dict({'BTC.CAB.Commons.LoginWrapper':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/LoggingWrapper/',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.LoggingWrapper.csproj'}),
                      'BTC.CAB.Commons':
                          dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC/Commons/',
                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME:'BTC.CAB.Commons.csproj'})
                      
                      }),
            CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                dict({'BTC\\Commons\\build\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                    'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                     })})))
        self.assertEquals(0, len(result))   
        
class DuplicatedModulesRuleTest(unittest.TestCase):
    def testNoDuplicatedOkay(self):
        rule = DuplicatedModulesRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 'moduleSpecificationFileBasename': 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                           'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                           'BTC\\AssemblyInfoManager\\build\\BTC.CAB.AssemblyInfoManager.VS2010.sln': ['../FileWalker/BTC.CAB.AssemblyInfoManager.FileWalker.csproj', '../FileWalker/Test/BTC.CAB.AssemblyInfoManager.FileWalker.Test.csproj', '../CommandLineInterface/BTC.CAB.AssemblyInfoManager.CLI.csproj', 
                                                                                                                            '../Commons/BTC.CAB.AssemblyInfoManager.Commons.csproj', '../Checker/BTC.CAB.AssemblyInfoManager.Checker.csproj', '../Checker/Test/BTC.CAB.AssemblyInfoManager.Checker.Test.csproj', 
                                                                                                                            '../Modifier/BTC.CAB.AssemblyInfoManager.Modifier.csproj', '../Modifier/Test/BTC.CAB.AssemblyInfoManager.Modifier.Test.csproj', '../Merge/BTC.CAB.AssemblyInfoManager.Merge.csproj', 
                                                                                                                            '../CommandLineInterface/Test/BTC.CAB.AssemblyInfoManager.CLI.Test.csproj', '../FileWriter/BTC.CAB.AssemblyInfoManager.FileWriter.csproj', '../FileReader/BTC.CAB.AssemblyInfoManager.FileReader.csproj', 
                                                                                                                            '../FileReader/Test/BTC.CAB.AssemblyInfoManager.FileReader.Test.csproj', '../FileWriter/Test/BTC.CAB.AssemblyInfoManager.FileWriter.Test.csproj']
                          })})))
        self.assertEquals(0, len(result))     
        
    def testOneDuplicatedFailure(self):
        rule = DuplicatedModulesRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 'moduleSpecificationFileBasename': 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Duplicated\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Duplicated\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Duplicated\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                          'BTC\\AssemblyInfoManager\\build\\BTC.CAB.AssemblyInfoManager.VS2010.sln': ['../FileWalker/BTC.CAB.AssemblyInfoManager.FileWalker.csproj', '../FileWalker/Test/BTC.CAB.AssemblyInfoManager.FileWalker.Test.csproj', '../CommandLineInterface/BTC.CAB.AssemblyInfoManager.CLI.csproj', 
                                                                                                                            '../Commons/BTC.CAB.AssemblyInfoManager.Commons.csproj', '../Checker/BTC.CAB.AssemblyInfoManager.Checker.csproj', '../Checker/Test/BTC.CAB.AssemblyInfoManager.Checker.Test.csproj', 
                                                                                                                            '../Modifier/BTC.CAB.AssemblyInfoManager.Modifier.csproj', '../Modifier/Test/BTC.CAB.AssemblyInfoManager.Modifier.Test.csproj', '../Merge/BTC.CAB.AssemblyInfoManager.Merge.csproj', 
                                                                                                                            '../CommandLineInterface/Test/BTC.CAB.AssemblyInfoManager.CLI.Test.csproj', '../FileWriter/BTC.CAB.AssemblyInfoManager.FileWriter.csproj', '../FileReader/BTC.CAB.AssemblyInfoManager.FileReader.csproj', 
                                                                                                                            '../FileReader/Test/BTC.CAB.AssemblyInfoManager.FileReader.Test.csproj', '../FileWriter/Test/BTC.CAB.AssemblyInfoManager.FileWriter.Test.csproj']
                          })})))
        self.assertEquals(1, len(result))
        #print result[0]   
        
        
class RedundantModulesInSolutionFilesTest(unittest.TestCase):  
    def testNoRedundantOkay(self):    
        rule = RedundantModulesInSolutionFilesRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 'moduleSpecificationFileBasename': 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Duplicated\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Duplicated\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Duplicated\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                          'BTC\\AssemblyInfoManager\\build\\BTC.CAB.AssemblyInfoManager.VS2010.sln': ['../FileWalker/BTC.CAB.AssemblyInfoManager.FileWalker.csproj', '../FileWalker/Test/BTC.CAB.AssemblyInfoManager.FileWalker.Test.csproj', '../CommandLineInterface/BTC.CAB.AssemblyInfoManager.CLI.csproj', 
                                                                                                                            '../Commons/BTC.CAB.AssemblyInfoManager.Commons.csproj', '../Checker/BTC.CAB.AssemblyInfoManager.Checker.csproj', '../Checker/Test/BTC.CAB.AssemblyInfoManager.Checker.Test.csproj', 
                                                                                                                            '../Modifier/BTC.CAB.AssemblyInfoManager.Modifier.csproj', '../Modifier/Test/BTC.CAB.AssemblyInfoManager.Modifier.Test.csproj', '../Merge/BTC.CAB.AssemblyInfoManager.Merge.csproj', 
                                                                                                                            '../CommandLineInterface/Test/BTC.CAB.AssemblyInfoManager.CLI.Test.csproj', '../FileWriter/BTC.CAB.AssemblyInfoManager.FileWriter.csproj', '../FileReader/BTC.CAB.AssemblyInfoManager.FileReader.csproj', 
                                                                                                                            '../FileReader/Test/BTC.CAB.AssemblyInfoManager.FileReader.Test.csproj', '../FileWriter/Test/BTC.CAB.AssemblyInfoManager.FileWriter.Test.csproj']
                          })})))
        self.assertEquals(0, len(result)) 

    def testOneRedundantFailure(self):    
        rule = RedundantModulesInSolutionFilesRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 'moduleSpecificationFileBasename': 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Duplicated\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Duplicated\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Duplicated\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj','../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                          'BTC\\AssemblyInfoManager\\build\\BTC.CAB.AssemblyInfoManager.VS2010.sln': ['../FileWalker/BTC.CAB.AssemblyInfoManager.FileWalker.csproj', '../FileWalker/Test/BTC.CAB.AssemblyInfoManager.FileWalker.Test.csproj', '../CommandLineInterface/BTC.CAB.AssemblyInfoManager.CLI.csproj', 
                                                                                                                            '../Commons/BTC.CAB.AssemblyInfoManager.Commons.csproj', '../Checker/BTC.CAB.AssemblyInfoManager.Checker.csproj', '../Checker/Test/BTC.CAB.AssemblyInfoManager.Checker.Test.csproj', 
                                                                                                                            '../Modifier/BTC.CAB.AssemblyInfoManager.Modifier.csproj', '../Modifier/Test/BTC.CAB.AssemblyInfoManager.Modifier.Test.csproj', '../Merge/BTC.CAB.AssemblyInfoManager.Merge.csproj', 
                                                                                                                            '../CommandLineInterface/Test/BTC.CAB.AssemblyInfoManager.CLI.Test.csproj', '../FileWriter/BTC.CAB.AssemblyInfoManager.FileWriter.csproj', '../FileReader/BTC.CAB.AssemblyInfoManager.FileReader.csproj', 
                                                                                                                            '../FileReader/Test/BTC.CAB.AssemblyInfoManager.FileReader.Test.csproj', '../FileWriter/Test/BTC.CAB.AssemblyInfoManager.FileWriter.Test.csproj']
                          })})))
        self.assertEquals(1, len(result))       
        #print result[0]          
                        
                        
class ExistAllProjectsInSolutionFilesRuleTest(unittest.TestCase):
    def testAllProjectsExistOkay(self):    
        rule = ExistAllProjectsInSolutionFilesRule(module_specification_file_extensions=['.csproj'], parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC/Commons/Build/test': list(),
                          'BTC/Commons/LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({}),
                          'BTC/Commons/LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj':
                            dict({})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                    dict({'BTC/Commons/Build/BTC.CAB.Commons.LoggingWrapper.sln': ['test', '../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          })})))
        self.assertEquals(0, len(result))    

    def testNonCaseSensitiveOkay(self):  
        rule = ExistAllProjectsInSolutionFilesRule(module_specification_file_extensions=['.csproj'], parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC/Commons/Build/test': list(),
                          'BTC/Commons/loggingwrapper/BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({}),
                          'BTC/Commons/LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj':
                            dict({})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                    dict({'BTC/Commons/Build/BTC.CAB.Commons.LoggingWrapper.sln': ['test', '../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          })})))
        self.assertEquals(0, len(result)) 
        
    def testAllProjectsWithExtensionExistOkay(self):    
        rule = ExistAllProjectsInSolutionFilesRule(module_specification_file_extensions=['.csproj'], parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC/Commons/LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({}),
                          'BTC/Commons/LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj':
                            dict({})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                    dict({'BTC/Commons/Build/BTC.CAB.Commons.LoggingWrapper.sln': ['test', '../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          })})))
        self.assertEquals(0, len(result))  
        
    def testOneProjectDoesNotExitsFailure(self):
        rule = ExistAllProjectsInSolutionFilesRule(module_specification_file_extensions=['.csproj'],parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC/Commons/Build/test': list(),
                          'BTC/Commons/LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj':
                            dict({})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS: 
                    dict({'BTC/Commons/Build/BTC.CAB.Commons.LoggingWrapper.sln': ['test', '../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          })})))
        self.assertEquals(1, len(result))
        #print result[0]  
        

class DirectoryHierarchyRuleTest(unittest.TestCase):

    def testDifferentCutFalse(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(1, len(result))  
    
    def testDifferentCutOkay(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result))  

    def testDifferentCutOkay2(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result))  
            
    def testSameLengthOkay(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result))  
        
    def testDifferentLengthOkay(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result)) 
    
    def testSameLengthOkay2(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Y' :
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C.Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result)) 

    def testSameCutOkay(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C.Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result)) 
            
    def testCrossedLengthFailure(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X.A':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\X.A', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X.A'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(1, len(result))     

    def testLongerModuleNameLengthFailure(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X.A':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\X.A.B.C.X', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X.A'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(1, len(result))   

    def testIgnoringFoldersSoFarOkay(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X.A':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A.B\\C.D', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X.A'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A.B\\C.E', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result))  
        
    def testConsiderBuildDirectoryOkay(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X.A':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A.B\\C.D\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X.A'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A.B\\C.E\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result))    

    def testConsiderTestPartOfDirectoryOkay(self):
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.Test':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Test', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Test'}),
                          'BTC.A.B':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(0, len(result))  

    def testComsiderTestDirectoryFailure(self):      
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X.A':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\X.A', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X.A'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y.Test', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(1, len(result)) 

    def testComsiderTestAndBuildDirectoryFailure(self):      
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X.A':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\X.A\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X.A'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y.Test\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(1, len(result))    
                
    def testComsiderBuildDirectoryFailure(self):      
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({       
                    CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC.A.B.X.A':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B\\X.A\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.X.A'}),
                          'BTC.A.B.Y':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\B.Y\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.B.Y'}),
                          'BTC.A.C.Z':
                            dict({ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\A\\C\\Z\\build', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.A.C.Z'})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : dict()})))
        self.assertEquals(1, len(result))     
                  
    def testRealDataOkay(self):    
        rule = DirectoryHierarchyRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER :
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 'moduleSpecificationFileBasename': 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Duplicated\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Duplicated\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Duplicated\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Duplicated\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}), 
                CheckerParameterKeys.MODULES_IN_SOLUTIONS : 
                    dict({'BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln': ['../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj', '../LoggingWrapper/test/BTC.CAB.Commons.LoggingWrapperTest.csproj'], 
                          'BTC\\Commons\\build\\BTC.CAB.Commons.VS2010.sln': ['../../LoggingWrapper/BTC.CAB.Commons.LoggingWrapper.csproj','../BTC.CAB.Commons.csproj', '../Test/BTC.CAB.Commons.Test.csproj'], 
                          'BTC\\AssemblyInfoManager\\build\\BTC.CAB.AssemblyInfoManager.VS2010.sln': ['../FileWalker/BTC.CAB.AssemblyInfoManager.FileWalker.csproj', '../FileWalker/Test/BTC.CAB.AssemblyInfoManager.FileWalker.Test.csproj', '../CommandLineInterface/BTC.CAB.AssemblyInfoManager.CLI.csproj', 
                                                                                                                            '../Commons/BTC.CAB.AssemblyInfoManager.Commons.csproj', '../Checker/BTC.CAB.AssemblyInfoManager.Checker.csproj', '../Checker/Test/BTC.CAB.AssemblyInfoManager.Checker.Test.csproj', 
                                                                                                                            '../Modifier/BTC.CAB.AssemblyInfoManager.Modifier.csproj', '../Modifier/Test/BTC.CAB.AssemblyInfoManager.Modifier.Test.csproj', '../Merge/BTC.CAB.AssemblyInfoManager.Merge.csproj', 
                                                                                                                            '../CommandLineInterface/Test/BTC.CAB.AssemblyInfoManager.CLI.Test.csproj', '../FileWriter/BTC.CAB.AssemblyInfoManager.FileWriter.csproj', '../FileReader/BTC.CAB.AssemblyInfoManager.FileReader.csproj', 
                                                                                                                            '../FileReader/Test/BTC.CAB.AssemblyInfoManager.FileReader.Test.csproj', '../FileWriter/Test/BTC.CAB.AssemblyInfoManager.FileWriter.Test.csproj']
                          })})))
        self.assertEquals(0, len(result))  
        
    
class ExistAllSourceFilesTest(unittest.TestCase):
    
    def testOneOkay(self):
        rule = ExistAllSourceFilesInProjectsRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                          dict({ModuleCheckerParameterKeys.SOURCE_FILES: 'a'})}),
                CheckerParameterKeys.SOURCE_FILE_LIST:
                    dict({'a':('BTC\\a','a')})})))
        self.assertEquals(0, len(result)) 
    
    def testOneFailure(self):
        rule = ExistAllSourceFilesInProjectsRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                          dict({ModuleCheckerParameterKeys.SOURCE_FILES: 'a'})}),
                CheckerParameterKeys.SOURCE_FILE_LIST:
                    dict({'b':('BTC\\a','a')})})))
        self.assertEquals(1, len(result))  
                                          
    def testRealDataFailure(self):    
        rule = ExistAllSourceFilesInProjectsRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 'moduleSpecificationFileBasename': 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}),
                CheckerParameterKeys.SOURCE_FILE_LIST:
                    dict({'BTC\\AssemblyInfoManager\\Commons\\src\\Util\\AssemblyReader.cs': ('BTC\\AssemblyInfoManager\\Commons\\src\\Util', 'AssemblyReader.cs'), 
                          'BTC\\AssemblyInfoManager\\CommandLineInterface\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\CommandLineInterface\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub1\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub1', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Checker\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Checker\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub2\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub2', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\src\\AbstractAssemblyInfoValue.cs': ('BTC\\AssemblyInfoManager\\Modifier\\src', 'AbstractAssemblyInfoValue.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWalker\\Util\\RegexBuilder.cs': ('BTC\\AssemblyInfoManager\\FileWalker\\Util', 'RegexBuilder.cs'), 
                          'BTC\\AssemblyInfoManager\\CommandLineInterface\\Test\\src\\Util\\TestHelper.cs': ('BTC\\AssemblyInfoManager\\CommandLineInterface\\Test\\src\\Util', 'TestHelper.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\Enums.cs': ('BTC\\AssemblyInfoManager\\Commons\\src', 'Enums.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWriter\\src\\XmlFileWriter.cs': ('BTC\\AssemblyInfoManager\\FileWriter\\src', 'XmlFileWriter.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\Logger\\ConsoleLogger.cs': ('BTC\\AssemblyInfoManager\\Commons\\src\\Logger', 'ConsoleLogger.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWalker\\Test\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\FileWalker\\Test\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Commons\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\Commons\\Properties\\AssemblyInfo.cs': ('BTC\\Commons\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Checker\\Test\\src\\Tests\\ResultFactoryTest.cs': ('BTC\\AssemblyInfoManager\\Checker\\Test\\src\\Tests', 'ResultFactoryTest.cs'), 
                          'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs': ('BTC\\Commons\\LoggingWrapper\\src', 'Log4NetLogWrapper.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\src\\Tests\\Log4NetTest.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\src\\Tests', 'Log4NetTest.cs'), 
                          'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs': ('BTC\\Commons\\LoggingWrapper\\src', 'MessageBoxAppender.cs'), 
                          'BTC\\Commons\\LoggingWrapper\\test\\Properties\\AssemblyInfo.cs': ('BTC\\Commons\\LoggingWrapper\\test\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\Commons\\src\\testing\\TestHelper.cs': ('BTC\\Commons\\src\\testing', 'TestHelper.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\src\\FileTypes\\AbstractAssemblyVersionFile.cs': ('BTC\\AssemblyInfoManager\\FileReader\\src\\FileTypes', 'AbstractAssemblyVersionFile.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\src\\Reader\\XmlFileReader.cs': ('BTC\\AssemblyInfoManager\\FileReader\\src\\Reader', 'XmlFileReader.cs'), 
                          'BTC\\AssemblyInfoManager\\CommandLineInterface\\src\\CommandLineInterface.cs': ('BTC\\AssemblyInfoManager\\CommandLineInterface\\src', 'CommandLineInterface.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWriter\\Test\\src\\Tests\\XmlWriterTest.cs': ('BTC\\AssemblyInfoManager\\FileWriter\\Test\\src\\Tests', 'XmlWriterTest.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\src\\Reader\\CgxmlReader.cs': ('BTC\\AssemblyInfoManager\\FileReader\\src\\Reader', 'CgxmlReader.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\src\\CgxmlModifier.cs': ('BTC\\AssemblyInfoManager\\Modifier\\src', 'CgxmlModifier.cs'), 
                          'BTC\\Commons\\Test\\Properties\\AssemblyInfo.cs': ('BTC\\Commons\\Test\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\IBaseFileType.cs': ('BTC\\AssemblyInfoManager\\Commons\\src', 'IBaseFileType.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\etc', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\Test\\src\\Tests\\CgxmlReaderTest.cs': ('BTC\\AssemblyInfoManager\\FileReader\\Test\\src\\Tests', 'CgxmlReaderTest.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs': ('BTC\\AssemblyInfoManager\\FileWalker\\src', 'DirectoryWrapper.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\Assembly\\AssemblyVersion.cs': ('BTC\\AssemblyInfoManager\\Commons\\src\\Assembly', 'AssemblyVersion.cs')})}))) 
        self.assertEquals(7, len(result))  
        #print(result[0]) 


class SourceFileOutOfProjectsTest(unittest.TestCase):
    
    def testOneOkay(self):
        rule = SourceFileOutOfProjectsRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                          dict({ModuleCheckerParameterKeys.SOURCE_FILES: 'a'})}),
                CheckerParameterKeys.SOURCE_FILE_LIST:
                    dict({'a':('BTC\\a','a')})})))
        self.assertEquals(0, len(result))     
        
    def testOneFailure(self):
        rule = SourceFileOutOfProjectsRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                          dict({ModuleCheckerParameterKeys.SOURCE_FILES: 'a'})}),
                CheckerParameterKeys.SOURCE_FILE_LIST:
                    dict({'b':('BTC\\b','b')})})))
        self.assertEquals(1, len(result))        
        
    def testRealDataFailure(self):    
        rule = SourceFileOutOfProjectsRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 'moduleSpecificationFileBasename': 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\Commons\\LoggingWrapper', 
                                  ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper', 
                                  ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.Commons.LoggingWrapper.csproj', 
                                  ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\Commons\\LoggingWrapper\\Properties\\AssemblyInfo.cs', u'BTC\\Commons\\LoggingWrapper\\src\\ILog.cs', u'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs', u'BTC\\Commons\\LoggingWrapper\\src\\LogManager.cs', u'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs'], 
                                  ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']})}),
                CheckerParameterKeys.SOURCE_FILE_LIST:
                    dict({'BTC\\AssemblyInfoManager\\Commons\\src\\Util\\AssemblyReader.cs': ('BTC\\AssemblyInfoManager\\Commons\\src\\Util', 'AssemblyReader.cs'), 
                          'BTC\\AssemblyInfoManager\\CommandLineInterface\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\CommandLineInterface\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub1\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub1', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Checker\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Checker\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub2\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\sub2', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\src\\AbstractAssemblyInfoValue.cs': ('BTC\\AssemblyInfoManager\\Modifier\\src', 'AbstractAssemblyInfoValue.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWalker\\Util\\RegexBuilder.cs': ('BTC\\AssemblyInfoManager\\FileWalker\\Util', 'RegexBuilder.cs'), 
                          'BTC\\AssemblyInfoManager\\CommandLineInterface\\Test\\src\\Util\\TestHelper.cs': ('BTC\\AssemblyInfoManager\\CommandLineInterface\\Test\\src\\Util', 'TestHelper.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\Enums.cs': ('BTC\\AssemblyInfoManager\\Commons\\src', 'Enums.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWriter\\src\\XmlFileWriter.cs': ('BTC\\AssemblyInfoManager\\FileWriter\\src', 'XmlFileWriter.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\Logger\\ConsoleLogger.cs': ('BTC\\AssemblyInfoManager\\Commons\\src\\Logger', 'ConsoleLogger.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWalker\\Test\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\FileWalker\\Test\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\Properties\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Commons\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\Commons\\Properties\\AssemblyInfo.cs': ('BTC\\Commons\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Checker\\Test\\src\\Tests\\ResultFactoryTest.cs': ('BTC\\AssemblyInfoManager\\Checker\\Test\\src\\Tests', 'ResultFactoryTest.cs'), 
                          'BTC\\Commons\\LoggingWrapper\\src\\Log4NetLogWrapper.cs': ('BTC\\Commons\\LoggingWrapper\\src', 'Log4NetLogWrapper.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\src\\Tests\\Log4NetTest.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\src\\Tests', 'Log4NetTest.cs'), 
                          'BTC\\Commons\\LoggingWrapper\\src\\MessageBoxAppender.cs': ('BTC\\Commons\\LoggingWrapper\\src', 'MessageBoxAppender.cs'), 
                          'BTC\\Commons\\LoggingWrapper\\test\\Properties\\AssemblyInfo.cs': ('BTC\\Commons\\LoggingWrapper\\test\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\Commons\\src\\testing\\TestHelper.cs': ('BTC\\Commons\\src\\testing', 'TestHelper.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\src\\FileTypes\\AbstractAssemblyVersionFile.cs': ('BTC\\AssemblyInfoManager\\FileReader\\src\\FileTypes', 'AbstractAssemblyVersionFile.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\src\\Reader\\XmlFileReader.cs': ('BTC\\AssemblyInfoManager\\FileReader\\src\\Reader', 'XmlFileReader.cs'), 
                          'BTC\\AssemblyInfoManager\\CommandLineInterface\\src\\CommandLineInterface.cs': ('BTC\\AssemblyInfoManager\\CommandLineInterface\\src', 'CommandLineInterface.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWriter\\Test\\src\\Tests\\XmlWriterTest.cs': ('BTC\\AssemblyInfoManager\\FileWriter\\Test\\src\\Tests', 'XmlWriterTest.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\src\\Reader\\CgxmlReader.cs': ('BTC\\AssemblyInfoManager\\FileReader\\src\\Reader', 'CgxmlReader.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\src\\CgxmlModifier.cs': ('BTC\\AssemblyInfoManager\\Modifier\\src', 'CgxmlModifier.cs'), 
                          'BTC\\Commons\\Test\\Properties\\AssemblyInfo.cs': ('BTC\\Commons\\Test\\Properties', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\IBaseFileType.cs': ('BTC\\AssemblyInfoManager\\Commons\\src', 'IBaseFileType.cs'), 
                          'BTC\\AssemblyInfoManager\\Modifier\\Test\\etc\\AssemblyInfo.cs': ('BTC\\AssemblyInfoManager\\Modifier\\Test\\etc', 'AssemblyInfo.cs'), 
                          'BTC\\AssemblyInfoManager\\FileReader\\Test\\src\\Tests\\CgxmlReaderTest.cs': ('BTC\\AssemblyInfoManager\\FileReader\\Test\\src\\Tests', 'CgxmlReaderTest.cs'), 
                          'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs': ('BTC\\AssemblyInfoManager\\FileWalker\\src', 'DirectoryWrapper.cs'), 
                          'BTC\\AssemblyInfoManager\\Commons\\src\\Assembly\\AssemblyVersion.cs': ('BTC\\AssemblyInfoManager\\Commons\\src\\Assembly', 'AssemblyVersion.cs')})}))) 
        self.assertEquals(30, len(result))  
        #print result[0]
                     
class ModuleGroupNameRuleTest(unittest.TestCase):

    def testOneModuleOkay(self): 
        rule = ModuleGroupNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker'})
                            })}))) 
        self.assertEquals(0, len(result))  
             
    def testTwoModulesOkay(self):    
        rule = ModuleGroupNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker'}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper'})})}))) 
        self.assertEquals(0, len(result))  
    
    def testTwoModulesFailure(self):    
        rule = ModuleGroupNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\A.B':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'A.B'}),
                          'BTC\a.C':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME: u'a.C'})})}))) 
        self.assertEquals(1, len(result))  
        
    def testTwoModulesDeepthThreeFailure(self):
        rule = ModuleGroupNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.CommOns.FileWalker'}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper'})})}))) 
        self.assertEquals(1, len(result))    

    def testTwoModulesDeepthSevenFailure(self):
        rule = ModuleGroupNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.Commons.FileWalker.API.Integrationtest.CaB.TestOne'}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.FileWalker.API.Integrationtest.CAB.TestTwo'})})}))) 
        self.assertEquals(1, len(result))  
        
    def testThreeModulesFailuresOnDifferentLevels(self):
        rule = ModuleGroupNameRule(parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.Commons.FileWalker.API.Integrationtest.CaB.TestOne'}),
                          'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.TestThree.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.CommOns.FileWalker.API.Integrationtest.CaB.TestThree'}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.FileWalker.API.Integrationtest.CAB.TestTwo'})})}))) 
        print result[0]
        self.assertEquals(2, len(result))          

    def testCABSpecificOkay(self):    
        rule = ModuleGroupNameRule(start_element=3, parameter_user_names=dict())
        result = list(rule.check(dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.Cab.AssemblyInfoManager.FileWalker'}),
                          'BTC\Commons\LoggingWrapper\BTC.CAB.Commons.LoggingWrapper.csproj':
                            dict({ModuleCheckerParameterKeys.BINARY_BASENAME: u'BTC.CAB.Commons.LoggingWrapper'})})}))) 
        self.assertEquals(0, len(result))  
                                                 
class ModuleCheckerRunnerCheckerRuleFactoryDefaultITest(unittest.TestCase):
    def testLocalRulesOkay(self):
        results = CheckerRunner(CheckerRuleFactoryDefault(dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE:"root namespace"}),[".csproj",]).rules()).check(
                                dict({CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                                    dict({'BTC.TimeSeries.API':
                                          dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE: u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: 'BTC\\AssemblyInfoManager\\FileWalker', 
                                                ModuleCheckerParameterKeys.BINARY_BASENAME:  u'BTC.CAB.AssemblyInfoManager.FileWalker', 
                                                ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: 'BTC.CAB.AssemblyInfoManager.FileWalker.csproj', 
                                                ModuleCheckerParameterKeys.SOURCE_FILES: [u'BTC\\AssemblyInfoManager\\FileWalker\\src\\DirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\FileFinder.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Properties\\AssemblyInfo.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\src\\IDirectoryWrapper.cs', u'BTC\\AssemblyInfoManager\\FileWalker\\Util\\SearchUtil.cs'], 
                                                ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: ['BTC']
                                                })})}))
        result = list(results)
        #for res in result:
        #    print res
        self.assertEquals(0, len(list(result))) 
               
    def testsourceRulesFailure(self):
        results = CheckerRunner(CheckerRuleFactoryDefault(dict({ModuleCheckerParameterKeys.ROOT_NAMESPACE:"root namespace"}),[".csproj",]).source_file_rules()).check(
                   dict({
                CheckerParameterKeys.MODULE_CHECKER_PARAMETER:
                    dict({'BTC\AssemblyInfoManager\FileWalker\BTC.CAB.AssemblyInfoManager.FileWalker.csproj':
                          dict({ModuleCheckerParameterKeys.SOURCE_FILES: 'a'})}),
                CheckerParameterKeys.SOURCE_FILE_LIST:
                    dict({'a':('BTC\\a','a')})}))
        result = list(results)
        #for res in result:
        #    print res
        self.assertEquals(0, len(list(result)))

class CheckerRuleFactoryDefaultTest(unittest.TestCase):
    """
    Attention! On Jenkins there are no assertIn and assertNotIn avaiable,
    so it has to be modeled with assertTrue(member in container) or
    assertFalse(member in container).
    """                                     
    def testExchangeRuleOneForAnotherOkay(self):
        rule = HasAssemblyNameRule(parameter_user_names=[])
        rules = [rule]
        self.assertTrue(rule in rules)
        self.assertTrue(rule in rules)
        exchange_rule = HasAssemblyNameRule(parameter_user_names=[("test","test")]) 
        rules = list(CheckerRuleFactoryDefault.exchange_rule(rules, exchange_rule))   
        self.assertFalse(rule in rules)
        self.assertTrue(exchange_rule in rules)

    def testExchangeRuleOneForAnotherFailure(self):
        rule = HasAssemblyNameRule(parameter_user_names=[])
        rules = [rule]
        self.assertTrue(rule in rules)
        exchange_rule = HasRootNamespaceNameRule(parameter_user_names=[("test","test")]) 
        rules = list(CheckerRuleFactoryDefault.exchange_rule(rules, exchange_rule))   
        self.assertTrue(rule in rules)
        #TODO: BTCEPMARCH-877
        #self.assertFalse(exchange_rule in rules)
        
    def testExchangeRuleOneOfTwoOkay(self):
        ruleToExchange = HasAssemblyNameRule(parameter_user_names=[])
        another_rule = HasRootNamespaceNameRule(parameter_user_names=[("test","test")])
        rules = [ruleToExchange, another_rule]
        self.assertTrue(ruleToExchange in rules)
        self.assertTrue(another_rule in rules)        
        exchange_rule = HasAssemblyNameRule(parameter_user_names=[("test","test")]) 
        rules = list(CheckerRuleFactoryDefault.exchange_rule(rules, exchange_rule))   
        self.assertTrue(another_rule in rules)
        self.assertTrue(exchange_rule in rules)
        self.assertFalse(ruleToExchange in rules)

    def testExchangeRuleOneOfTwoFailure(self):
        one_rule = HasParameterRule(parameter_key="nothing", parameter_user_names=[])
        another_rule = HasRootNamespaceNameRule(parameter_user_names=[("test","test")])
        rules = [one_rule, another_rule]
        self.assertTrue(one_rule in rules)
        self.assertTrue(another_rule in rules)        
        exchange_rule = HasAssemblyNameRule(parameter_user_names=[("test","test")]) 
        rules = list(CheckerRuleFactoryDefault.exchange_rule(rules, exchange_rule))   
        self.assertTrue(another_rule in rules)
        #TODO: BTCEPMARCH-877
        #self.assertFalse(exchange_rule in rules)
        self.assertTrue(one_rule in rules)
                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
