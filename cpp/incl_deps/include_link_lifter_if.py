'''
Created on 07.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import DependencyFilter
from commons.config_if import AutoConfigurable

class ModuleLinks(AutoConfigurable):
    def __init__(self, combined_modules, node_restriction_in = None):
        raise NotImplementedError

    def __initialize_universal_output(self):
        raise NotImplementedError

    def universal_output(self, outputter):
        """
        @type outputter: DependencyFilter
        """
        raise NotImplementedError

    def rename_node(self, old_name, new_name):
        raise NotImplementedError
        
    def get_incoming_link_counts(self):
        raise NotImplementedError
    
    def join_regular_incs(self):
        raise NotImplementedError
            
    def add(self, element):        
        raise NotImplementedError
    
class IncludeLinkLifter(AutoConfigurable):
    def __init__(self,
                 file_include_deps_supply,
                 file_to_module_map_supply,
                 node_restriction_in=None, *args, **kwargs):
        pass

    def report_missing_files(self):
        raise NotImplementedError

    def process(self, use_mapping_exceptions = True):
        raise NotImplementedError

    def get_module_links(self):
        '''
        @rtype: ModuleLinks
        '''
        raise NotImplementedError
    
