'''
Created on 17.05.2011

@author: SIGIESEC
'''
from commons.config_util import (ConfigTools, ModuleEnumerator, 
    AbstractsToConcreteMap, ModuleScanner, AutoWireConfigFileFinder, ClassLoader, 
    AutoWireConfigChecker)
from commons.os_util import FixedBaseDirPathResolver
from test.unit_tests.commons.testdata import config_tools_testdata
from test.unit_tests.commons.testdata.config_tools_testdata import (
    AbstractAutoConfigurable, ConcreteAutoConfigurable, UnrelatedClass, Test, 
    ConcreteAutoConfigurableWithArgs)
from test.unit_tests.test_helper import TestDirectoryHelper
import logging
import os.path
import unittest

class TestHelper(object):
    @staticmethod
    def get_base_directory():
        return os.path.normpath(os.path.join(os.path.dirname(config_tools_testdata.__file__), os.pardir, os.pardir, os.pardir, os.pardir))

    @staticmethod
    def get_base_resolver():
        return FixedBaseDirPathResolver(TestHelper.get_base_directory())


class ConfigToolsTest(unittest.TestCase):
    def test_is_class_abstract_autoconfigurable_1(self):
        self.assertTrue(ConfigTools.is_class_abstract_autoconfigurable(AbstractAutoConfigurable))
        
    def test_is_class_abstract_autoconfigurable_2(self):
        self.assertFalse(ConfigTools.is_class_abstract_autoconfigurable(ConcreteAutoConfigurable))

    def test_is_class_abstract_autoconfigurable_3(self):
        self.assertFalse(ConfigTools.is_class_abstract_autoconfigurable(UnrelatedClass))

    def test_is_class_concrete_autoconfigurable_1(self):
        self.assertFalse(ConfigTools.is_class_concrete_autoconfigurable(AbstractAutoConfigurable))
        
    def test_is_class_concrete_autoconfigurable_2(self):
        self.assertTrue(ConfigTools.is_class_concrete_autoconfigurable(ConcreteAutoConfigurable))

    def test_is_class_concrete_autoconfigurable_3(self):
        self.assertFalse(ConfigTools.is_class_concrete_autoconfigurable(UnrelatedClass))
        
    def test_is_class_any_autoconfigurable_1(self):
        self.assertTrue(ConfigTools.is_class_any_autoconfigurable(AbstractAutoConfigurable))
        
    def test_is_class_any_autoconfigurable_2(self):
        self.assertTrue(ConfigTools.is_class_any_autoconfigurable(ConcreteAutoConfigurable))

    def test_is_class_any_autoconfigurable_3(self):
        self.assertFalse(ConfigTools.is_class_any_autoconfigurable(UnrelatedClass))

    def test_to_fqn(self):
        self.assertEquals("test.unit_tests.commons.testdata.config_tools_testdata.AbstractAutoConfigurable", 
                          ConfigTools.to_fqn(AbstractAutoConfigurable))
        
    def test_fqn_to_pair_1(self):
        self.assertEquals(("module", "Class"), ConfigTools.fqn_to_pair("module.Class"))

    def test_fqn_to_pair_2(self):
        self.assertEquals(("package.module", "Class"), ConfigTools.fqn_to_pair("package.module.Class"))

    def test_fqn_to_pair_fail_1(self):
        self.assertRaises(ValueError, ConfigTools.fqn_to_pair, "package.module.")
        
    def test_fqn_to_pair_fail_2(self):
        self.assertRaises(ValueError, ConfigTools.fqn_to_pair, "Class")
        
    def test_fqn_to_pair_fail_3(self):
        self.assertRaises(ValueError, ConfigTools.fqn_to_pair, ".Class")

    def test_is_autoconfigurable_object_1(self):
        self.assertTrue(ConfigTools.is_autoconfigurable_object(Test.aac_instance))

    def test_is_autoconfigurable_object_2(self):
        self.assertFalse(ConfigTools.is_autoconfigurable_object(Test.aac_class))

    def test_is_autoconfigurable_object_3(self):
        self.assertFalse(ConfigTools.is_autoconfigurable_object(Test.cac_instance))

    def test_is_autoconfigurable_object_4(self):
        self.assertFalse(ConfigTools.is_autoconfigurable_object(Test.cac_class))

    def test_is_autoconfigurable_class_1(self):
        self.assertFalse(ConfigTools.is_autoconfigurable_class(Test, "aac_instance"))

    def test_is_autoconfigurable_class_2(self):
        self.assertTrue(ConfigTools.is_autoconfigurable_class(Test, "aac_class"))

    def test_is_autoconfigurable_class_3(self):
        self.assertFalse(ConfigTools.is_autoconfigurable_class(Test, "cac_instance"))

    def test_is_autoconfigurable_class_4(self):
        self.assertFalse(ConfigTools.is_autoconfigurable_class(Test, "cac_class"))
        
    def test_get_type_of_autoconfigurable_class_or_instance_1(self):
        self.assertEquals(AbstractAutoConfigurable, 
                          ConfigTools.get_type_of_autoconfigurable_class_or_instance(Test.aac_class))

    def test_get_type_of_autoconfigurable_class_or_instance_2(self):
        self.assertEquals(AbstractAutoConfigurable, 
                          ConfigTools.get_type_of_autoconfigurable_class_or_instance(Test.aac_instance))
        
    def test_get_config_variables_single(self):
        self.assertEquals(["config_var_class", "config_var_instance"], 
                          sorted(ConfigTools.get_config_variables_single(config_tools_testdata)))
        
    def test_get_config_variables_iter(self):
        self.assertEquals([(config_tools_testdata, "config_var_class"), (config_tools_testdata, "config_var_instance")], 
                          sorted(ConfigTools.get_config_variables_iter([config_tools_testdata])))
        
    def test_get_abstract_adapter_types_for_config_variables_iter(self):
        self.assertEquals([AbstractAutoConfigurable, AbstractAutoConfigurable, AbstractAutoConfigurable, AbstractAutoConfigurable], list(ConfigTools.get_abstract_adapter_types_for_config_variables_iter([(config_tools_testdata, "config_var_class"), (config_tools_testdata, "config_var_instance"), (config_tools_testdata, "config_var_class"), (config_tools_testdata, "config_var_instance")])))

    def test_get_abstract_adapter_types_for_config_variables_set(self):
        self.assertEquals([AbstractAutoConfigurable], list(ConfigTools.get_abstract_adapter_types_for_config_variables_set([(config_tools_testdata, "config_var_class"), (config_tools_testdata, "config_var_instance"), (config_tools_testdata, "config_var_class"), (config_tools_testdata, "config_var_instance")])))
        
