'''
Created on 18.02.2012

@author: SIGIESEC
'''
from base.project_default import DefaultProjectFile
from cpp.incl_deps.include_resolver_util import (
    DefaultIncludePathCanonicalizerFactory, IncludeDirectiveNormalizer, 
    FuzzyResolverInternal)
from test.unit_tests.commons.os_util_test import MockOsPath
import posixpath
import unittest


#TODO: Just checks whether there is an #include or not? commentaries are irrelevant?
class IncludeDirectiveNormalizerTest(unittest.TestCase):
    def test_has_line_include_directive_basic(self):
        self.assertTrue(IncludeDirectiveNormalizer.has_line_include_directive('#include "..\inc\oratypes.h8i"'))

    def test_has_line_include_directive_with_ws(self):
        self.assertTrue(IncludeDirectiveNormalizer.has_line_include_directive('# include "..\inc\oratypes.h8i"'))
  
    def test_has_line_include_directive_with_some_ws(self):
        self.assertTrue(IncludeDirectiveNormalizer.has_line_include_directive('#     include "..\inc\oratypes.h8i"'))
          
    def test_has_line_include_directive_bug(self):
        self.assertTrue(IncludeDirectiveNormalizer.has_line_include_directive('  #include "..\inc\oci.h8i"\n'))

    def test_has_line_include_directive_commentary(self):
        self.assertTrue(IncludeDirectiveNormalizer.has_line_include_directive('//#include "..\inc\oci.h8i"\n'))
        
    def test_has_line_include_directive_commentary2(self):
        self.assertTrue(IncludeDirectiveNormalizer.has_line_include_directive('/*#include "..\inc\oci.h8i"\n*/'))
        
    def test_has_line_include_directive_empty(self):
        self.assertFalse(IncludeDirectiveNormalizer.has_line_include_directive(''))

    def test_has_line_include_directive_other_directive(self):
        self.assertFalse(IncludeDirectiveNormalizer.has_line_include_directive('#noinclude'))
        
    def test_has_line_include_directive_other_directive2(self):
        self.assertFalse(IncludeDirectiveNormalizer.has_line_include_directive('#noinclud e'))
    
    def __create_include_path_canonicalizer_factory(self):
        return DefaultIncludePathCanonicalizerFactory(global_internal_include_paths=['/test'], 
                                                      global_external_include_paths=['/std-include'], 
                                                      quoted_internal_include_paths=True, 
                                                      path_module=MockOsPath(['/std-include/string', '/test/x.h'], decoratee=posixpath))

    def test1(self):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix="a/b.cpp",
                                                                   local_repository_root="/test",
                                                                   path_module=posixpath), include_canonicalizer_factory=self.__create_include_path_canonicalizer_factory())
        test_str = "void foo();"
        self.assertEquals(test_str, normalizer.normalize(test_str))
        
    def test2(self):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix="a/b.cpp",
                                                                   local_repository_root="/test",
                                                                   path_module=posixpath), include_canonicalizer_factory=self.__create_include_path_canonicalizer_factory())
        test_str = "#include <string>\n"
        self.assertEquals(test_str, normalizer.normalize(test_str))
        
    def test3(self):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix="a/b.cpp",
                                                                   local_repository_root="/test",
                                                                   path_module=posixpath), include_canonicalizer_factory=self.__create_include_path_canonicalizer_factory())
        test_str = '#include "../x.h"\n'
        self.assertEquals('#include "x.h"\n', normalizer.normalize(test_str))
        
    def test4(self):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix="a/b.cpp",
                                                                   local_repository_root="/test",
                                                                   path_module=posixpath), include_canonicalizer_factory=self.__create_include_path_canonicalizer_factory())
        test_str = r'#include "..\x.h"\n'
        self.assertEquals('#include "x.h"\n', normalizer.normalize(test_str))
        
    def test5(self):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix="a/b.cpp",
                                                                   local_repository_root="/test",
                                                                   path_module=posixpath), include_canonicalizer_factory=self.__create_include_path_canonicalizer_factory())
        test_str = r'#include "..\y.h"\n'
        self.assertEquals('#include <../y.h>\n', normalizer.normalize(test_str))

    def test6(self):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix="a/b.cpp",
                                                                   local_repository_root="/test",
                                                                   path_module=posixpath), include_canonicalizer_factory=self.__create_include_path_canonicalizer_factory())
        test_str = r'#include "/std-include/string"\n'
        self.assertEquals('#include <string>\n', normalizer.normalize(test_str))
        
class FuzzyResolverInternalTest(unittest.TestCase):
    def test1(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', )}), 
                                         path_module=posixpath)
        self.assertEqual((), resolver.get_matches('asename'))
        self.assertEqual(('/a/b/basename', ), resolver.get_matches('basename'))
        self.assertEqual(('/a/b/basename', ), resolver.get_matches('../c/basename'))
        
    def test1b(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', )}),
                                         match_nonexact_if_unique=False,
                                         match_partially_unique=False,
                                         path_module=posixpath)
        self.assertEqual((), resolver.get_matches('asename'))
        self.assertEqual(('/a/b/basename', ), resolver.get_matches('basename'))
        self.assertEqual((), resolver.get_matches('../c/basename'))
 
    def test1c(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', )}),
                                         match_nonexact_if_unique=True,
                                         match_partially_unique=False,
                                         path_module=posixpath)
        self.assertEqual((), resolver.get_matches('asename'))
        self.assertEqual(('/a/b/basename', ), resolver.get_matches('basename'))
        self.assertEqual(('/a/b/basename',), resolver.get_matches('../c/basename'))
        self.assertEqual(('/a/b/basename',), resolver.get_matches('b/basename'))
        self.assertEqual((), resolver.get_matches('b\basename'))

    def test1d(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', '/b/c/basename')}),
                                         match_nonexact_if_unique=True,
                                         match_partially_unique=False,
                                         path_module=posixpath)
        self.assertEqual((), resolver.get_matches('asename'))
        self.assertEqual(('/a/b/basename', '/b/c/basename'), resolver.get_matches('basename'))
        self.assertEqual(('/b/c/basename',), resolver.get_matches('../c/basename'))
        self.assertEqual(('/a/b/basename',), resolver.get_matches('b/basename'))
        self.assertEqual(('/a/b/basename', '/b/c/basename'), resolver.get_matches('../d/c/basename'))
                
    def test5(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', '/b/c/basename')}), 
                                         path_module=posixpath)
        self.assertEqual(('/b/c/basename', ), resolver.get_matches('../d/c/basename'))     
                   
    def test2(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', '/b/c/basename')}), 
                                         path_module=posixpath)
        self.assertEqual(('/a/b/basename', '/b/c/basename'), resolver.get_matches('basename'))

    def test3(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', '/b/c/basename')}), 
                                         path_module=posixpath)
        self.assertEqual(('/b/c/basename', ), resolver.get_matches('c/basename'))

    def test4(self):
        resolver = FuzzyResolverInternal(filemap=dict({'basename': ('/a/b/basename', '/b/c/basename')}), 
                                         path_module=posixpath)
        self.assertEqual(('/b/c/basename', ), resolver.get_matches('../c/basename'))
        