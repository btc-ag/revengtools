# -*- coding: UTF-8 -*-
'''
Created on 22.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.progress_if import ProgressListener
from cpp.cpp_if import CppDataSupply, FileToModuleMapSupply
from cpp.cpp_util import IncludePathMapping
from cpp.idep.cdep_include_deps_base import CdepIncludeDependencyGeneratorBase
from cpp.incl_deps.include_deps_if import IncludeDependencyGenerator
from tempfile import mkstemp
import logging
import os.path
from cpp.cpp_util_wrap import get_default_include_path_mapping

config_basic = BasicConfig()
config_cpp_data_supply = CppDataSupply
config_file_to_module_map_supply = FileToModuleMapSupply
config_progress_listener = ProgressListener

class DirwiseCdepIncludeDependencyGenerator(CdepIncludeDependencyGeneratorBase):
    
    def __init__(self):
        CdepIncludeDependencyGeneratorBase.__init__(self)
        # TODO remove the fallback
        self.__cdep_path = os.environ.get("CDEP_PROGRAM")
        if self.__cdep_path is None:
          self.__cdep_path = os.path.join(config_basic.get_revengtools_basedir(), 
                                          "cpp", "idep", "cdep.exe")
        self.__directory_to_file_map = None
        self.__file_count = 0
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__progress_listener = config_progress_listener()

    def generate(self):
        self._generate_include_path_temp_file()
        os.chdir(config_basic.get_local_source_base_dir())
        directories = self.__get_directories()
        self.__progress_listener.set_total(len(directories))
        for directory in directories:
            self.generate_dir(directory)
            self.__progress_listener.increment(1)
        self._remove_include_path_temp_file()

    @staticmethod
    def split_into_two_halves(input_files):
        """
        >>> input_files=[1,2,3]
        >>> two_halves = DirwiseCdepIncludeDependencyGenerator.split_into_two_halves(input_files)
        >>> list(two_halves[0] + two_halves[1]) == input_files
        True
        >>> list(two_halves[0])
        [1]
        """
        split_point = len(input_files) / 2
        two_halves = input_files[:split_point], input_files[split_point:]
        return two_halves

    def generate_for_input_files_in_dir(self, directory, input_files):
        cmdline = self._get_cmdline(directory, input_files)
        if len(cmdline) > 8191:
            input_files = list(input_files)
            self.__logger.info("cmdline too long, splitting for directory %s" % (directory, ))
            two_halves = self.split_into_two_halves(input_files)
            for portion in two_halves:
                self.generate_for_input_files_in_dir(directory, portion)
        else:
            self.__logger.debug("calling %s" % (cmdline, ))
            os.system(cmdline)

    def generate_dir(self, directory): 
        input_files = self.__get_files(directory)
        self.__logger.debug("Generating include deps for %i files in directory %s" % (len(input_files), directory))
        
        if len(input_files) > 0:
            self.generate_for_input_files_in_dir(directory, input_files)

    def __add_path(self, path):
        dirname = os.path.dirname(path)
        if dirname.find("&") != -1:
            self.__logger.warning("Skipping file in directory with illegal character: %s" % path)
        else:
            if dirname not in self.__directory_to_file_map:
                self.__directory_to_file_map[dirname] = set()
            self.__directory_to_file_map[dirname].add(path)
            self.__file_count += 1

    def __generate_directory_to_file_map(self):
        self.__logger.debug("Generating directory to file map")
        self.__directory_to_file_map = dict()
        # read headerlist
        header_files = config_cpp_data_supply().get_header_list()
        for path_line in header_files:
            self.__add_path(path_line[0])
            
        # read vcproj_to_implementation_files
        implementation_files = config_file_to_module_map_supply().get_module_to_implementation_file_map()
        for path_line in implementation_files:
            self.__add_path(path_line[1])
            
        self.__logger.info("%i input files (incl. duplicates) specified in %i directories" % (self.__file_count, len(self.__directory_to_file_map.keys())))
        
    def __get_directories(self):
        if self.__directory_to_file_map == None:
            self.__generate_directory_to_file_map()
        return self.__directory_to_file_map.keys()
    
    def __get_files(self, directory):
        return self.__directory_to_file_map[directory]

    def incremental_generate(self):
        pass
        # TODO
        # if solution_file_changed:
        #    generate for new projects
        #    remove for removed projects
        # if vcproj_changed:
        #    generate for new files
        #    remove for removed files
        # for all changed files:
        #    regenerate
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()

