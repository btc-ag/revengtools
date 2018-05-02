# -*- coding: UTF-8 -*-

'''
Created on 25.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.diagnostics_if import ModuleCheckerParameterKeys, CheckerParameterKeys, TechnologyTypes
from base.diagnostics_util import CheckerRuleFactory, CheckerRunner
from base.modules_base import BaseModuleListSupply
from base.modules_if import ModuleListSupplyEx, SolutionFileSupply, RuleSupply
from commons.config_if import ConfigDependent
from commons.core_util import frozendict, SetValuedDictTools
from commons.os_util import NormalizedPathsIter, PathTools
from cpp.cpp_if import FileToModuleMapSupply
from cpp.msvc.msvc_supply_if import MSVCDataSupply
from itertools import imap
import logging
import os.path
import posixpath
import sys

config_basic = BasicConfig()
config_file_to_module_map_supply = FileToModuleMapSupply()
config_checker_rule_factory_class = CheckerRuleFactory

vcproj_names = frozendict({ModuleCheckerParameterKeys.BINARY_BASENAME: "build target name",
                           ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: "CMakeLists.txt directory",
                           ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: "root directory of source files",
                           ModuleCheckerParameterKeys.SOURCE_FILES: "implementation files",
                           #ModuleCheckerParameterKeys.ROOT_NAMESPACE: "root namespace",
                           }
                          )


class FileMSVCDataSupply(MSVCDataSupply, BaseModuleListSupply, ModuleListSupplyEx, ConfigDependent, SolutionFileSupply, RuleSupply):

    def __init__(self, *args, **kwargs):
        MSVCDataSupply.__init__(self, *args, **kwargs)
        BaseModuleListSupply.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__module_to_vcproj_map = None
        self.__module_to_file_map = None
        self.__module_to_txt_map = None
        self.__module_list = None
        self.__project_dir_resolver = config_basic.get_local_source_resolver()
        self.__analysis_base_dirs = config_basic.get_local_source_base_dir_subset()
        self.__checker = self.__create_checker()
        self.__module_checker_parameter = None
        self.__checked_rules = list()
        self.__initializied = False
        self.__results = None
        
    def __create_checker(self):
        return CheckerRunner(rules=config_checker_rule_factory_class(parameter_user_names=vcproj_names, module_specification_file_extensions=[".vcproj"]).all_rules(technology=TechnologyTypes.CPP))
    
    def get_vcproj_list_filename(self):
        return os.path.join(config_basic.get_results_directory(), "vcprojs-from-sln")

    def get_module_to_vcproj_map_filename(self):
        return os.path.join(config_basic.get_results_directory(), "module_to_vcprojfiles")

    def get_module_to_txt_map_filename(self):
        return os.path.join(config_basic.get_results_directory(), "module_to_txtfiles")

    def __get_module_to_vcproj_map(self):
        # TODO das gibt letztlich eine item iterator zurück
        if self.__module_to_vcproj_map == None:
            self.__module_to_vcproj_map = dict(NormalizedPathsIter.create(filename=self.get_module_to_vcproj_map_filename(),
                                                                    delimiter=':',
                                                                    what="module name to .vcproj map"))
        return self.__module_to_vcproj_map

    def __get_module_to_txt_map(self):
        # TODO das gibt letztlich eine item iterator zurück
        if self.__module_to_txt_map == None:
            self.__module_to_txt_map = SetValuedDictTools.convert_from_itemiterator(NormalizedPathsIter.create(filename=self.get_module_to_txt_map_filename(),
                                                                    delimiter=':',
                                                                    what="module name to .txt map"))
        return self.__module_to_txt_map


    def get_module_to_vcproj_map(self):
        return self.__get_module_to_vcproj_map().iteritems()
    
    def get_module_descriptors(self):
        self.__ensure_initializied()
        for (modulename, _filename) in self.get_module_to_vcproj_map():
            yield (self.get_cmakelists_file_safe(modulename), modulename)

    def __get_relative_name(self, absolute_name):
        # TODO duplicates csproj_modules.CSharpModuleListSupply
        resource = self.__project_dir_resolver.resolve(absolute_name)
        return os.path.relpath(resource.name(), resource.get_resolution_root())

    def get_cmakelists_file(self, module_name):
        cmakelists = filter(lambda x: posixpath.basename(x).lower()=='CMakeLists.txt'.lower(), self.__get_module_to_txt_map()[module_name])
        if len(cmakelists) != 1:
            msg = "No or multiple CMakeLists.txt found for module %s: %s" % (module_name, cmakelists)            
            raise ValueError(msg)
        return PathTools.canonicalize_capitalization(self.__project_dir_resolver.resolve(cmakelists[0]).name())    
    #TODO: Gehoeren die Ausnahmen hier rein?
    CHECK_EXCEPTIONS=set(["ALL_BUILD", "ZERO_CHECK"])
    
    @staticmethod
    def __trim_after(string, trim_after):
        pos = string.rfind(trim_after)
        if pos != -1:
            return string[:pos+len(trim_after)]
        else:
            return string
        
    @staticmethod  
    def __get_filename(fullname):
        splitted_fullname = os.path.normpath(fullname).split(os.path.sep)
        return splitted_fullname[len(splitted_fullname)-1]
                
    def __check(self, module_name, fullname):
        if module_name in self.CHECK_EXCEPTIONS:
            return ()
        try:
            specfile_path = self.get_cmakelists_file(module_name)
        except:
            specfile_path = fullname
        specfile_dir_transformed = os.path.dirname(specfile_path.replace(posixpath.sep, os.path.sep))
        #Nina wants to have some feedback in the console to see the process is still alive
        print >>sys.stderr, "parsing %s"%(fullname)    
        # the directory of the .vcproj does not matter for cmake-generated files, since it might be generated into a mangled directory name to avoid paths that are too long
        module_files = list(self.get_files_for_module(module_name))
        common_base_dir = PathTools.common_base_directory(module_files)
        data = dict({ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: self.__analysis_base_dirs,
                     ModuleCheckerParameterKeys.BINARY_BASENAME: module_name,
                     ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: self.__get_relative_name(specfile_dir_transformed),
                     ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME: self.__trim_after(self.__get_relative_name(common_base_dir), "src") if common_base_dir else None,
                     ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: self.__get_filename(specfile_path),
                     ModuleCheckerParameterKeys.SOURCE_FILES: module_files,
                     #ModuleCheckerParameterKeys.ROOT_NAMESPACE: root_namespace,
                     })
        self.__logger.info("Module Data for %s: "%fullname + str(data))
        self.__module_checker_parameter[fullname] = data        
    
    def get_cmakelists_file_safe(self, module_name):
        try:
            return self.__get_relative_name(self.get_cmakelists_file(module_name))
        except:
            self.__logger.warning("cannot determine CMakeLists.txt for %s" % (module_name, ), exc_info=1)
            return "unknown CMakeLists.txt for module %s" % (module_name,)        

    def __ensure_initializied(self):
        if not self.__initializied:
            self.__module_checker_parameter = dict()
            for (module_name, fullname) in self.__get_module_to_vcproj_map().iteritems():
                self.__check(module_name, fullname)  
            self.__initializied = True
                
    def get_checker_information(self):
        self.__ensure_initializied()
        checker_information = dict()
        checker_information[CheckerParameterKeys.MODULE_CHECKER_PARAMETER] = self.__module_checker_parameter
        return checker_information
        
    def get_results(self):
        #if not self.__module_checker_parameter:
        #    self.__logger.critical("No diagnostic results before starting the global analyze")
        if self.__results == None:
            self.__logger.info("Data in cpp:")
            self.__logger.info(self.get_checker_information())
            self.__results = list(self.__create_checker().check(self.get_checker_information()))
            return self.__results
        else:
            return self.__results
        
    def get_vcproj_list(self):
        # TODO das ist keine richtige Liste, sondern ein Iterator über Tupel
        return NormalizedPathsIter.create(filename=self.get_vcproj_list_filename(), 
                                          what="list of .vcproj files referenced in .sln")

    def get_module_list(self):
        if self.__module_list == None:
            self.__module_list = set(key for (key, _value) in self.get_module_to_vcproj_map())
        return self.__module_list


    def is_module_available(self, module):
        return module in self.__get_module_to_vcproj_map()

    def is_module_empty(self, module):
        return module not in self.__get_module_to_file_map()


    def __get_module_to_file_map(self):
        file_to_module_map_supply = config_file_to_module_map_supply
        if self.__module_to_file_map == None:
            self.__module_to_file_map = file_to_module_map_supply.generate_module_to_file_map(True)
        return self.__module_to_file_map

    def get_files_for_module(self, module):
        file_to_module_map_supply = config_file_to_module_map_supply
        if module in self.__get_module_to_file_map():
            return map(self.__get_relative_name, 
                       imap(PathTools.canonicalize_capitalization, 
                            (self.__project_dir_resolver.resolve(filename).name() for filename in self.__get_module_to_file_map()[module])))
        else:
            if module.startswith('_'):
                # TODO PRINS-specific?
                return ()
            else:
                if not self.is_module_available(module):
                    self.__logger.warning("Unknown module %s in %s, perhaps out-of-date?" % (module, self.get_module_to_vcproj_map_filename()))
                else:
                    self.__logger.info("No files for module %s in %s, perhaps out-of-date?" % (module, str(file_to_module_map_supply)))
                return ()
            
    def get_checked_rules(self):
        return self.__checker.get_rule_information()
        
#    def release_file_list(self):
#        self.__logger.debug("release_file_list called")
#        self.__module_to_file_map = None

