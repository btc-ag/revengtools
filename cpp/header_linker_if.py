#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 24.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
                
class BaseOutput(object):
    def __init__(self):
        pass

    def add_module_map(self, module, header):
        raise NotImplementedError()
        
    def write(self):
        raise NotImplementedError()

class DictOutput(BaseOutput):
    def __init__(self):
        self.__store = dict()
        
    def add_module_map(self, module, header):
        # TODO hier wird das umkehren des Dictionary schon vorgenommen... das sollte außerhalb geschehen
        #assert module != None
        if module != None:
            self.__store[header] = module
        
    def write(self):
        pass

    def get_dict(self):
        return self.__store

    def clear_dict(self):
        self.__store = dict()

class HeaderLinkerStatistics(object):
    def __init__(self):
        self._file_matches_samemoduledir = 0
        self._file_matches_otherdir = 0
        self._dir_matches = 0
        self._module_spec_matches = 0
        self._no_matches = 0
        self._ignored_files = 0
        self._external_files_match = 0
        self._external_files_nomatch = 0
        
    def sum(self):
        return self._file_matches_samemoduledir + self._file_matches_otherdir + \
          self._dir_matches + self._module_spec_matches + self._no_matches + \
          self._ignored_files + self._external_files_match + self._external_files_nomatch  
          
class HeaderLinker(AutoConfigurable):
    def __init__(self,
                 data_supply=None,
                 file_to_module_map_supply=None,
                 outputter=DictOutput(),
                 use_implementation_mapping_exceptions=True):
        pass

    def outputter(self):
        raise NotImplementedError()
    
    def link_header(self, header, stats=HeaderLinkerStatistics()):
        raise NotImplementedError()

    def link_all_headers(self, header_list):
        raise NotImplementedError()      


if __name__ == "__main__":
    import doctest
    doctest.testmod()
