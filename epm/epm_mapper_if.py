'''
Created on 26.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

# TODO drei Teile: logische Elemente, physische Elemente und Abbildung

class PhysicalToLogicalMapper(AutoConfigurable):
    """
    Provides a mapping from the physical elements (modules) to Quasar-like 
    logical elements (components, interfaces, configurators) and their 
    categories according to the EPM Architectural Style. This must be 
    implemented in a technology-specific way (e.g. to honour naming 
    conventions), and may need to be customized for integration with 
    legacy systems (which were designed before the 
    EPM Architectural Style was defined or applied). 
    """ 
    def get_logical_element(self, module):
        '''
        
        @param physical_element:
        @rtype: LogicalElement
        '''
        raise NotImplementedError
    
class CategoryMapper(AutoConfigurable):
    def get_category(self, logical_element):
        raise NotImplementedError


if __name__ == "__main__":
    import doctest
    doctest.testmod()
