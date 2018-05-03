# -*- coding: UTF-8 -*-
'''
Created on 07.10.2010

@author: SIGIESEC
'''
from commons.config_if import ConfigDependent
from cpp.cpp_if import FileToModuleMapSupply
from cpp.incl_deps.include_deps_if import FileIncludeDepsSupply
from cpp.incl_deps.include_link_lifter_if import IncludeLinkLifter, ModuleLinks
import logging
import os.path

config_module_links = ModuleLinks

class DefaultIncludeLinkLifter(IncludeLinkLifter, ConfigDependent):
    FROM = 0
    TO = 1

    def __init__(self,
                 file_include_deps_supply=None,
                 file_to_module_map_supply=None,
                 node_restriction_in=None, *args, **kwargs):
        IncludeLinkLifter.__init__(self, 
                                   file_include_deps_supply=file_include_deps_supply, 
                                   file_to_module_map_supply=file_to_module_map_supply, 
                                   node_restriction_in=node_restriction_in, 
                                   *args, **kwargs)
        assert isinstance(file_include_deps_supply, FileIncludeDepsSupply)
        assert isinstance(file_to_module_map_supply, FileToModuleMapSupply) 
        # TODO the following should be made a parameter
        self.combined_modules = True
        self.__file_include_deps_supply = file_include_deps_supply
        self.__file_to_module_map_supply = file_to_module_map_supply
        
        self.__ignored_files = None
        self.__out_of_scope_files = None
        self.__missing_files = None
        
        self.__node_restriction_in = node_restriction_in
        
        self.__logger = logging.getLogger(self.__class__.__module__)

    def __log_missing_file(self, file_path, direction):
        if file_path not in self.__missing_files:
            self.__missing_files[file_path] = [0, 0]
        self.__missing_files[file_path][direction] += 1
        
    def report_missing_files(self):
        self.__logger.info("%i total files, %i files ignored, %i files out of scope, %i other files not linked to a module" % 
                     (len(self.__individual_to_input_aggregate_map), len(self.__ignored_files), len(self.__out_of_scope_files), len(self.__missing_files)))
        self.__logger.debug("List of files not linked to a module")
        for (path, counts) in sorted(self.__missing_files.iteritems()):
            self.__logger.debug("%s %s" % (path, str(counts)))    
            
    def _out_of_scope(self, path):
        # TODO map external header files (absolute paths) to virtual modules
        return os.path.isabs(path)

    def _ignore_missing(self, path):
        return False
    
    @staticmethod
    def __log_file_generic(dictionary, path):
        if path not in dictionary:
            dictionary[path] = 0
        dictionary[path] += 1
    
    def __log_ignored_file(self, file_path):
        self.__log_file_generic(self.__ignored_files, file_path)
            
    def __log_out_of_scope_file(self, file_path):
        self.__log_file_generic(self.__out_of_scope_files, file_path)

    def __process_missing_file(self, path, position):
        if self._ignore_missing(path):
            self.__log_ignored_file(path)
        elif self._out_of_scope(path):
            self.__log_out_of_scope_file(path)
        else:
            self.__log_missing_file(path, position)

    def release(self):
        self.__file_to_module_map_supply = None # save space
        self.__individual_to_input_aggregate_map = None
        self.__file_include_deps_supply = None

        self.__ignored_files = None
        self.__out_of_scope_files = None
        self.__missing_files = None

    def process(self, use_mapping_exceptions=True):
        """
        
        May only be called once.
        """
        # TODO statt dieser Release-Methode sollte ein temporäres internes Objekt verwendet werden.
        if self.__file_to_module_map_supply == None:
            raise RuntimeError("IncludeLinkLifter.process was illegally called more than once")
        
        # TODO use_mapping_exceptions should not be passed to this method. If the caller wants to 
        # manipulate the setting, it should create a FileToModuleMapSupply with the desired 
        # features
        self.__individual_to_input_aggregate_map = self.__file_to_module_map_supply.generate_file_to_module_map(use_mapping_exceptions)
        
        self.__module_links = config_module_links(combined_modules=self.combined_modules, 
                                                  node_restriction_in=self.__node_restriction_in)
        file_links = self.__file_include_deps_supply.get_file_include_deps()
        self.__missing_files = dict()
        self.__ignored_files = dict()
        self.__out_of_scope_files = dict()
        for (from_file, to_file) in file_links:
            if from_file not in self.__individual_to_input_aggregate_map:
                self.__process_missing_file(from_file, self.FROM)
            elif to_file not in self.__individual_to_input_aggregate_map:
                self.__process_missing_file(to_file, self.TO)
            else:
                #self.__logger.debug("%s:%s -> %s:%s" % (__individual_to_input_aggregate_map[from_file],from_file,__individual_to_input_aggregate_map[to_file],to_file))
                if self.__individual_to_input_aggregate_map[from_file] != self.__individual_to_input_aggregate_map[to_file]:
                    self.__module_links.add((self.__individual_to_input_aggregate_map[from_file], 
                                             self.__individual_to_input_aggregate_map[to_file]))
                    
        self.report_missing_files()
    
        self.__module_links.join_regular_incs()
        
        self.release()
    
    def get_module_links(self):
        return self.__module_links
