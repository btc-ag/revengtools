'''
Created on 08.09.2010

@author: SIGIESEC
'''
from cast.technology import TechnologyConfig
from configuration.revengtools_config import RevEngToolsConfigParser

class RevEngToolsTechnologyConfig(TechnologyConfig):
    def __init__(self):
        TechnologyConfig.__init__(self)
        self.__adaptee = RevEngToolsConfigParser()

    def get_elementtypes_callables(self):
        return self.__adaptee.get("OBJECTTYPES_FUNCTION_LIKE")

    def get_elementtypes_data_structure(self):
        return self.__adaptee.get("OBJECTTYPES_STRUCT")

    def get_linktypes_data_structure_access(self):
        return self.__adaptee.get("LINKTYPES_STRUCT_ALL")

    def get_elementtypes_variable(self):
        return self.__adaptee.get("OBJECTTYPES_GV")
    
    def get_linktypes_variable_access(self):
        return self.__adaptee.get("LINKTYPES_VARIABLE_ALL")
    
    def get_elementtypes_macro(self):
        return self.__adaptee.get("OBJECTTYPES_MACRO")
    
    def get_linktypes_macro_usage(self):
        return self.__adaptee.get("LINKTYPES_MACRO")
    
    def get_linktypes_call(self):
        return self.__adaptee.get("LINKTYPES_FUNCTION_CALL")
