'''
Created on 10.06.2011

@author: SIGIESEC

TODO this was copied from cpp.csharp.vcxproj_modules and has probably lots of duplication!
'''
from base.basic_config_if import BasicConfig
from base.modules_base import BaseModuleListSupply
from base.modules_if import (ModuleListSupplyEx, SourceFileSupply, 
    SolutionFileSupply, RuleSupply)
from commons.config_if import ConfigDependent
from commons.core_util import StringTools
from cpp.msvc.parse_sln_internal import InternalSolutionFileParser
from cpp.msvc.vcxproj_parser import VSConstants, VCXProjParser, VCXProjParserTools
import logging
import os

class VCXProjModuleListSupply(BaseModuleListSupply, ModuleListSupplyEx, ConfigDependent, SourceFileSupply, SolutionFileSupply, RuleSupply):
    # TODO the setters should be removed. the design should be changed in a way that these are not necessary
    
    def __init__(self, basic_config=BasicConfig(), *args, **kwargs):
        BaseModuleListSupply.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__module_files_to_names = dict()
        self.__modules_to_files = dict()
        self.__basic_config = basic_config
        # TODO the project file base dir might not be equal to the local source base dir when project files 
        # are generated (as it is already the case for C++/cmake)
        self.__project_dir_resolver = basic_config.get_local_source_resolver()
        self.__analysis_base_dirs = basic_config.get_local_source_base_dir_subset()
        self.__diagnostics = dict()
        self.__module_diagnostics = None
        self.__modules_in_solution_files = dict()
        self.__source_files = dict()
        self.__global_results = list()
        self.__initialized = False
        self.__checked_rules = None
        self.__source_file_results = list()
        
    def __ensure_initialized(self):
        if not self.__initialized:
            self.__initialize()
            self.__initialized = True
        
    def __initialize(self):
                # TODO when more than one base path exists, it does not make sense to create all combinations, 
                # there must be some way to specify which subset belongs to which base dir. Currently, this
                # is not required for any application.
        for base_path in self.__project_dir_resolver.get_base_paths():
            for subset in self.__analysis_base_dirs:
                directory = os.path.normpath(os.path.join(base_path, subset))
                self.__logger.info("Parsing .vcxproj files in %s" % directory)
                os.path.walk(directory, self.__walk, None)

    def get_files_for_module(self, module):
        self.__ensure_initialized()
        return self.__modules_to_files[module]
        
        # TODO the following does not work easily, since the dependency resolution is based on assembly names...
