'''
Created on 05.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable, ConfigDependent
from cpp.cpp_if import CppFileConfiguration

class UnknownPath(Exception):
    def __init__(self, path):
        Exception.__init__(self)
        self.__path = path

    def get_path(self):
        return self.__path

    def __str__(self, *args, **kwargs):
        return "UnknownPath(%s)" % (self.__path, )

class IncludeRulesFactory(AutoConfigurable):
    def get_include_rules(self):
        raise NotImplementedError(self.__class__)

config_cpp_file_configuration = CppFileConfiguration()

class IncludeRuleChecker(AutoConfigurable, ConfigDependent):
    # TODO move check of known paths out of the interface, into a specific rule implementation
    def is_known_path(self, path):
        raise NotImplementedError(self.__class__)
    
    def is_legal_dependency(self, from_file, to_file):
        # TODO assert is_path(from_file) and is_path(to_file)
        assert isinstance(from_file, basestring) and isinstance(to_file, basestring)
        
        if not self.is_known_path(from_file):
            raise UnknownPath(from_file)
        if not self.is_known_path(to_file):
            raise UnknownPath(to_file)
        return config_cpp_file_configuration.is_header_file(to_file)    

    def get_rule_name(self):
        return self.__class__.__name__

    def get_violation_description(self, from_file, to_file):
        """
        @precondition: not self.is_legal_dependency(from_file, to_file)
        """
        return "Violation of %s" % (self.get_rule_name(), )  

class NullIncludeRuleChecker(IncludeRuleChecker):
    def is_known_path(self, path):
        return True
    
    def is_legal_dependency(self, from_file, to_file):
        return True

class NullIncludeRulesFactory(IncludeRulesFactory):
    def get_include_rules(self):
        return ()
    
