"""
Created on 29.09.2012

@author: SIGIESEC
"""
from commons.configurator import InstanceConfigurator
from test.unit_tests.commons.testdata.configurator_testdata import (
    _OneImplementation, _OneImplementationAdditionalParam, _SecondInterface,
    _ThirdImplementation, _FourthImplementation, _OtherImplementation)
import unittest

class InstanceConfiguratorTest(unittest.TestCase):

    def test_get_concrete_adapter(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),
                         (("test.unit_tests.commons.testdata.configurator_testdata", "_SecondInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_SecondImplementation"), dict())),
                         )
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.get_concrete_adapter(_SecondInterface())
        self.assertEquals("test", my_object.second_method("test"))

    def test_create_instance_no_additional_param(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_instance(_OneImplementation)
        self.assertEquals("test", my_object.my_method("test"))

    def test_create_factory_no_additional_param(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_factory(_OneImplementation)()
        self.assertEquals("test", my_object.my_method("test"))

    def test_create_instance_additional_param(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_instance(_OneImplementationAdditionalParam, param="x")
        self.assertEquals("testx", my_object.my_method("test"))

    def test_create_factory_additional_param_prebound(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_factory(_OneImplementationAdditionalParam, param="x")()
        self.assertEquals("testx", my_object.my_method("test"))

    def test_create_factory_additional_param(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_factory(_OneImplementationAdditionalParam)(param="x")
        self.assertEquals("testx", my_object.my_method("test"))

    def test_create_factory_additional_param_positional(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_factory(_OneImplementationAdditionalParam)("x")
        self.assertEquals("testx", my_object.my_method("test"))

    def test_create_factory_missing_additional_param(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        self.assertRaises(TypeError, configurator.create_factory(_OneImplementationAdditionalParam))
        # TODO check for string: __init__() takes at least 2 non-keyword arguments (1 given)
        
    def test_create_instance_indirect_config_dependent(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_factory(_ThirdImplementation)()
        self.assertEquals("third", my_object.third_method())

    def test_create_instance_indirect_object_factory(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),)
        configurator = InstanceConfigurator(configuration)
        my_object = configurator.create_instance(_FourthImplementation)
        self.assertEquals("fourth", my_object.third_method())
        
    # TODO add test case where an instance of a ConfigDependent class is injected
    # TODO add failure test cases
    
    def test_get_required_concrete_adapters(self):
        configuration = ((("test.unit_tests.commons.testdata.configurator_testdata", "_OtherInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_OtherImplementation"), dict())),
                         (("test.unit_tests.commons.testdata.configurator_testdata", "_SecondInterface"), 
                          (("test.unit_tests.commons.testdata.configurator_testdata", "_SecondImplementation"), dict())),
                         )
        configurator = InstanceConfigurator(configuration)
        actualRequired = frozenset(configurator.get_required_concrete_adapters(_OneImplementation))
        expectedRequired = frozenset([_OtherImplementation])
        self.assertEquals(expectedRequired,
                          actualRequired)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
