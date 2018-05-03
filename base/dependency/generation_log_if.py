# -*- coding: UTF-8 -*-
'''
Created on 26.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import GraphDescription
from commons.config_if import AutoConfigurable

class GenerationLogGenerator(AutoConfigurable):
    """
    Storage interface for a generation log, i.e. a log of generated output files
    to be displayed to the user.
    
    A typical implementation will provide a persistent storage which can be reused 
    across processes.
    
    @see: C{GenerationLogSupply} for the companion interface for querying a 
      generation log.            
    """
    
    def add_generated_file(self, description, filename=None):
        assert isinstance(description, GraphDescription)
        raise NotImplementedError
    
class GenerationLogSupply(AutoConfigurable):
    """
    Query interface for a generation log, which has been created using
    a corresponding C{GenerationLogGenerator} instance.
    """
    
    def get_generation_log_iter(self):
        raise NotImplementedError
    
