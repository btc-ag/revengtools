'''
Created on 18.02.2012

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.core_if import EnumerationItem, Enumeration

class IncludeSpecificationType(EnumerationItem):
    pass

class IncludeSpecificationTypes(Enumeration):
    _type = IncludeSpecificationType
    ANGLE = IncludeSpecificationType()
    QUOTED = IncludeSpecificationType()

class IIncludePathCanonicalizer(object):
    def get_canonic_paths(self, include_specification_types):
        raise NotImplementedError(self.__class__)

    def canonicalize(self, included_file):
        """
        
        @param included_file: 
        @type included_file: str or ProjectFile
        @rtype: tuple(IncludeSpecificationType, Resource)
        """        
        raise NotImplementedError(self.__class__)        
            
class IIncludePathCanonicalizerFactory(AutoConfigurable):
    def get_include_path_canonicalizer(self, implementation_file, included_file):
        raise NotImplementedError(self.__class__)
            
