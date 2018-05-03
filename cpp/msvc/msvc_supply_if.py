'''
Created on 28.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class MSVCDataSupply(AutoConfigurable):
    def is_module_empty(self, module):
        raise NotImplementedError

    def get_module_to_vcproj_map(self):
        raise NotImplementedError

    def get_vcproj_list(self):
        raise NotImplementedError
