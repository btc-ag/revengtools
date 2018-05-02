'''
Created on 20.12.2011

@author: SIGIESEC
'''
from base.project_default import DefaultProjectFile
from cpp.incl_deps.file_transform_if import ManualProcessingException
from cpp.incl_deps.include_list_generator_wrap import IncludeListGenerator
from cpp.incl_deps.repair_includes_base import (DefaultSymbolScanner, 
    TwoPhaseRequiredIncludeFilesCalculator, BaseFileNormalizer)
from itertools import imap, ifilter
from mock import patch, Mock
import cpp.incl_deps.repair_includes_if
import logging
import os
import unittest

class TwoPhaseRequiredIncludeFilesCalculatorTest(unittest.TestCase):
    @patch('cpp.incl_deps.repair_includes_if.UsedSymbolsLister')
    @patch('cpp.incl_deps.repair_includes_if.HeaderLister')
    def testNoSymbols(self, UsedSymbolsListerMock, HeaderListerMock):
        used_symbols_lister = cpp.incl_deps.repair_includes_if.UsedSymbolsLister()
        used_symbols_lister.get_symbol_candidates.return_value = dict()
        header_lister = cpp.incl_deps.repair_includes_if.HeaderLister()
        header_lister.map_symbol_ids_to_headers.return_value = set()
        is_implementation_file_func = lambda x: True
        resource_resolver = None
        testee = TwoPhaseRequiredIncludeFilesCalculator(used_symbols_lister, header_lister, is_implementation_file_func, resource_resolver)
        local_root = os.path.dirname(os.tempnam())
        test_file = DefaultProjectFile(path_rel_to_root_unix="a.cpp", local_repository_root=local_root, resource=None)
        self.assertEquals(set(), set(testee.calculate_required_include_files(test_file)))
        self.assertTrue(used_symbols_lister.get_symbol_candidates.called)
        self.assertEquals([(([], test_file),)], header_lister.map_symbol_ids_to_headers.call_args_list)

    @patch('cpp.incl_deps.repair_includes_if.UsedSymbolsLister')
    @patch('cpp.incl_deps.repair_includes_if.HeaderLister')
    def testOneSymbol(self, UsedSymbolsListerMock, HeaderListerMock):
        used_symbols_lister = cpp.incl_deps.repair_includes_if.UsedSymbolsLister()
        used_symbols_lister.get_symbol_candidates.return_value = dict({'test_id': 'test'}) 
        header_lister = cpp.incl_deps.repair_includes_if.HeaderLister()
        header_lister.map_symbol_ids_to_headers.return_value = set(('test.h', ))
        is_implementation_file_func = lambda x: True
        resource_resolver = None
        testee = TwoPhaseRequiredIncludeFilesCalculator(used_symbols_lister, header_lister, is_implementation_file_func, resource_resolver)
        local_root = os.path.dirname(os.tempnam())
        test_file = DefaultProjectFile(path_rel_to_root_unix="a.cpp", local_repository_root=local_root, resource=None)
        self.assertEquals(set(('test.h', )), set(testee.calculate_required_include_files(test_file)))
        self.assertTrue(used_symbols_lister.get_symbol_candidates.called)
        self.assertEquals([((['test_id'], test_file),)], header_lister.map_symbol_ids_to_headers.call_args_list)

class DefaultSymbolScannerTest(unittest.TestCase):
    TEST_PROGRAM_1 = """
void my_foo(int i) {
   foo(i * 2);
}
"""

    TEST_PROGRAM_2 = """
class Foo;

class Bar {
public:
    virtual Foo *GetFoo() = 0;
};
"""
    
    def setUp(self):
        self.__testee = DefaultSymbolScanner()
        
    def tearDown(self):
        self.__testee = None

    def testNoLines1(self):
        self.assertEquals(0, len(self.__testee.scan_for_symbols([], dict())))

    def testNoLines2(self):
        self.assertEquals(0, len(self.__testee.scan_for_symbols([], ["foo", "bar"])))
        
    def testNoSymbols1(self):
        self.assertEquals(0, len(self.__testee.scan_for_symbols(self.TEST_PROGRAM_1.splitlines(), dict())))

    def testSymbols(self):
        self.assertEquals(set("1"), self.__testee.scan_for_symbols(self.TEST_PROGRAM_1.splitlines(), dict({"1": "foo", "2": "bar"})))

    def testSymbolsForwardDeclaration(self):
        self.assertEquals(set("2"), self.__testee.scan_for_symbols(self.TEST_PROGRAM_2.splitlines(), dict({"1": "Foo", "2": "Bar"})))

class MemoryFile(object):
    def __init__(self):
        self.__lines = list()
    
    def write(self, line):
        self.__lines.append(line)
        
    def lines(self):
        return iter(self.__lines)
    
    def text(self):
        return "\n".join(self.__lines)

