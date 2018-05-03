# -*- coding: UTF-8 -*-

'''
Created on 29.09.2010

@author: SIGIESEC
'''
from commons.core_if import EnumerationItem, Enumeration

class _LogicalEntityType(EnumerationItem):
    pass

class LogicalEntityTypes(Enumeration):
    Component = _LogicalEntityType
    Interface = _LogicalEntityType
    Configurator = _LogicalEntityType

class LogicalElement(object):
    def __init__(self, element_type, element_name):
        self.__type = element_type
        self.__name = element_name
        
    def get_type(self):
        return self.__type
    
    def get_name(self):
        return self.__name

