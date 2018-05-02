'''
Created on 30.05.2011

@author: SIGIESEC
'''
from commons.config_plain import (PlainAutoWireConfigParser, 
    PlainAutoWireConfigGenerator)
from commons.config_util import ClassLoader
from commons.configurator import ConcreteAdapterRegistry
from test.unit_tests.commons.testdata.config_tools_testdata import (
    ConcreteAutoConfigurable, AbstractAutoConfigurable, 
    ConcreteAutoConfigurableWithArgs)
from test.unit_tests.test_helper import TestDirectoryHelper
import unittest


class PlainAutoWireConfigParserTest(unittest.TestCase):
    def test_parse_lines_none(self):
        
        parser = PlainAutoWireConfigParser()
        self.assertEquals([], list(parser.parse_lines([])))
        self.assertFalse(parser.has_errors())

    def test_parse_lines_some_with_comment(self):
        parser = PlainAutoWireConfigParser()
        self.assertEquals([(("abstract", "Abstract"), (("concrete", "Concrete"), None))], 
                          list(parser.parse_lines(["abstract.Abstract=concrete.Concrete", "#comment"])))
        self.assertFalse(parser.has_errors())

    def test_parse_lines_some_with_empty_line(self):
        parser = PlainAutoWireConfigParser()
        self.assertEquals([(("abstract", "Abstract"), (("concrete", "Concrete"), None))], 
                          list(parser.parse_lines(["abstract.Abstract=concrete.Concrete", ""])))
        self.assertFalse(parser.has_errors())

    def test_parse_lines_failure_bad_comment(self):
        parser = PlainAutoWireConfigParser()
        self.assertEquals([(("abstract", "Abstract"), (("concrete", "Concrete"), None))], 
                          list(parser.parse_lines(["abstract.Abstract=concrete.Concrete", "badcomment"])))
        self.assertTrue(parser.has_errors())
        errors = list(parser.get_errors())
        self.assertEquals(1, len(errors))
        self.assertEquals(2, errors[0].get_context().get_line())

    def test_parse_lines_failure_invalid_expression(self):
        parser = PlainAutoWireConfigParser()
        self.assertEquals([], 
                          list(parser.parse_lines(["abstract.Abstract==concrete.Concrete"])))
        self.assertTrue(parser.has_errors())
        errors = list(parser.get_errors())
        self.assertEquals(1, len(errors))
        self.assertEquals(1, errors[0].get_context().get_line())
        
    def test_parse_lines_with_arg(self):
        parser = PlainAutoWireConfigParser()
        result = list(parser.parse_lines(["abstract.Abstract=concrete.Concrete[a=12]", "#comment"]))
        self.assertEquals((), tuple(parser.get_errors()))
        self.assertEquals([(("abstract", "Abstract"), (("concrete", "Concrete"), dict({"a": dict({"type": "str", "value": "12"})})))], 
                          result)
        

    def test_parse_lines_abstract_wo_concrete(self):
        parser = PlainAutoWireConfigParser()
        result = list(parser.parse_lines(["test.commons.testdata.config_tools_testdata.AbstractAutoConfigurable"]))
        self.assertEquals(1, len(tuple(parser.get_errors())))
        self.assertEquals([], result)
       
    #TODO: untested: parse_files...
    

class PlainAutoWireConfigGeneratorTest(unittest.TestCase):
    def test_simple(self):
        acg = PlainAutoWireConfigGenerator(abstracts_to_concrete_map=dict([(AbstractAutoConfigurable, set([ConcreteAutoConfigurable]))]))
        self.assertEquals(['# %s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable'%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix()),
                           ''], 
                          list(acg.get_configuration_lines()))

    def test_simple_selected(self):
        acg = PlainAutoWireConfigGenerator(abstracts_to_concrete_map=dict([(AbstractAutoConfigurable, set([ConcreteAutoConfigurable]))]),
                                           selection_strategy_func=lambda abstract, concretes: concretes[0] if len(concretes) else None)
        self.assertEquals([TestDirectoryHelper.getTestmodulesPrefix()+'.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable'%TestDirectoryHelper.getTestmodulesPrefix(),
                           ''], 
                          list(acg.get_configuration_lines()))

    def test_simple_args(self):
        acg = PlainAutoWireConfigGenerator(abstracts_to_concrete_map=dict([(AbstractAutoConfigurable, set([ConcreteAutoConfigurable]))]),
                                           args_func=lambda x: ("arg", ))
        self.assertEquals(['# %s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable[arg=???]'%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix()),
                           ''], 
                          list(acg.get_configuration_lines()))

    def test_simple_args_integration(self):
        acg = PlainAutoWireConfigGenerator(abstracts_to_concrete_map=dict([(AbstractAutoConfigurable, set([ConcreteAutoConfigurableWithArgs]))]),
                                           args_func=ClassLoader.get_constructor_args)
        self.assertEquals(['# %s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurableWithArgs[testarg=???,defarg=???]'%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix()),
                           ''], 
                          list(acg.get_configuration_lines()))