class BaseFileNormalizerTest(unittest.TestCase):
    TEST_IMPL_FILE_1 = """
#include "foo.h"
    
void my_foo(int i) {
   foo(i * 2);
}
"""
    TEST_IMPL_FILE_1_RESULT = """
//GENERATED_LIST
    
void my_foo(int i) {
   foo(i * 2);
}
"""

    TEST_IMPL_FILE_2 = """
#include "foo.h"
"""
    TEST_IMPL_FILE_2_RESULT = """
//GENERATED_LIST
"""

    TEST_IMPL_FILE_3 = """
//MANUAL_INCLUDES
#include "foo.h"    
"""

    TEST_HEADER_FILE_1 = """
#include "foo.h"
    
void my_foo(int i);
"""
    TEST_HEADER_FILE_1_RESULT = """
#ifndef BAR_H
#define BAR_H
    
//GENERATED_LIST
    
void my_foo(int i);

#endif // END of #ifndef BAR_H
"""
    TEST_HEADER_FILE_1_RESULT_PRAGMA_ONCE = """
#pragma once    
    
//GENERATED_LIST
    
void my_foo(int i);
"""

    TEST_HEADER_FILE_2 = """
#include "foo.h"
"""
    TEST_HEADER_FILE_2_RESULT = """
#ifndef BAR_H
#define BAR_H
//GENERATED_LIST
#endif // END of #ifndef BAR_H
"""
    TEST_HEADER_FILE_2_RESULT_PRAGMA_ONCE = """
#pragma once    
//GENERATED_LIST
"""

    TEST_HEADER_FILE_3 = """
//MANUAL_INCLUDES
#include "foo.h"    
"""

    TEST_HEADER_FILE_4 = """
#ifndef BAR_H
#define BAR_H
#include "foo.h"
#endif // END of #ifndef BAR_H
"""
    TEST_HEADER_FILE_4_RESULT = """
#ifndef BAR_H
#define BAR_H
//GENERATED_LIST
#endif // END of #ifndef BAR_H
"""


    PLACEHOLDER = "//GENERATED_LIST"

    # TODO rename and move transform
    @staticmethod
    def transform(lines):
        return list(ifilter(len, imap(lambda line: line.strip(), lines)))
    
    def testTransform(self):
        self.assertEquals([], self.transform(["   ", ""]))
        self.assertEquals(["a"], self.transform(["   ", "   a", ""]))
    
    def make_mock(self, include_guard_normalizer, config):
        mock = Mock(spec_set=IncludeListGenerator)
        mock.generate_include_directives.return_value = [self.PLACEHOLDER]
        return mock

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.__testee = BaseFileNormalizer(is_implementation_file_func=lambda name: name.endswith(".cpp"),
                                           include_list_generator_factory=self.make_mock,
                                           use_pragma_once=False)
        
    def assertEqualsModWhitespace(self, first, second):
        first_list = list(first)
        second_list = list(second)
        self.assertEquals(self.transform(first_list), self.transform(second_list))
    
    def testNonEmpty(self):
        result = MemoryFile()
        self.__testee.process("bar.cpp", [], self.TEST_IMPL_FILE_1.splitlines(), result)
        self.assertEqualsModWhitespace(self.TEST_IMPL_FILE_1_RESULT.splitlines(), result.lines())

    def testEmpty(self):
        result = MemoryFile()
        self.__testee.process("bar.cpp", [], self.TEST_IMPL_FILE_2.splitlines(), result)
        self.assertEqualsModWhitespace(self.TEST_IMPL_FILE_2_RESULT.splitlines(), result.lines())

    def testManual(self):
        result = MemoryFile()
        self.assertRaises(ManualProcessingException, lambda: self.__testee.process("bar.cpp", [], self.TEST_IMPL_FILE_3.splitlines(), result))

    def testHeaderNonEmpty(self):
        result = MemoryFile()
        self.__testee.process("bar.h", [], self.TEST_HEADER_FILE_1.splitlines(), result)
        self.assertEqualsModWhitespace(self.TEST_HEADER_FILE_1_RESULT.splitlines(), result.lines())

    def testHeaderEmpty(self):
        result = MemoryFile()
        self.__testee.process("bar.h", [], self.TEST_HEADER_FILE_2.splitlines(), result)
        self.assertEqualsModWhitespace(self.TEST_HEADER_FILE_2_RESULT.splitlines(), result.lines())

    def testHeaderEmptyWithIncludeGuards(self):
        result = MemoryFile()
        self.__testee.process("bar.h", [], self.TEST_HEADER_FILE_4.splitlines(), result)
        self.assertEqualsModWhitespace(self.TEST_HEADER_FILE_4_RESULT.splitlines(), result.lines())

    def testHeaderNonEmptyPragmaOnce(self):
        self.__testee = BaseFileNormalizer(is_implementation_file_func=lambda name: name.endswith(".cpp"),
                                           include_list_generator_factory=self.make_mock,
                                           use_pragma_once=True)
        result = MemoryFile()
        self.__testee.process("bar.h", [], self.TEST_HEADER_FILE_1.splitlines(), result)
        self.assertEqualsModWhitespace(self.TEST_HEADER_FILE_1_RESULT_PRAGMA_ONCE.splitlines(), result.lines())

    def testHeaderEmptyPragmaOnce(self):
        self.__testee = BaseFileNormalizer(is_implementation_file_func=lambda name: name.endswith(".cpp"),
                                           include_list_generator_factory=self.make_mock,
                                           use_pragma_once=True)
        result = MemoryFile()
        self.__testee.process("bar.h", [], self.TEST_HEADER_FILE_2.splitlines(), result)
        self.assertEqualsModWhitespace(self.TEST_HEADER_FILE_2_RESULT_PRAGMA_ONCE.splitlines(), result.lines())

    def testHeaderManual(self):
        result = MemoryFile()
        self.assertRaises(ManualProcessingException, lambda: self.__testee.process("bar.h", [], self.TEST_HEADER_FILE_3.splitlines(), result))
            

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']    
    unittest.main()
