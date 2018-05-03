'''
Created on 12.10.2010

@author: SIGIESEC
'''
from commons.core_util import CollectionTools
from cpp.cpp_if import CppFileConfiguration, FileToModuleMapSupply
import os.path
import logging


class DefaultCppFileConfiguration(CppFileConfiguration):
    _header_file_extensions = ['.h', '.hpp']
    _implementation_file_extensions = ['.c', '.cpp']
    
    def get_header_file_extensions(self):
        return self._header_file_extensions

    def get_implementation_file_extensions(self):
        return self._implementation_file_extensions

    def is_header_file(self, path):
        ext = os.path.splitext(path)[1]
        return ext in self.get_header_file_extensions() 

    def is_implementation_file(self, path):
        """
        >>> DefaultCppFileConfiguration.is_implementation_file("foo.c")
        True
        >>> DefaultCppFileConfiguration.is_implementation_file("foo.cpp")
        True
        >>> DefaultCppFileConfiguration.is_implementation_file("foo.h")
        False
        """
        ext = os.path.splitext(path)[1]
        return ext in self.get_implementation_file_extensions() 

class BaseFileToModuleMapSupply(FileToModuleMapSupply):
    def __init__(self):
        self.__individual_to_input_aggregate_map = [None, None]
        self.__module_to_file_map = [None, None]
        self.__logger = logging.getLogger(self.__module__)
        
    def get_header_file_to_module_map(self, use_exceptions=True):
        header_file_to_module_map = dict([(filename, module) for (module, filename) in self.get_module_to_header_file_map_final()])
        if use_exceptions:
            header_file_to_module_map.update(dict([(filename, module) for (module, filename) in self.get_header_file_map_exceptions()]))
        #for entry in header_file_to_module_map:
            #self.__logger.info("Header file to module map: %s")%str(entry)
        return header_file_to_module_map

    def get_implementation_file_to_module_map(self, use_exceptions=True):
        modules_per_implementation_file = dict([(filename, module) for (module, filename) in self.get_module_to_implementation_file_map()])
        if use_exceptions:
            modules_per_implementation_file.update(dict([(filename, module) for (module, filename) in self.get_implementation_file_map_exceptions()]))
        if modules_per_implementation_file !=None:
            try:
                for entry in modules_per_implementation_file:
                    self.__logger.info("entry in modules per implementation file: %s"%entry)
            except:
                self.__logger.info("Writing entries for modules per implementation file failed")
            #TODO: see also cpp/header_linker_default
            #self.__logger.info("modules per implementation file dict: %s")%str(modules_per_implementation_file)
            #do not understand error message:
            #TypeError: unsupported operand type(s) for %: 'NoneType' and 'str'
            #self.__logger.info("modules per implementation file dict: %s")%(modules_per_implementation_file)
            #TypeError: unsupported operand type(s) for %: 'NoneType' and 'dict'
            #especially cause following is possible:
            #diction = dict({None: None})
            #print ("Print the dict %s")%diction
        else:
            self.__logger.critical("no modules per implementation file dict!")
        return modules_per_implementation_file

    def generate_file_to_module_map(self, use_exceptions=True):
        if self.__individual_to_input_aggregate_map[use_exceptions] == None:
            self.__individual_to_input_aggregate_map[use_exceptions] = self.get_header_file_to_module_map(use_exceptions)
            self.__individual_to_input_aggregate_map[use_exceptions].update(self.get_implementation_file_to_module_map(use_exceptions))
        return self.__individual_to_input_aggregate_map[use_exceptions]

    def generate_module_to_file_map(self, use_exceptions=True):
        # TODO nicht erst die inverse berechnen
        if self.__module_to_file_map[use_exceptions] == None:
            self.__module_to_file_map[use_exceptions] = CollectionTools.transpose(self.generate_file_to_module_map(use_exceptions))
        return self.__module_to_file_map[use_exceptions]
