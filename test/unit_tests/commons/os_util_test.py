'''
Created on 21.05.2011

@author: SIGIESEC
'''
from __future__ import with_statement
from commons.os_util import (FileResource,  
    FixedBaseDirPathResolver, 
    PathCanonicalizer)
from commons.resource_if import (ResourceMetricProcessor, ResourceAccessError, 
    IllegalResourceIdentifierError, ResourceUnresolvable)
from tempfile import NamedTemporaryFile
import os
import posixpath
import time
import unittest
import ntpath
from test.unit_tests import commons

# abstract interface test

class AbsoluteFileLengthCalculatorTest(object):
    @classmethod
    def get_mtime_minwait(cls):
        if os.name == 'nt':
            return 3
        else:
            return 0

    def setUp(self):
        self._testee = self.create_testee()
        assert isinstance(self._testee, ResourceMetricProcessor)

    def tearDown(self):
        self._testee = None

    def test_fail(self):
        f = NamedTemporaryFile(delete=False)
        f.close()
        os.unlink(f.name)
        self.assertRaises(ResourceAccessError, self._testee.apply_metric_to_resource, FileResource(f.name))

    def test_succeed_and_fail(self):
        f = NamedTemporaryFile(delete=False)
        f.close()
        self.assertEquals(0, self._testee.apply_metric_to_resource(FileResource(f.name)))
        os.unlink(f.name)
        self.assertRaises(ResourceAccessError, self._testee.apply_metric_to_resource, FileResource(f.name))
        time.sleep(self.get_mtime_minwait())
        with open(f.name, "wt") as f2:
            f2.write("\n")
            f2.close()
        self.assertEquals(1, self._testee.apply_metric_to_resource(FileResource(f.name)))
        os.unlink(f.name)

# test specializations implementation

class AbstractResourceResolverTest(object):
    def create_testee(self):
        raise NotImplementedError(self.__class__)        
    
    def case_illegal(self):
        raise NotImplementedError(self.__class__)
    
    def test_illegal(self):
        for illegal in self.case_illegal():
            self.assertRaises(IllegalResourceIdentifierError, self.create_testee().resolve, illegal)
            
    def case_unknown(self):
        raise NotImplementedError(self.__class__)
            
    def test_unknown(self):
        for unknown in self.case_unknown():
            self.assertRaises(ResourceUnresolvable, self.create_testee().resolve, unknown, True)

    def case_valid(self):
        raise NotImplementedError(self.__class__)
            
    def test_valid(self):
        for (valid, result) in self.case_valid():
            self.assertEquals(result, self.create_testee().resolve(valid, True))
            
class LocalPathResolverTest(AbstractResourceResolverTest):
    def test_valid_abs(self):
        for (valid, _result) in self.case_valid():
            self.assertTrue(os.path.isabs(self.create_testee().resolve(valid, True).name()))

class FixedBaseDirPathResolverTest(LocalPathResolverTest, unittest.TestCase):
    def __get_base_dir(self):
        return os.path.dirname(commons.__file__)
    
    def create_testee(self):
        return FixedBaseDirPathResolver(self.__get_base_dir())
    
    def case_illegal(self):
        return ["D:\\lala"]
    
    def case_unknown(self):
        return ["__foo__.xyz"]
    
    def case_valid(self):
        return [("os_util_test.py", os.path.join(self.__get_base_dir(), "os_util_test.py"))]
    
class MockOsPath(object):
    def __init__(self, existing_files, decoratee):
        self.__existing_files = existing_files
        self.__decoratee = decoratee
        
    def exists(self, name):
        return self.normpath(name) in self.__existing_files
    
    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__decoratee, attr)

#    def __setattr__(self, attr, value):
#        """ Delegate access to implementation """
#        return setattr(self.__decoratee, attr, value)

class PathCanonicalizerTest(unittest.TestCase):
    def testCanonicList0NT(self):
        self.assertEqual(['D:\\Test', 'E:\\Test'], PathCanonicalizer.default_canonic_path_list(['D:\\Test', 'E:\\Test'], path_module=ntpath))

    def testCanonicList0(self):
        self.assertEqual(['/test'], PathCanonicalizer.default_canonic_path_list(['/test'], path_module=posixpath))

    def testCanonicList1(self):
        self.assertEqual(['/test'], PathCanonicalizer.default_canonic_path_list(['/test', '/test/x'], path_module=posixpath))

    def testCanonicList2(self):
        self.assertEqual(['/test'], PathCanonicalizer.default_canonic_path_list(['/test/', '/test/x'], path_module=posixpath))

    def testCanonicList3(self):
        self.assertEqual(['/test', '/test2'], PathCanonicalizer.default_canonic_path_list(['/test/', '/test2/'], path_module=posixpath))
    
    def testSimple(self):
        canonicalizer = PathCanonicalizer(input_path_list=['/test', '/test/x'], 
                                          canonic_path_list=['/test'], 
                                          path_module=MockOsPath(existing_files=['/test/x/y'], decoratee=posixpath))
        canonical_resource = canonicalizer.canonical_resource_for_path("y")
        self.assertEqual("/test/x/y", canonical_resource.name())
        self.assertEqual("/test", canonical_resource.get_resolution_root())
        canonical_resource = canonicalizer.canonical_resource_for_path("x/y")
        self.assertEqual("/test/x/y", canonical_resource.name())
        self.assertEqual("/test", canonical_resource.get_resolution_root())
        canonical_resource = canonicalizer.canonical_resource_for_path("/test/x/y")
        self.assertEqual("/test/x/y", canonical_resource.name())
        self.assertEqual("/test", canonical_resource.get_resolution_root())
        self.assertRaises(ResourceUnresolvable, lambda: canonicalizer.canonical_resource_for_path("test/x/y"))
        self.assertRaises(ResourceUnresolvable, lambda: canonicalizer.canonical_resource_for_path("z"))
        
    def testNonUniqueFail(self):
        self.assertRaises(ValueError, lambda: PathCanonicalizer(input_path_list=['/test', '/test/x'], 
                                                                canonic_path_list=['/test', '/test/x'], 
                                                                path_module=posixpath))
        
    def testUncoveredFail(self):
        self.assertRaises(ValueError, lambda: PathCanonicalizer(input_path_list=['/test', '/test/x'], 
                                                                canonic_path_list=['/other'], 
                                                                path_module=posixpath))
        

# TODO write a test for MultipleBaseDirPathResolver !

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
