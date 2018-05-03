'''
Created on 28.12.2011

@author: SIGIESEC
'''
from cpp.incl_deps.include_list_generator import (NullHeaderCanonicalSorter, 
    StandardGroupCanonicalSorter, IncludeListGeneratorInternal, NullHeaderPathMapper, 
    IncludeListGeneratorConfig, IncludeGuardNormalizer, NullHeaderExceptionMapper)
from cpp.incl_deps.include_rule_checker_if import NullIncludeRuleChecker
from itertools import chain
import unittest


class HeaderCanonicalSorterTestBase(object):
    """
    Contains basic tests that every implementation of HeaderCanonicalSorter must adhere to. 
    """

    def assertPostcondition(self, inputs):
        input_list = list(inputs)
        # test postcondition 1
        self.assertEquals(sorted(set(input_list)), 
                          sorted(set(chain.from_iterable(self.get_testee().canonical_groups(input_list)))))
        # test postcondition 2
        self.assertEquals(0, 
                          len(filter(lambda group: len(group)==0, self.get_testee().canonical_groups(input_list))))
        
    def get_testee(self):
        raise NotImplementedError(self.__class__)
    
    def assertEquals(self, first, second, msg=''):
        raise NotImplementedError(self.__class__)
    
    def testPostconditionInternal(self):
        self.assertPostcondition(("a.h", ))
        
    def testPostconditionExternal(self):
        self.assertPostcondition(("<string>", ))
        
    def testPostconditionMixed1(self):
        self.assertPostcondition(("a.h", "<string>"))
        
    def testPostconditionMixed2(self):
        self.assertPostcondition(("a.h", "<string>", "a.h", "b.h"))
        
    def testPostconditionMixed3(self):
        self.assertPostcondition(("x,y,z", "a.h", "a.b.c", "<string>", "x,y,z", "a.h", "b.h"))

    def testPostconditionNone(self):
        self.assertPostcondition(())

    def testNone(self):
        self.assertEquals((), self.get_testee().canonical_groups(()))

        
class NullHeaderCanonicalSorterTest(unittest.TestCase, HeaderCanonicalSorterTestBase):        
    def setUp(self):
        self.__testee = NullHeaderCanonicalSorter()

    def get_testee(self):
        return self.__testee
    
    def testInternal(self):
        self.assertEquals((("a.h", ), ), self.__testee.canonical_groups(("a.h", )))
        
    def testExternal(self):
        self.assertEquals((("<string>", ), ), self.__testee.canonical_groups(("<string>", )))
        
    def testMixed_basic(self):
        self.assertEquals((("<string>", "a.h", ), ), self.__testee.canonical_groups(("a.h", "<string>", )))

    def testMixed_duplicated(self):
        self.assertEquals((("<string>", "a.h", "b.h", ), ), self.__testee.canonical_groups(("a.h", "<string>", "a.h", "b.h")))
    
    
class StandardGroupCanonicalSorterTest(unittest.TestCase, HeaderCanonicalSorterTestBase):        
    def setUp(self):
        self.__testee = StandardGroupCanonicalSorter()

    def get_testee(self):
        return self.__testee

    def testEmpty(self):
        self.assertEquals((), self.__testee.canonical_groups(( )))

    def testInternal(self):
        self.assertEquals((("a.h", ), ), self.__testee.canonical_groups(("a.h", )))
        
    def testExternal(self):
        self.assertEquals((("<string>", ), ), self.__testee.canonical_groups(("<string>", )))
        
    def testMixed1(self):
        self.assertEquals((("a.h", ), ("<string>", ), ), self.__testee.canonical_groups(("a.h", "<string>", )))
        
    def testMixed2(self):
        self.assertEquals((("a.h", "b.h", ), ("<string>", ), ), self.__testee.canonical_groups(("a.h", "<string>", "a.h", "b.h")))


    
    #TODO: Why is there the empty string in the list of include directives?
class IncludeListGeneratorInternalTest(unittest.TestCase):
    def test1(self):
        self.__testee = IncludeListGeneratorInternal(include_guard_normalizer=IncludeGuardNormalizer(use_pragma_once=True), 
                                                     config=IncludeListGeneratorConfig(use_redundant_include_guards=False, 
                                                                                       include_paths_rel_to_root=True, 
                                                                                       use_pragma_once=True), 
                                                     include_rule_checker=NullIncludeRuleChecker(), 
                                                     header_exception_mapper=NullHeaderExceptionMapper(), 
                                                     header_path_mapper=NullHeaderPathMapper(), 
                                                     header_canonical_sorter=StandardGroupCanonicalSorter(), 
                                                     include_generation_timestamp=False)
        self.assertEquals(['// *** list of 3 include directives (1369018009)', '#include "a/ax.h"', '#include "b/b.h"', '', '#include <string>', '// *** end of generated include list', ''], 
                          self.__testee.generate_include_directives("a/a.h", ["a/ax.h", "b/b.h", "<string>",])) 
    def test_duplicated_include(self):
        self.__testee = IncludeListGeneratorInternal(include_guard_normalizer=IncludeGuardNormalizer(use_pragma_once=True), 
                                                     config=IncludeListGeneratorConfig(use_redundant_include_guards=False, 
                                                                                       include_paths_rel_to_root=True, 
                                                                                       use_pragma_once=True), 
                                                     include_rule_checker=NullIncludeRuleChecker(), 
                                                     header_exception_mapper=NullHeaderExceptionMapper(), 
                                                     header_path_mapper=NullHeaderPathMapper(), 
                                                     header_canonical_sorter=StandardGroupCanonicalSorter(), 
                                                     include_generation_timestamp=False)
        self.assertEquals(['// *** list of 3 include directives (1369018009)', '#include "a/ax.h"', '#include "b/b.h"', '', '#include <string>', '// *** end of generated include list', ''], 
                          self.__testee.generate_include_directives("a/a.h", ["a/ax.h", "a/ax.h", "b/b.h", "<string>",])) 
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testPostcondition']
    unittest.main()