#        names = list()
#        try:
#            (basename, _ext) = os.path.splitext(os.path.basename(parser.get_filename()))
#            names.append(basename)
#        except ValueError:
#            pass
#        try:
#            names.append(parser.get_assembly_name())
#        except ValueError:
#            self.__logger.warning(".vcxproj file %s does not declare an assembly name" % (parser.get_filename()), exc_info=1)
#        try:
#            names.append(parser.get_root_namespace())
#        except ValueError:
#            self.__logger.info(".vcxproj file %s does not declare a root namespace" % (parser.get_filename()), exc_info=1)
#        return sorted(names, key=lambda x: -len(x))[0]
    

    def __to_rel_to_project_root_path(self, abspath):
        """
        Converts an absolute path to a path relative to the project's base path.
        
        @param abspath: an absolute path
        @type abspath: basestring
        
        @rtype: str or unicode (depending on type(abspath))        
        """
        # TODO this should use self.__project_dir_resolver instead, since BasicConfig.get_local_source_base_dir() is deprecated
        # TODO a utility function should be added to commons.os_util which does this in general for an absolute path and a LocalPathResolver
        # TODO is it guaranteed that the string returned by get_local_source_base_dir never ends with os.path.sep?  
        return StringTools.strip_prefix(abspath, self.__basic_config.get_local_source_base_dir() + os.path.sep)

    def __walk(self, _arg, dirname, filenames):
        for filename in filenames:
            if filename.endswith(VSConstants.VCXPROJ_EXTENSION):
                fullname = os.path.join(dirname, filename) 
                self.__logger.info("Parsing .vcxproj file %s" % fullname)
                parser = VCXProjParser(fullname)
                self.__module_files_to_names[fullname] = VCXProjParserTools.get_best_name(parser, self.__project_dir_resolver)
                self.__modules_to_files[self.__module_files_to_names[fullname]] = tuple(parser.get_source_files())
                #checker = config_vcxproj_checker_class(parser)
                #self.__diagnostics[fullname] = list(checker.get_irregularities())
            """
            Creates a dict with all given solutionfiles which are mapped to the
            list of projects which are defined in it. This mapping is needed for
            better tracebility e.g. for the output when a project is defined in 
            two different solutionfiles.
            """
            if filename.endswith(VSConstants.MSVC_EXTENSION):
                fullname = os.path.join(dirname, filename)
                self.__logger.info("Parsing .sln file %s" %fullname)             
                parser = InternalSolutionFileParser(open(fullname))
                relative_name = self.__to_rel_to_project_root_path(fullname)
                self.__modules_in_solution_files[relative_name] = tuple(parser.vcprojs())
            """
            Creates a dict with all source files in the analyzed directories
            """
            if filename.endswith(VSConstants.SOURCE_EXTENSION):
                relative_dir_name = self.__to_rel_to_project_root_path(dirname)
                relative_name = os.path.join(relative_dir_name, filename)
                self.__source_files[relative_name] = (relative_dir_name, filename)
                
    def get_modules_in_solution_files(self):
        """
        Returns a dict with all given solutionfiles which are mapped to the
        list of projects which are defined in it. This mapping is needed for
        better tracebility e.g. for the output when a project is defined in 
        two different solutionfiles.
        """
        self.__ensure_initialized()
        return self.__modules_in_solution_files

    def get_source_files(self):
        self.__ensure_initialized()
        return self.__source_files
                
    def get_module_list(self):
        self.__ensure_initialized()
        return self.__module_files_to_names.itervalues()
    
    def get_module_spec_files(self):
        self.__ensure_initialized()
        for rel_filename in self.__module_files_to_names.iterkeys():
            yield self.__project_dir_resolver.resolve(rel_filename)

    def __get_relative_name(self, absolute_name):
        resource = self.__project_dir_resolver.resolve(absolute_name)
        return os.path.relpath(resource.name(), resource.get_resolution_root())
        
    def get_module_descriptors(self):
        self.__ensure_initialized()
        for (absolute_name, modulename) in self.__module_files_to_names.iteritems():
            yield (self.__get_relative_name(absolute_name), modulename)
            
    #def get_module_diagnostics(self):
    #    self.__ensure_initialized()
    #    if not self.__module_diagnostics:
    #        self.__module_diagnostics = list()
    #        for (absolute_name, diagnostics) in self.__diagnostics.iteritems():
    #            self.__module_diagnostics.append((self.__get_relative_name(absolute_name), diagnostics))
    #    return self.__module_diagnostics        

    def set_source_file_results(self, source_file_result):
        # TODO this is never called. it should be removed
        self.__source_file_results = source_file_result
        
    def get_source_file_results(self):        
        # TODO this is never called. it should be removed
        # TODO why is self.__ensure_initialized called?
        self.__ensure_initialized() 
        return self.__source_file_results
    
    def set_results(self, global_results):
        self.__global_results = tuple(global_results)
        
    def get_results(self):
        # TODO why is self.__ensure_initialized called?
        self.__ensure_initialized()
        return self.__global_results 

    def set_checked_rules(self, checked_rules):
        self.__checked_rules = tuple(checked_rules)
        
    def get_checked_rules(self):
        # TODO why is self.__ensure_initialized called?
        self.__ensure_initialized()
        return self.__checked_rules
                                   
    def __str__(self):
        if self.__initialized:
            return "%s(modules=%s)" % (self.__class__.__name__, ", ".join(self.get_module_list()))
        else:
            return "%s(<uninitialized)" % (self.__class__.__name__)
        
        