class ModuleEnumeratorTest(unittest.TestCase):
    def test_get_package_for_dirname_1(self):
        self.assertEquals("",
                          ModuleEnumerator.get_package_prefix_for_dirname("."))

    def test_get_package_for_dirname_2(self):
        self.assertEquals("a.b.c.",
                          ModuleEnumerator.get_package_prefix_for_dirname("a/b/c"))

    def test_get_package_for_dirname_3(self):
        self.assertRaises(ValueError,
                          ModuleEnumerator.get_package_prefix_for_dirname, "../a/b/c")
    
    def test_find_modules_1(self):
        base_directory, testdata_directory = self.__get_directories()
        self.assertEquals(['test.unit_tests.commons.testdata.__init__', 
                           'test.unit_tests.commons.testdata.config_tools_testdata', 
                           'test.unit_tests.commons.testdata.config_tools_testdata2',
                           'test.unit_tests.commons.testdata.configurator_testdata',
                           ], 
                          sorted(ModuleEnumerator.find_modules(basedir=base_directory, startdir=testdata_directory)))

    def __get_directories(self):
        base_directory = TestHelper.get_base_directory()
        testdata_directory = os.path.join("test", "unit_tests", "commons", "testdata")
        self.assertTrue(os.path.exists(os.path.join(base_directory, testdata_directory)), 
                        "Test setup error: %s does not exist in %s" % (testdata_directory, base_directory))
        return base_directory, testdata_directory

    def test_find_modules_2(self):
        base_directory, testdata_directory = self.__get_directories()
        self.assertEquals(['__init__', 'config_tools_testdata', 'config_tools_testdata2', 'configurator_testdata'], 
                          sorted(ModuleEnumerator.find_modules(basedir=os.path.join(base_directory, testdata_directory))))
        
    def test_decode_parameter_value_1(self):
        self.assertEquals("14", ConfigTools.decode_parameter_value(dict({"value": "14", "type": "str"}), None))

    def test_decode_parameter_value_2(self):
        self.assertEquals(14, ConfigTools.decode_parameter_value(dict({"value": "14", "type": "int"}), None))

    def test_decode_parameter_value_3(self):
        self.assertRaises(ValueError, ConfigTools.decode_parameter_value, dict({"value": "xyz", "type": "int"}), None)

    def test_decode_parameter_value_class_1(self):
        self.assertEquals(ConcreteAutoConfigurable, ConfigTools.decode_parameter_value(dict({"value": "test.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable", "type": "class"}), 
                                                                    lambda module, cls:  ConcreteAutoConfigurable if (module, cls)==("test.commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable") else None))

    def test_decode_parameter_value_object_1(self):
        obj = ConfigTools.decode_parameter_value(dict({"value": "test.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable", "type": "object"}), 
                                                                    lambda module, cls:  ConcreteAutoConfigurable if (module, cls)==("test.commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable") else None)
        self.assertTrue(isinstance(obj, ConcreteAutoConfigurable))
        
