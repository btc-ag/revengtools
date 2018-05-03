#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 22.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.generic_files_util import GenericFilesTools
from commons.config_if import ConfigDependent
from commons.os_util import NormalizedPathsIter
from cpp.cpp_default import BaseFileToModuleMapSupply
from cpp.cpp_if import CppDataSupply, HeaderListSupply
import logging
import os.path

config_basic = BasicConfig()
config_data_supply = CppDataSupply()

class FileCppDataSupplier(CppDataSupply, ConfigDependent):
    def __init__(self):
        CppDataSupply.__init__(self)

    def __header_list_filename(self):
        return os.path.join(config_basic.get_local_source_base_dir(), "headerlist")

    def __module_rootdirs_filename(self):
        return os.path.join(config_basic.get_results_directory(), "module_rootdirs")
    
    def get_module_rootdirs(self):
        # TODO this is wrong for cmake-generated files, if at all, it must be based on the location of the CMakeLists.txt file
        return dict(NormalizedPathsIter.create(self.__module_rootdirs_filename(), 
                                               "module rootdirs", 
                                               delimiter=':'))

    def get_header_list(self):
        # TODO Kopie erstellen? So kann die Liste nur einmal durchlaufen werden...
        return NormalizedPathsIter.create(self.__header_list_filename(), 
                                          "header list")
    
    
class InternalHeaderListSupply(HeaderListSupply, ConfigDependent):
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__) 

    def get_header_list(self):
        # TODO das sollte dieser Klasse als Parameter übergeben werden
        # bei Aufruf aus check_include_link_dep_consistency reicht vielleicht 
        # die Liste aus CppDataSupply (?) 
        
        # In CppDataSupply.get_header_list stehen nur die Header aus den Modulspezifikationen,
        # hier müssten jetzt alle in den include-statements vorkommenden Header 
        # verarbeitet werden.
        result = [x[0] for x in config_data_supply.get_header_list()]
        self.__logger.info("%i headers within project directory" % (len(result)))
        return result

    
class FileFileToModuleMapSupply(BaseFileToModuleMapSupply, ConfigDependent):

    def __init__(self, generic_files_tools=GenericFilesTools, *args, **kwargs):
        BaseFileToModuleMapSupply.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__module__)
        self.__generic_files_tools = generic_files_tools()

    def __str__(self):
        if config_basic.__class__ != BasicConfig: 
            return "%s reading from %s, %s, %s, %s, %s" % (self.__class__.__name__,
                                                       self.__module_to_implementation_file_map_filename(),
                                                       self.__header_mapping_exceptions_filename(),
                                                       self.__implementation_mapping_exceptions_filename(),
                                                       self.__module_to_header_file_map_final_filename(),
                                                       self.__module_to_header_file_map_filename(),
                                                       )
        else:
            return "%s (UNCONFIGURED)" % self.__class__.__name__
    
    def __module_to_implementation_file_map_filename(self):
        return self.__generic_files_tools.get_results_dir_filename("module_to_implementationfiles")

    def __header_mapping_exceptions_filename(self):
        return config_basic.get_version_specific_config_path("header_mapping_exceptions")

    def __implementation_mapping_exceptions_filename(self):
        return config_basic.get_version_specific_config_path("implementation_mapping_exceptions")

    def __module_to_header_file_map_final_filename(self):
        return self.__generic_files_tools.get_results_dir_filename("module_to_headerfiles_linked")

    def __module_to_header_file_map_filename(self):
        return self.__generic_files_tools.get_results_dir_filename("module_to_headerfiles_raw")

    def get_module_to_header_file_map(self):
        return NormalizedPathsIter.create(self.__module_to_header_file_map_filename(),
                                   "module to header file map",
                                   delimiter = ':')

    def get_module_to_implementation_file_map(self):
        self.__logger.info("filename of implementation file map: %s"%self.__module_to_implementation_file_map_filename())
        return NormalizedPathsIter.create(self.__module_to_implementation_file_map_filename(),
                                   "module to implementation file map",
                                   delimiter = ':')

    def get_module_to_header_file_map_final(self):
        return NormalizedPathsIter.create(self.__module_to_header_file_map_final_filename(),
                                   "module to linked header file map",
                                   delimiter = ',')

    def get_header_file_map_exceptions(self):
        return NormalizedPathsIter.create(self.__header_mapping_exceptions_filename(),
                                          "header file map exceptions", 
                                          delimiter=':',
                                          allow_missing=True)
    
    def get_implementation_file_map_exceptions(self):
        return NormalizedPathsIter.create(self.__implementation_mapping_exceptions_filename(),
                                          "implementation file map exceptions", 
                                          delimiter=':',
                                          allow_missing=True)
    