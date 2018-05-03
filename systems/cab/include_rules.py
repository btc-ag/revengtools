'''
Created on 28.12.2011

@author: SIGIESEC
'''
from cpp.incl_deps.include_rule_checker_if import (IncludeRuleChecker, 
    IncludeRulesFactory)
import os

class CABFileTypes(object):
    """
    Contains methods determining the type of files according to CAB-specific 
    naming conventions.
    """
    
    @staticmethod
    def is_implementation_header(path):
        """
        Checks if the given path refers to an X{implementation header}, i.e.
        a header file containing implementation of template or inline functions
        or methods.
        
        TODO: this is currently based on the temporary naming convention that any 
        header ending with impl.h is an implementation header. This is subject 
        to revision. 

        """
        #return path.endswith("Impl.h")
        return path.lower().endswith("impl.h")
    
    @staticmethod
    def is_header(path):
        # TODO this also includes PRINS-specific conventions... 
        # some PRINS files have been imported into the CAB
        return path.lower().endswith((".h", ".dh", ".df", ".hpp", ".dc"))

    @staticmethod
    def is_implementation_file(path):
        return path.endswith(".cpp")    

class ImplementationHeaderRule(IncludeRuleChecker):
    """
    A rule that checks that implementation headers () are only 
    included by implementation files or other implementation headers, and 
    particularly not by regular headers.
    
    >>> rule = ImplementationHeaderRule()
    >>> rule.is_legal_dependency("Class.cpp", "Class.h")
    True
    >>> rule.is_legal_dependency("Class.h", "TemplateImpl.h")
    False
    >>> rule.is_legal_dependency("AnotherTemplateImpl.h", "TemplateImpl.h")
    True
    """
    
    def is_legal_dependency(self, from_file, to_file):                
        return not CABFileTypes.is_implementation_header(to_file) or \
            (CABFileTypes.is_implementation_header(from_file) or CABFileTypes.is_implementation_file((from_file)))

class NoImplementationFileIncludeRule(IncludeRuleChecker):
    """
    A rule that checks that implementation files are never included. 
    Implementation that needs to be included should be put in 
    implementation headers.
    
    >>> rule = NoImplementationFileIncludeRule()
    >>> rule.is_legal_dependency("Class.cpp", "Class.h")
    True
    >>> rule.is_legal_dependency("Class.cpp", "Class.df")
    True
    >>> rule.is_legal_dependency("Class.cpp", "AnotherClass.cpp")
    False
    """
    def is_legal_dependency(self, from_file, to_file):                
        return CABFileTypes.is_header(to_file) or os.path.isabs(to_file) # assume external files are always headers

class CABIncludeRulesFactory(IncludeRulesFactory):
    INCLUDE_RULES = (ImplementationHeaderRule(), NoImplementationFileIncludeRule())
    
    def get_include_rules(self):
        return self.INCLUDE_RULES

if __name__ == "__main__":
    import doctest
    doctest.testmod()
