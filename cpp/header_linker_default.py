#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 26.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.config_if import ConfigDependent
from commons.core_util import CollectionTools
from cpp.cpp_if import (CppDataSupply, FileToModuleMapSupply, 
    CppFileConfiguration)
from cpp.cpp_util_wrap import get_default_include_path_mapping
from cpp.header_linker_if import (HeaderLinker, DictOutput, 
    HeaderLinkerStatistics)
import logging
import os.path
import posixpath

# TODO prüfen, ob diese Default-Instanzen benötigt werden

# TODO generell posixpath statt os.path verwenden

config_basic = BasicConfig()
config_cpp_data_supply = CppDataSupply()
config_file_to_module_map_supply = FileToModuleMapSupply()
config_cpp_file_configuration = CppFileConfiguration()

class DefaultHeaderLinker(HeaderLinker, ConfigDependent):
    def __init__(self,
                 data_supply=None,
                 file_to_module_map_supply=None,
                 outputter=DictOutput(),
                 use_implementation_mapping_exceptions=True):
        HeaderLinker.__init__(self,
                     data_supply=data_supply,
                     file_to_module_map_supply=file_to_module_map_supply,
                     outputter=outputter,
                     use_implementation_mapping_exceptions=use_implementation_mapping_exceptions)
        if data_supply == None:
            data_supply = config_cpp_data_supply
        if file_to_module_map_supply == None:
            file_to_module_map_supply = config_file_to_module_map_supply
        self.__logger = logging.getLogger(self.__module__)
        self.__outputter = outputter
        self.__data_supply = data_supply

        self.__implementation_file_to_module_map = file_to_module_map_supply.get_implementation_file_to_module_map(use_implementation_mapping_exceptions)
        #self.__implementation_files = set(self.__implementation_file_to_module_map.keys())
        self.__implementation_file_basename_to_files = dict()
        for filename in self.__implementation_file_to_module_map.keys():
            basename = posixpath.basename(filename)
            if basename not in self.__implementation_file_basename_to_files:
                self.__implementation_file_basename_to_files[basename] = []
            self.__implementation_file_basename_to_files[basename].append(filename)
        self.__default_modules_per_dir = self.__data_supply.get_module_rootdirs()
        self.__headers_in_module_specs = self.__init_headers_in_module_specs(file_to_module_map_supply)
        self.__external_include_dir_mapper = get_default_include_path_mapping()

    def __init_headers_in_module_specs(self, file_to_module_map_supply):        
        headers_in_module_specs = CollectionTools.transpose_items_as_dict(file_to_module_map_supply.get_module_to_header_file_map())
        duplicate_headers = CollectionTools.find_duplicates(value for (key, value) in file_to_module_map_supply.get_module_to_header_file_map())
        self.__logger.info("%i headers in module specs, ignoring %i duplicates" % (len(headers_in_module_specs), len(duplicate_headers)))
        for header in duplicate_headers:
            del headers_in_module_specs[header]
        return headers_in_module_specs

    def outputter(self):
        return self.__outputter
        
    @staticmethod
    def __implementation_files_for_header(header_filename):
        (basename, _ext) = posixpath.splitext(header_filename)
        return [basename + ext for ext in config_cpp_file_configuration.get_implementation_file_extensions()]

    def __try_otherdir(self, header_filename):
        # TODO statt endswith os.path.basename verwenden
        match = []
        for name in self.__implementation_files_for_header(posixpath.basename(header_filename)):
            if name in self.__implementation_file_basename_to_files:
                match += self.__implementation_file_basename_to_files[name]
        #match = [filename 
        #         for filename in self.__implementation_files 
        #         if filename.endswith((c_name, cpp_name))]
        if len(match) > 0:
            if len(match) > 1:
                self.__logger.warning("skipping directory match, ambiguous for %s: %s" % (header_filename, match))
                return False
            self.__outputter.add_module_map(self.__implementation_file_to_module_map[match[0]], header_filename)
            return True
        else:
            return False
       

    def _implementation_file_candidates_same_module(self, header):
        return self.__implementation_files_for_header(header)

    def __try_same_module(self, header):
        self.__logger.info("def __try_same_module for %s"%str(header))
        for implementation_file_candidate in self._implementation_file_candidates_same_module(header):
            #TODO: Unschoener Workaround! Warum sind die Eintraege in module_to_implementationfiles lowercase?
            #try:
            #    implementation_file_candidate = implementation_file_candidate.lower()
            #except AttributeError:
            #    pass
            self.__logger.info("implementation_file_candidate %s"%str(implementation_file_candidate))
            if implementation_file_candidate in self.__implementation_file_to_module_map:
                self.__outputter.add_module_map(self.__implementation_file_to_module_map[implementation_file_candidate], header)
                return True
        return False
    
    # TODO is_top_level_dir und _get_best_dir sollten in eigene Klasse ClosestDirMatcher
    
    top_level_dirs = set(['.'])
    def _is_top_level_dir(self, directory):
        return directory in self.top_level_dirs 
    
    def _get_default_module(self, directory):
        if directory in self.__default_modules_per_dir:
            return self.__default_modules_per_dir[directory]
        else:
            return None

    def _get_best_dir_module(self, header):
        assert not os.path.isabs(header), "called with absolute path (%s)" % header
        start_directory = os.path.dirname(header) 
        directory = start_directory
        while not (self._is_top_level_dir(directory) or len(directory) == 0):
            default_module = self._get_default_module(directory)
            if default_module != None:
                # Fallback to default project in the directory
                if directory != start_directory:
                    self.__default_modules_per_dir[start_directory] = default_module 
                return default_module
            else:
                # Fallback to default project in the directory above
                #directory = PathTools.unix_normpath(os.path.join(directory, os.path.pardir))
                # TODO prüfen, ob das so auch funktioniert
                directory = posixpath.dirname(directory)
        return None

    def __try_bestdir(self, header):
        bestdir_module = self._get_best_dir_module(header)
        if bestdir_module != None:
            #self.__logger.debug("directory %s matched for %s" % (bestdir, header, ))
            self.__outputter.add_module_map(bestdir_module, header)
            return True
        else:
            return False

    def _ignore_file(self, header):
        return False
    
    def _ignore_module_spec_for_file(self, header):
        return False

    # TODO statt speziell diese Reihenfolge festzulegen, sollte es eine Funktion geben, die für 
    # jeden Header die Reihenfolge der Prüfungen zurück gibt 
    def _try_other_dir_first_for_file(self, header):
        return False

    def __external_match(self, header):
        if os.path.isabs(header):
            # TODO es können auch relative Pfade sein, diese müssen dann aber erst in absolute 
            # umgewandelt werden bzw. die Pfade in der __external_include_dir_map müssen ggf. in 
            # relative Pfade umgewandelt werden 
            external_module = self.__external_include_dir_mapper.find_module_for_header(header)
            if external_module != None:
                self.__outputter.add_module_map(external_module, header)
                return True
        return False


    def link_header(self, header, stats=HeaderLinkerStatistics()):
        # TODO allgemein prüfen, ob Verzeichnis zu den Quellverzeichnissen gehört
        if os.path.isabs(header):
            if self.__external_match(header):
                stats._external_files_match += 1
            else:
                self.__logger.info("no match for external header %s", header)
                stats._external_files_nomatch += 1
            return
        if self._ignore_file(header):
            stats._ignored_files += 1
            return
        if self.__try_same_module(header):
            stats._file_matches_samemoduledir += 1
        elif self._try_other_dir_first_for_file(header) \
             and self.__try_otherdir(header):
            stats._file_matches_otherdir += 1
        elif header in self.__headers_in_module_specs and not self._ignore_module_spec_for_file(header):
            self.__logger.debug("module spec %s matched for %s" % (self.__headers_in_module_specs[header], header))
            self.__outputter.add_module_map(self.__headers_in_module_specs[header], header)
            stats._module_spec_matches += 1
        elif self.__try_bestdir(header):
            stats._dir_matches += 1
        else:
            self.__logger.info("no module for %s" % (header))
            self.__outputter.add_module_map(None, header)
            stats._no_matches += 1 # try default module in directory


    def link_all_headers(self, header_list):
        # TODO link_all_headers und output trennen; man könnte intern den DictOutputter verwenden

        stats = HeaderLinkerStatistics()
        for header in header_list:
            self.link_header(header=header, stats=stats)
        self.__outputter.write()
                
        self.__logger.info(("%i impl file matches (same module dir), "+
                           "%i impl file matches (other module dir), "+
                           "%i module spec (e.g. vcproj) matches, "+
                           "%i dir matches, %i not matched, %i files ignored, "+
                           "%i external matched, %i external not mached") % 
                     (stats._file_matches_samemoduledir,
                      stats._file_matches_otherdir,
                      stats._module_spec_matches,
                      stats._dir_matches,
                      stats._no_matches,
                      stats._ignored_files,
                      stats._external_files_match,
                      stats._external_files_nomatch,
                      ))
        if stats.sum() != len(header_list):
            self.__logger.error("Sum of processed (%i) does not equal total number of files (%i)" % (stats.sum(), len(header_list)))

    def _get_headers_in_module_specs(self):
        return self.__headers_in_module_specs

if __name__ == "__main__":
    import doctest
    doctest.testmod()
