'''
Created on 01.10.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
    
class ModuleLinkDepsSupply(AutoConfigurable):
    def get_module_link_deps_graph(self):
        """
        @rtype: AttributeGraph
        """
        raise NotImplementedError
