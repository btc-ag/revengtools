'''
Created on 13.10.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class DependencyParser(AutoConfigurable):
    """
    @deprecated: deprecated as a public interface for clients, use DependencyGraphFactory instead
    """
    def process(self):
        raise NotImplementedError(self.__class__)
    
    def output(self, outputter):
        raise NotImplementedError(self.__class__)
    
