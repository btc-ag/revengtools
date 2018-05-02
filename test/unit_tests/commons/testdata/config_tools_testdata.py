'''
Created on 17.05.2011

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class AbstractAutoConfigurable(AutoConfigurable):
    pass

class ConcreteAutoConfigurable(AbstractAutoConfigurable):
    def __init__(self):
        pass

class ConcreteAutoConfigurableWithArgs(AbstractAutoConfigurable):
    def __init__(self, testarg, defarg=None, *args, **kwargs):
        self.__testarg = testarg
        self.__defarg = defarg

    def get_testarg(self):
        return self.__testarg


    def get_defarg(self):
        return self.__defarg


    def set_testarg(self, value):
        self.__testarg = value


    def set_defarg(self, value):
        self.__defarg = value


    def del_testarg(self):
        del self.__testarg


    def del_defarg(self):
        del self.__defarg

    testarg = property(get_testarg, set_testarg, del_testarg, "testarg's docstring")
    defarg = property(get_defarg, set_defarg, del_defarg, "defarg's docstring")

class UnrelatedClass(object):
    pass

class Test(object):
    aac_instance = AbstractAutoConfigurable()
    aac_class = AbstractAutoConfigurable

    cac_instance = ConcreteAutoConfigurable()
    cac_class = ConcreteAutoConfigurable

config_var_instance = AbstractAutoConfigurable()
config_var_class = AbstractAutoConfigurable
config_var_none = UnrelatedClass