class ConcreteAdapterRegistryTest(unittest.TestCase):
    """
    This is not a real unit test, but an integration test.
    """
    def __load_class(self, m, c):
        cls = self.__map[(m,c)]
        self.__registry.register_concrete_adapter(cls, True)
        return cls
    
    def test_integration_init_no_args(self):
        parser = PlainAutoWireConfigParser()
        config = list(parser.parse_lines(["%s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable"%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix())]))
        self.assertEquals((), tuple(parser.get_errors())) 
        self.__map = dict(((("%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), "ConcreteAutoConfigurable"), 
                     ConcreteAutoConfigurable),))
        self.__registry = ConcreteAdapterRegistry(dict(config), self.__load_class, lambda x: None)
        self.assertEquals(ConcreteAutoConfigurable, type(self.__registry.get_concrete_adapter(AbstractAutoConfigurable)()))
        concrete_adapter = self.__registry.get_concrete_adapter(AbstractAutoConfigurable())
        self.assertEquals(ConcreteAutoConfigurable, type(concrete_adapter))
        
    def test_integration_init_with_args(self):
        parser = PlainAutoWireConfigParser()
        config = list(parser.parse_lines(["%s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurableWithArgs[testarg=12]"%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix())])) 
        self.assertEquals((), tuple(parser.get_errors())) 
        self.__map = dict(((("%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), "ConcreteAutoConfigurableWithArgs"), 
                     ConcreteAutoConfigurableWithArgs),))
        self.__registry = ConcreteAdapterRegistry(dict(config), self.__load_class, lambda x: None)
        self.assertEquals(ConcreteAutoConfigurableWithArgs, 
                          type(self.__registry.get_concrete_adapter(AbstractAutoConfigurable)()))
        concrete_adapter = self.__registry.get_concrete_adapter(AbstractAutoConfigurable())
        self.assertEquals(ConcreteAutoConfigurableWithArgs, type(concrete_adapter))
        self.assertEquals("12", concrete_adapter.get_testarg())

    def test_integration_init_with_args_and_types(self):
        parser = PlainAutoWireConfigParser()
        config = list(parser.parse_lines(["%s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurableWithArgs[testarg=12:int]"%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix())])) 
        self.assertEquals((), tuple(parser.get_errors())) 
        self.__map = dict(((("%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), "ConcreteAutoConfigurableWithArgs"), 
                     ConcreteAutoConfigurableWithArgs),))
        self.__registry = ConcreteAdapterRegistry(dict(config), self.__load_class, lambda x: None)
        self.assertEquals(ConcreteAutoConfigurableWithArgs, 
                          type(self.__registry.get_concrete_adapter(AbstractAutoConfigurable)()))
        concrete_adapter = self.__registry.get_concrete_adapter(AbstractAutoConfigurable())
        self.assertEquals(ConcreteAutoConfigurableWithArgs, type(concrete_adapter))
        self.assertEquals(12, concrete_adapter.get_testarg())
        
    #TODO: Is this behavior intended? Is the first entry overwritten? Should there be an error message?
    def test_integration_init_multiple_concrete_(self):
        parser = PlainAutoWireConfigParser()
        config = list(parser.parse_lines(["%s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurableWithArgs[testarg=12]"%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix()),
                                     "%s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable"%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix())])) 
        self.assertEquals((), tuple(parser.get_errors())) 
        self.__map = dict(((("%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), "ConcreteAutoConfigurableWithArgs"), 
                     ConcreteAutoConfigurableWithArgs),
                           (("%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), "ConcreteAutoConfigurable"), 
                     ConcreteAutoConfigurable)))
        self.__registry = ConcreteAdapterRegistry(dict(config), self.__load_class, lambda x: None)
        self.assertEquals(ConcreteAutoConfigurable, 
                          type(self.__registry.get_concrete_adapter(AbstractAutoConfigurable)()))
        concrete_adapter = self.__registry.get_concrete_adapter(AbstractAutoConfigurable())
        self.assertEquals(ConcreteAutoConfigurable, type(concrete_adapter))
        
    def test_integration_init_multiple_concrete__(self):
        parser = PlainAutoWireConfigParser()
        config = list(parser.parse_lines(["%s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurable"%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix()),
                                     "%s.commons.testdata.config_tools_testdata.AbstractAutoConfigurable=%s.commons.testdata.config_tools_testdata.ConcreteAutoConfigurableWithArgs[testarg=12]"%(TestDirectoryHelper.getTestmodulesPrefix(),TestDirectoryHelper.getTestmodulesPrefix())
                                     ])) 
        self.assertEquals((), tuple(parser.get_errors())) 
        self.__map = dict(((("%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), "ConcreteAutoConfigurableWithArgs"), 
                     ConcreteAutoConfigurableWithArgs),
                           (("%s.commons.testdata.config_tools_testdata"%(TestDirectoryHelper.getTestmodulesPrefix()), "ConcreteAutoConfigurable"), 
                     ConcreteAutoConfigurable)))
        self.__registry = ConcreteAdapterRegistry(dict(config), self.__load_class, lambda x: None)
        self.assertEquals(ConcreteAutoConfigurableWithArgs, 
                          type(self.__registry.get_concrete_adapter(AbstractAutoConfigurable)()))
        concrete_adapter = self.__registry.get_concrete_adapter(AbstractAutoConfigurable())
        self.assertEquals(ConcreteAutoConfigurableWithArgs, type(concrete_adapter))

    def test_integration_init_abstract_wo_concrete(self):
        parser = PlainAutoWireConfigParser()
        config = list(parser.parse_lines(["test.commons.testdata.config_tools_testdata.AbstractAutoConfigurable"]))
        self.assertEquals(1, len(tuple(parser.get_errors()))) 
        self.__map = dict(((("test.commons.testdata.config_tools_testdata", "ConcreteAutoConfigurable"), 
                     ConcreteAutoConfigurable),))
        self.__registry = ConcreteAdapterRegistry(dict(config), self.__load_class, lambda x: None)
        self.assertEquals(None, self.__registry.get_concrete_adapter(AbstractAutoConfigurable))
                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()