class AbstractsToConcreteMapTest(unittest.TestCase):
    def setUp(self):
        self.__atcm = AbstractsToConcreteMap([AbstractAutoConfigurable, ConcreteAutoConfigurable])
    
    def test_get_map(self):
        self.assertEquals([(AbstractAutoConfigurable, set([ConcreteAutoConfigurable]))], 
                          list(self.__atcm.get_map().iteritems()))
    
    def test_find_abstract_1(self):
        self.assertEquals((AbstractAutoConfigurable, set([ConcreteAutoConfigurable])), 
                          self.__atcm.find_abstract(TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.AbstractAutoConfigurable"))

    def test_find_abstract_2(self):
        self.assertEquals((None, None), 
                          self.__atcm.find_abstract("test.commons.testdata.config_tools_testdata.UnrelatedClass"))

    def test_find_concretes_for_abstract(self):
        self.assertEquals([TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.ConcreteAutoConfigurable"], 
                          self.__atcm.find_concretes_for_abstract(TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.AbstractAutoConfigurable"))
        
    # TODO more tests: Abstract w/o any concrete, abstract with more than one concrete

class ModuleScannerTest(unittest.TestCase):
    def test_all(self):
        ms = ModuleScanner()
        ms.gather_autoconfigurables(config_tools_testdata)
        self.assertTrue(ms.modified())
        self.assertEquals([AbstractAutoConfigurable, ConcreteAutoConfigurable, ConcreteAutoConfigurableWithArgs],
                          sorted(ms.get_autoconfigurables(), key=str))
        ms.gather_autoconfigurables(config_tools_testdata)
        self.assertFalse(ms.modified())

class AutoWireConfigFileFinderTest(unittest.TestCase):
    def __exists(self, path):
        return True
    
    def setUp(self):
        self.__awcff = AutoWireConfigFileFinder(exists_func=self.__exists)
    
    def test_no_flavor(self):
        res = set(self.__awcff.find_autowire_configs())
        exp = set([
                   os.path.join(TestHelper.get_base_directory(), "configuration", "autowire.config"),
                   os.path.join(os.getcwd(),"autowire.config"),
                   ])
        self.assertEquals(exp,res)
        
    def test_two_flavors(self):
        self.__awcff.add_flavors(["flavor"])
        res = set(self.__awcff.find_autowire_configs())
        exp = set([
                   os.path.join(TestHelper.get_base_directory(), "configuration", "autowire.config"),
                   os.path.join(TestHelper.get_base_directory(), "configuration", "autowire.config-flavor"),
                   os.path.join(os.getcwd(),"autowire.config"),
                   os.path.join(os.getcwd(),"autowire.config-flavor"),
                   ])
        self.assertEquals(exp,res) 

class ClassLoaderTest(unittest.TestCase):
    # TODO add test for module not already loaded        

    def test_get_class(self):
        self.assertEquals(AbstractAutoConfigurable, 
                          ClassLoader.get_class(TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.AbstractAutoConfigurable"))

    def test_get_class_fail(self):
        self.assertRaises(RuntimeError, 
                          ClassLoader.get_class, TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.foo")

    def test_get_instance_no_arg(self):
        instance = ClassLoader.get_instance(TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.ConcreteAutoConfigurable")
        self.assertEquals(ConcreteAutoConfigurable, type(instance))

    def test_get_instance_with_arg(self):
        instance = ClassLoader.get_instance(TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.ConcreteAutoConfigurableWithArgs",
                                            dict({"testarg": 1}))
        self.assertEquals(ConcreteAutoConfigurableWithArgs, type(instance))
        self.assertEquals(1, instance.get_testarg())

    def test_get_instance_fail_extra_arg(self):
        self.assertRaises(TypeError, 
                          ClassLoader.get_instance, 
                          TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.ConcreteAutoConfigurable",
                          dict({"testarg": 1}))

    def test_get_instance_fail_missing_arg(self):
        self.assertRaises(TypeError, 
                          ClassLoader.get_instance, 
                          TestDirectoryHelper.getTestmodulesPrefix()+".commons.testdata.config_tools_testdata.ConcreteAutoConfigurableWithArgs")

class AutoWireConfigCheckerTest(unittest.TestCase):
    
    def get_module_prefix(self):
        return "test.unit_tests"
    
    def count_by_loglevel(self):
        problems = self.__checker.get_problems()
        return (len(filter(lambda (x,y,z): x==logging.INFO, problems)),
                len(filter(lambda (x,y,z): x==logging.WARNING, problems)),
                len(filter(lambda (x,y,z): x==logging.ERROR, problems)),
                )        
    
    def setUp(self):
        self.__checker = AutoWireConfigChecker()
    
    def test_okay(self):
        self.__checker.check_entry((("test.unit_tests.commons.testdata.config_tools_testdata", "AbstractAutoConfigurable"), 
                                    (("test.unit_tests.commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable"), dict())), None)
        self.assertFalse(self.__checker.has_problems(), self.__checker.get_problems())
        
    def test_abstract_missing(self):        
        self.__checker.check_entry((("xtest.commons.testdata.config_tools_testdata", "AbstractAutoConfigurable"), 
                                    ((self.get_module_prefix()+".commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable"), dict())), None)
        self.assertEquals((0, 0, 1), self.count_by_loglevel(), self.__checker.get_problems())

    def test_concrete_missing(self):        
        self.__checker.check_entry(((self.get_module_prefix()+".commons.testdata.config_tools_testdata", "AbstractAutoConfigurable"), 
                                    (("xtest.commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable"), dict())), None)
        self.assertEquals((0, 0, 1), self.count_by_loglevel(), self.__checker.get_problems())

    def test_both_missing(self):        
        self.__checker.check_entry((("xtest.commons.testdata.config_tools_testdata", "AbstractAutoConfigurable"), 
                                    (("xtest.commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable"), dict())), None)
        self.assertEquals((0, 0, 2), self.count_by_loglevel(), self.__checker.get_problems())

    def test_concrete_not_concrete_autoconfigurable(self):        
        self.__checker.check_entry(((self.get_module_prefix()+".commons.testdata.config_tools_testdata", "AbstractAutoConfigurable"), 
                                    ((self.get_module_prefix()+".commons.testdata.config_tools_testdata", "AbstractAutoConfigurable"), dict())), None)
        self.assertEquals((0, 1, 0), self.count_by_loglevel(), self.__checker.get_problems())

    def test_abstract_not_abstract_autoconfigurable(self):        
        self.__checker.check_entry(((self.get_module_prefix()+".commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable"), 
                                    ((self.get_module_prefix()+".commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable"), dict())), None)
        self.assertEquals((0, 1, 0), self.count_by_loglevel(), self.__checker.get_problems())

    def test_incompatible(self):
        self.__checker.check_entry(((self.get_module_prefix()+".commons.testdata.config_tools_testdata", "AbstractAutoConfigurable"), 
                                    ((self.get_module_prefix()+".commons.testdata.config_tools_testdata2", "ConcreteAutoConfigurableOther"), dict())), None)
        self.assertEquals((0, 1, 0), self.count_by_loglevel(), self.__checker.get_problems())
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
