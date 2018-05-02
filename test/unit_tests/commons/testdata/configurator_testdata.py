"""
Created on 29.09.2012

@author: SIGIESEC
"""
from commons.config_if import AutoConfigurable, ConfigDependent, ObjectFactory

class _OtherInterface(AutoConfigurable):
    def their_method(self, param):
        raise NotImplementedError
    
class _OtherImplementation(_OtherInterface): 
    def their_method(self, param):
        return param

class _OneImplementation(ConfigDependent):
    def __init__(self, my_dependency=_OtherInterface()):
        self.__my_dependency = my_dependency

    def my_method(self, param):
        return self.__my_dependency.their_method(param)

class _OneImplementationAdditionalParam(object):
    def __init__(self, param, my_dependency=_OtherInterface()):
        self.__my_dependency = my_dependency
        self.__param = param

    def my_method(self, param):
        return self.__my_dependency.their_method(param) + self.__param
    
class _SecondInterface(AutoConfigurable):
    def second_method(self, param):
        raise NotImplementedError    

class _SecondImplementation(object):
    def __init__(self, my_dependency=_OtherInterface()):
        self.__my_dependency = my_dependency

    def second_method(self, param):
        return self.__my_dependency.their_method(param)

class _ThirdImplementation(object):
    def __init__(self, one_impl=_OneImplementation):
        self.__one_impl = one_impl()
    
    def third_method(self):
        return self.__one_impl.my_method("third")
    
class _FourthImplementation(ConfigDependent):
    def __init__(self, object_factory=ObjectFactory()):
        self.__one_impl = object_factory.create_instance(xxclsxx=_OneImplementation)
    
    def third_method(self):
        return self.__one_impl.my_method("fourth")
    