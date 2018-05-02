#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 24.09.2010

@author: SIGIESEC
'''
from cpp.cpp_default import BaseFileToModuleMapSupply
from cpp.cpp_if import FileToModuleMapSupply
from cpp.file_supply import InternalHeaderListSupply
from cpp.header_linker_if import DictOutput, HeaderLinker
import logging
from commons.config_if import ConfigDependent

config_file_to_module_map_supply = FileToModuleMapSupply()
config_header_linker = HeaderLinker

# TODO Decorator zum Cachen der Dateien schreiben

# TODO dies "Header Exception Only" sollte über einen Parameter eingestellt werden
# Die Klasse sollte aufgeteilt werden?
class OnTheFlyHeaderExceptionOnlyFileToModuleMapSupply(BaseFileToModuleMapSupply, ConfigDependent):
    def __init__(self):
        BaseFileToModuleMapSupply.__init__(self)
        self.__header_file_to_module_map = None

    def get_module_to_header_file_map(self):
        # TODO hier inverses get_header_file_to_module_map zurückgeben?
        return config_file_to_module_map_supply.get_module_to_header_file_map()

    def get_module_to_implementation_file_map(self):
        return config_file_to_module_map_supply.get_module_to_implementation_file_map()

    def get_implementation_file_map_exceptions(self):
        return ()    

    @staticmethod
    def __create_header_file_to_module_map():
        logging.getLogger(OnTheFlyHeaderExceptionOnlyFileToModuleMapSupply.__module__).info("Linking headers to modules")
        outputter = DictOutput()
        header_list = InternalHeaderListSupply().get_header_list()
        config_header_linker(outputter=outputter, use_implementation_mapping_exceptions=False).link_all_headers(header_list)
        return outputter.get_dict()

    def get_header_file_to_module_map(self, use_exceptions):
        if self.__header_file_to_module_map == None:
            self.__header_file_to_module_map = self.__create_header_file_to_module_map()
        header_file_to_module_map = self.__header_file_to_module_map
        #if use_exceptions:
        header_file_to_module_map.update(dict([(filename, module) 
                                               for (module, filename) 
                                               in config_file_to_module_map_supply.get_header_file_map_exceptions()]))
        return header_file_to_module_map
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    