'''
Created on 18.02.2012

@author: SIGIESEC
'''
import unittest
from cpp.cpp_util import CommentFilter, IncludePathMappingResolver
import string

class CommentFilterTest(unittest.TestCase):
    def test1(self):
        lines = ['#include <test>']
        cf = CommentFilter()
        self.assertEquals(lines, map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(0, cf.lines_with_comment())
        
    def test2(self):
        lines = ['// #include <test>']
        cf = CommentFilter()
        self.assertEquals([''], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def test3(self):
        lines = ['#include <test> // lalala']
        cf = CommentFilter()
        self.assertEquals(['#include <test>'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def test4(self):
        lines = ['//#include <test> // lalala']
        cf = CommentFilter()
        self.assertEquals([''], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def test5(self):
        lines = [' // #include <test>']
        cf = CommentFilter()
        self.assertEquals([''], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def test6(self):
        lines = ['', 'test();']
        cf = CommentFilter()
        self.assertEquals(['', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(0, cf.lines_with_comment())

    def test7(self):
        lines = ['/* ... */', 'test();']
        cf = CommentFilter()
        self.assertEquals(['', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def test8(self):
        lines = ['/* ... */ /* */', 'test();']
        cf = CommentFilter()
        self.assertEquals(['', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def test9(self):
        lines = ['#include /* ... */ <test>']
        cf = CommentFilter()
        self.assertEquals(['#include  <test>'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())
        
    def test10(self):
        lines = ['/*', '*/', '#include <test>']
        cf = CommentFilter()
        self.assertEquals(['', '', '#include <test>'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(2, cf.lines_with_comment())

    def test11(self):
        lines = ['/*', '#include <test>', '*/', 'test();']
        cf = CommentFilter()
        self.assertEquals(['', '', '', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(3, cf.lines_with_comment())

    def testIllegalNestedComment(self):
        lines = ['/*', '/* #include <test> */', '*/', 'test();']
        cf = CommentFilter()
        self.assertEquals(['', '', '*/', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(2, cf.lines_with_comment())

    def testBlockCommentStartInBlockComment(self):
        lines = ['/* /* */', '#include <test>']
        cf = CommentFilter()
        self.assertEquals(['', '#include <test>'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def testBlockCommentStartInBlockCommentMoreInLine(self):
        lines = ['/* /* */ #include <test>']
        cf = CommentFilter()
        self.assertEquals(['#include <test>'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def testBlockCommentInLineComment(self):
        lines = ['// /* /* */ #include <test>']
        cf = CommentFilter()
        self.assertEquals([''], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def testStringInBlockComment(self):
        lines = ['/* " */ test();']
        cf = CommentFilter()
        self.assertEquals(['test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    
    def testBlockCommentInString(self):
        lines = ['printf("/*");', 'test();']
        cf = CommentFilter()
        self.assertEquals(['printf("/*");', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(0, cf.lines_with_comment())

    def testBlockCommentInStringQuoted(self):
        lines = ['printf("\\"/*");', 'test();']
        cf = CommentFilter()
        self.assertEquals(['printf("\\"/*");', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(0, cf.lines_with_comment())

    def testLineCommentInBlockComment(self):
        lines = ['/*//cPD->prot("______")->prot(C_EingabeKnoten::toString(&ele))->endl();;*/', 'test();']
        cf = CommentFilter()
        self.assertEquals(['', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def testSomeBug1(self):
        lines = ["/******************************************************** WBLEIF.H ***/\n", 'test();']
        cf = CommentFilter()
        self.assertEquals(['', 'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(1, cf.lines_with_comment())
        
    def testBlockCommentInStringLineContinuation(self):
        lines = ["\"xxx\\\n", "/* no comment */\";\n"]
        cf = CommentFilter()
        self.assertEquals(["\"xxx\\", "/* no comment */\";"], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(0, cf.lines_with_comment())

    def testLineCommentInStringLineContinuation(self):
        lines = ["\"xxx\\\n", "// no comment\";\n"]
        cf = CommentFilter()
        self.assertEquals(["\"xxx\\", "// no comment\";"], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(0, cf.lines_with_comment())
        
    def testBlockCommentAfterContent(self):
        lines = ["test(); /* ...", "... */ test();\n"]
        cf = CommentFilter()
        self.assertEquals(["test();", "test();"], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(2, cf.lines_with_comment())
        
    def testUnclosedString(self):
        lines = ["\"", "/* ...", "... */ test();\n"]
        cf = CommentFilter()
        self.assertEquals(["\"", "", "test();"], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(2, cf.lines_with_comment())
        
    def testUnicode(self):
        lines = [u'/* ... */', u'test();']
        cf = CommentFilter()
        self.assertEquals([u'', u'test();'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertEquals(1, cf.lines_with_comment())

    def testDoubleEscape(self):
        lines = ['"\\\\" /* test(); */\n']
        cf = CommentFilter()
        self.assertEquals(['"\\\\"'], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(1, cf.lines_with_comment())
         
    def testQuoteCharLiteral(self):
        lines = ["if (*qexeanf == '\"') /* test(); */\n"]
        cf = CommentFilter()
        self.assertEquals(["if (*qexeanf == '\"')"], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(1, cf.lines_with_comment())

        
    def testSomeBug(self):
        lines = ["#define ORACLE_8i   /////// NUR ZUM TEST! MUSS UEBER STUDIO EINGESCHLEUST WERDEN\n", 
                 "#define OCI_BTC_ERROR                  (100000)\n"]

        cf = CommentFilter()
        self.assertEquals(["#define ORACLE_8i", "#define OCI_BTC_ERROR                  (100000)"], map(string.strip, list(cf.filter(iter(lines)))))
        self.assertFalse(cf.in_comment())
        self.assertEquals(1, cf.lines_with_comment())

class IncludePathMappingTest(unittest.TestCase):
    def test_interpret_line_internal(self):
        self.assertEquals(("/test", None), IncludePathMappingResolver().interpret_line(("/test", )))
        
    def test_interpret_line_external(self):
        self.assertEquals(("/test", "test"), IncludePathMappingResolver().interpret_line(("/test", "test")))

    def test_interpret_line_external_var(self):
        ipmr = IncludePathMappingResolver(variables=dict({"base":"/usr"}))
        self.assertEquals(("/usr/test", "test"), ipmr.interpret_line(("${base}/test", "test")))
                