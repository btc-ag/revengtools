'''
Created on 30.05.2011

@author: SIGIESEC
'''
from commons.config_xml import XMLAutoWireConfigParser
from test.unit_tests.test_helper import TestDirectoryHelper
from test.unit_tests.commons.config_util_test import TestHelper
import unittest


class XMLAutoWireConfigParserTest(unittest.TestCase):

    def test_parse_lines_with_arg(self):
        parser = XMLAutoWireConfigParser()
        testfile = TestHelper.get_base_resolver().resolve("%s/commons/testdata/autowire.xml"%(TestDirectoryHelper.getTestmoduleDirectory())).open()
        result = list(parser.parse_lines(testfile))
        self.assertEquals((), tuple(parser.get_errors()))
        self.assertEquals([((u"%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), u"AbstractAutoConfigurable"), ((u"%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), u"ConcreteAutoConfigurableWithArgs"), dict({u"testarg": dict({"type": u"int", "value": u"12"})})))], 
                          result)

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()