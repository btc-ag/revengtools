#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Contains utilities around C{base.diagnostics_if}, and implementations of module diagnostics rules.  

Created on 25.05.2012

@author: SIGIESEC
'''
from base.diagnostics_if import (CheckerRule, CheckerParameterKeys, 
    DiagnosticResult, ModuleCheckerParameterKeys, CheckerRuleFactory, DiagnosticDescription,
    DiagnosticSubjectTypeParameterKeys, CheckerRuleType, TechnologyTypes)
from functools import partial
from itertools import combinations, chain, ifilter
from commons.core_util import StringTools, IterTools
import difflib
import logging
import os.path
import warnings

class RuleUtil(object):
    @staticmethod
    def get_dirname_parts(dirname, delete_build = False):
        splitted_dirname = os.path.normpath(dirname).split(os.path.sep)
        if delete_build and splitted_dirname[len(splitted_dirname)-1]=="build":
            return splitted_dirname[:len(splitted_dirname)-1]
        else:
            return splitted_dirname
    
    @staticmethod
    def get_dirname(dirname, delete_build = False):
        dirname = os.path.normpath(dirname)
        if dirname.endswith("build"):
            return StringTools.strip_suffix(dirname, "".join((os.path.sep, "build")))
        else:
            return dirname
        
    @staticmethod
    def get_module_name(data):
        try:
            specification_dir_name = data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME]
        except:
            specification_dir_name = None
        
        try:
            specification_base_name = data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME]
        except:
            specification_base_name = None
        
        if specification_dir_name and specification_base_name:
            return os.path.sep.join((specification_dir_name,
                                     specification_base_name))
        elif specification_dir_name:
            return specification_dir_name
        return "<undefined>"
    
    @staticmethod
    def highlight(first, second, startDiffMark="{b}", endDiffMark="{/b}"):
        s = difflib.SequenceMatcher(None, first, second)
        firstRes = ""
        secondRes = ""
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag in ['delete', 'replace']:
                firstRes += startDiffMark
            if tag in ['insert', 'replace']:
                secondRes += startDiffMark
            firstRes += first[i1:i2]
            secondRes += second[j1:j2]                
            if tag in ['delete', 'replace']:
                firstRes += endDiffMark
            if tag in ['insert', 'replace']:
                secondRes += endDiffMark
                
        return (firstRes, secondRes) 

class CheckerRunner(CheckerRule):
    """
    Implements a composite rule.
    """
    
    def __init__(self, rules):
        self.__rules = list(rules)
        self.__logger = logging.getLogger(self.__class__.__module__)
        
    def check(self, data):
        self.__logger.info("checking rules for data %s" % CheckerUtil.format_data(data))
        return (chain.from_iterable(rule.check(data) for rule in self.__rules))

    def get_rule_information(self):
        return (rule.get_diagnostic_description() for rule in self.__rules)

class CheckerUtil(object):    
    @staticmethod
    def format_data(data):
        return (", ".join("%s=%s" % (key,value) for (key,value) in data.iteritems()))          
            
            
class CheckerRuleBase(CheckerRule):
    """
    An abstract base class intended to simplify the implementation of most module checker rules.
    
    The most simple implementations will only override _rule_core
    """
    def __init__(self, rule_type, parameter_user_names, required_parameter_keys=(), rulename=None):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.info("Initializing %s" %self.__class__)
        self.__rule_type = rule_type
        self.__parameter_user_names = dict(parameter_user_names)
        self.__required_parameter_keys = required_parameter_keys
        # TODO check whether the required parameter keys are contained in parameter_user_names?
        if rulename:
            self.__rulename = rulename
        else:
            self.__rulename = self.__class__.__name__
        
    def _get_parameter_user_name(self, key):
        """
        Maps a parameter key (key of the data parameter of check and _rule_core) to a human-readable description.
        
        Not intended to be overridden by subclasses.
        """
        return self.__parameter_user_names.get(key, key)
    
    def _precondition(self, data):
        """
        Checks if the _rule_core of this class will be able to perform its checks. The default implementation
        checks whether the required parameter keys are set in the input data. 
        
        @rtype: Boolean
        
        Intended to be overridden by subclasses if specialized behaviour is required. Subclasses may call 
        this method and _get_parameter_user_name.
        """
        # TODO also check whether the values of the required parameter keys are non-null?
        if not all(key in data for key in self.__required_parameter_keys):
            self.__logger.info("Skipping rule %s because %s is not in the data %s."%(str(self.__class__.__name__),str(self.__required_parameter_keys), str(data)))
        return all(key in data for key in self.__required_parameter_keys)
    
    def _rule_core(self, data):
        """
        The expected behaviour of this method is equivalent to ModuleCheckerRule.check. However, its implementation
        may assume that the _precondition is satisfied (and does not need to make those checks again). 
        
        Must be implemented by subclasses. Subclasses may call _get_parameter_use_name.
        
        @return: Has to return an iterable object of Result Diagnostics e.g. via yield.  
        """
        raise NotImplementedError(self.__class__)
    
    def check(self, data):
        """
        First checks the _precondition and, if it is satisfied, executes _rule_core. If the 
        _precondition is not satisfied, no checks are performed and no diagnostics are produced.
        
        TODO produce some debug diagnostic if precondition is not satisfied 
        
        @see: ModuleCheckerRule.check
        
        Not intended to be overridden by subclasses. Must never be called from subclasses.
        """
        if self.__rule_type == CheckerRuleType.MODULE_RULE:
            #return (chain.from_iterable(rule.check(data) for rule in self.__rules))
            return (chain.from_iterable(self.__check_per_dataset(data)))
        else:
            if self._precondition(data):
                return self._rule_core(data)
            else:
                self.__logger.debug("Skipping rule %s: precondition is not satisfied for data = %s" % (self.__rulename, CheckerUtil.format_data(data)))
            return ()

    def __check_per_dataset(self, data):
        for dataset in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            if self._precondition(data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][dataset]):
                yield self._rule_core(data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][dataset])
            else:
                self.__logger.debug("Skipping rule %s: precondition is not satisfied for data = %s" % (self.__rulename, CheckerUtil.format_data(data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][dataset])))
                
    def get_diagnostic_description(self):
        raise NotImplementedError(self.__class__)            
        
        
class HasParameterRule(CheckerRuleBase):
    """
    Checks if the parameters, with which the class was initialized, are set.
    """
    def __init__(self, parameter_key, *args, **kwargs):
        CheckerRuleBase.__init__(self, rule_type = CheckerRuleType.MODULE_RULE, *args, **kwargs)
        self.__parameter_key = parameter_key
        self.__level = logging.WARNING
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules without %s"%self._get_parameter_user_name(self.__parameter_key),
                description = "This rule checks whether the module has the parameter %s or not."%self._get_parameter_user_name(self.__parameter_key),
                subject_type = self.__subject_type,
                example = [("CoreAssetBase\\BTC\\ERP\\DotNet\\SAP\\TEO\\Proxies\\SapNetProxies\\SapNetProxies.csproj", "WARNING: Module has no root namespace")],
                documentation_link = "no documentation so far")
    
    def _rule_core(self, data):
        if not data.get(self.__parameter_key, None):
            yield DiagnosticResult(level=self.__level,
                                    message="Module has no %s" % (self._get_parameter_user_name(self.__parameter_key)),
                                    diagnostic_description = self.__diagnostic_description,
                                    subject = RuleUtil.get_module_name(data),
                                    subject_type = self.__subject_type) 

    def get_diagnostic_description(self):
        return self.__diagnostic_description
    

class HasAssemblyNameRule(HasParameterRule):
    """
    Checks if the binary basename is set.
    """
    def __init__(self, *args, **kwargs):
        HasParameterRule.__init__(self, parameter_key=ModuleCheckerParameterKeys.BINARY_BASENAME, *args, **kwargs)


class HasRootNamespaceNameRule(HasParameterRule):
    """
    Checks if the root namespace is set.
    """
    def __init__(self, *args, **kwargs):
        HasParameterRule.__init__(self, parameter_key=ModuleCheckerParameterKeys.ROOT_NAMESPACE, *args, **kwargs)


class ParametersMatchRule(CheckerRuleBase):
    def __init__(self, parameter_user_names, key_transform_pairs, required_parameter_keys=(), *args, **kwargs):
        CheckerRuleBase.__init__(self, 
                                       rule_type = CheckerRuleType.MODULE_RULE,
                                       parameter_user_names=parameter_user_names, 
                                       required_parameter_keys=(), 
                                       *args, **kwargs)
        self.__key_transform_pairs = key_transform_pairs
        self.__level = logging.WARNING
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE_SPECIFICATION_FILE
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules where parameters do not match",
                description = "This rule checks whether parameters match to each other.",
                subject_type = self.__subject_type,
                example = [("CoreAssetBase\\BTC\\Geometry\\DotNet\\GML2RIM\\build\\BTC.CAB.Geometry.GML2RIM.csproj", "WARNING: assembly name (BTC.CAB.Geometry.GML2RIM) does not match root namespace (BTC.Geometry.GML2RIM)")],
                documentation_link = "no documentation so far")
        
    def _rule_core(self, data):
        for ((key1, transformation1), (key2, transformation2)) in combinations(self.__key_transform_pairs, 2):
            if key1 in data and key2 in data and transformation1(data[key1]) != transformation2(data[key2]):
                (highlightedValue1, highlightedValue2) = RuleUtil.highlight(data[key1], data[key2])
                yield DiagnosticResult(level=self.__level,
                                    message="%s (%s) does not match %s (%s)" 
                                        % (self._get_parameter_user_name(key1), transformation1(highlightedValue1),
                                           self._get_parameter_user_name(key2), transformation2(highlightedValue2)),
                                    diagnostic_description = self.__diagnostic_description,
                                    subject = RuleUtil.get_module_name(data),
                                    subject_type = self.__subject_type)  
    
    def get_diagnostic_description(self):
        return self.__diagnostic_description
                 
                        
class DefaultParameterMatchRule(ParametersMatchRule):
    @staticmethod
    def DEFAULT_SPECIFICATION_FILE_TRANSFORMATION(filename):
        return os.path.splitext(filename)[0]
    
    def __init__(self, module_specification_file_extensions, module_specification_file_transformation=None, *args, **kwargs):
        if not module_specification_file_transformation:
            module_specification_file_transformation = self.DEFAULT_SPECIFICATION_FILE_TRANSFORMATION
        self.__module_specification_file_extensions = module_specification_file_extensions
        ParametersMatchRule.__init__(self, key_transform_pairs=((ModuleCheckerParameterKeys.BINARY_BASENAME, lambda x: x),
                                                                (ModuleCheckerParameterKeys.ROOT_NAMESPACE, lambda x: x),
                                                                (ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME, module_specification_file_transformation),
                                                                ), *args, **kwargs)
                
    def _precondition(self, data):
        return ParametersMatchRule._precondition(self, data) and \
            (not ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME in data or 
             any(data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME].endswith(ext) 
                 for ext in self.__module_specification_file_extensions))
    

class HierarchicalNameRule(CheckerRuleBase):
    """
    Checks if the BINARY_BASENAME has at least 3 parts.
    """
    def __init__(self, *args, **kwargs):
        CheckerRuleBase.__init__(self, rule_type = CheckerRuleType.MODULE_RULE, required_parameter_keys=[ModuleCheckerParameterKeys.BINARY_BASENAME], *args, **kwargs)
        self.__level = logging.WARNING
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules with too short %s"%(self._get_parameter_user_name(ModuleCheckerParameterKeys.BINARY_BASENAME)),
                description = "Checks whether the %s has at least 3 parts."%(self._get_parameter_user_name(ModuleCheckerParameterKeys.BINARY_BASENAME)),
                subject_type = self.__subject_type,
                example = [("CoreAssetBase\\BTC\Identity\\build\\PostBuilder\\PostBuilder.csproj", "WARNING: %s (PostBuilder) has less than 3 parts (BTC.xyz.abc)"%(self._get_parameter_user_name(ModuleCheckerParameterKeys.BINARY_BASENAME)))],
                documentation_link = "no documentation so far")
        
    def _rule_core(self, data):
        if "btc" in data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME].lower().split(os.path.sep) and \
                len(data[ModuleCheckerParameterKeys.BINARY_BASENAME].split(".")) < 3:
                yield DiagnosticResult(level=self.__level,
                                    message="%s (%s) has less than 3 parts (BTC.xyz.abc)" 
                                    % (self._get_parameter_user_name(ModuleCheckerParameterKeys.BINARY_BASENAME), 
                                       data[ModuleCheckerParameterKeys.BINARY_BASENAME], ),
                                    diagnostic_description = self.__diagnostic_description,
                                    subject = RuleUtil.get_module_name(data),
                                    subject_type = self.__subject_type) 

    def get_diagnostic_description(self):
        return self.__diagnostic_description
    
    
class ModuleSpecBelowSourceRootRule(CheckerRuleBase):
    """
    Checks if the rootdir is at the same level as the module specification
    """
    #TODO: Is this the expected behavior? The diagnostic result seems to
    #      intend something else.

    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        CheckerRuleBase.__init__(self, rule_type = CheckerRuleType.MODULE_RULE, required_parameter_keys=[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME, ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME], *args, **kwargs)
        self.__level = logging.WARNING
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules with inconsistent rootdir and module specification",
                description = "Checks whether the module specification file is in the root directory or in a folder named build or source, which is located in the root directory.",
                subject_type = self.__subject_type,
                example = [("extern\\cppunit-1.12.1\\build\\TestRunner ","WARNING: inconsistent CMakeLists.txt directory (extern\\cppunit-1.12.1\\build\\TestRunner), expected above or beside root directory of source files (extern\\cppunit-1.12.1\\src) ")],
                documentation_link = "no documentation so far")
        
    def _rule_core(self, data):
        if not data[ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME]:
            yield DiagnosticResult(level=self.__level,
                                    message="no %s (possible reason: module has no source files)" 
                                        % self._get_parameter_user_name(ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME),
                                    diagnostic_description = self.__diagnostic_description,
                                    subject = data[ModuleCheckerParameterKeys.BINARY_BASENAME],
                                    subject_type = self.__subject_type) 
        else:        
            transform = lambda x: os.path.normpath(os.path.normcase(x))
            # TODO better use os.path.samefile ?            
            #Posssible are any combinations of ('\', '\build) and ('\', '\src') 
            #if transform(data[ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME]) != transform(data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME]) and \
            #    transform(os.path.join(data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME], "build")) != \
            #    transform(os.path.join(data[ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME], "src")) and \
            #    transform(os.path.join(data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME], "build")) != \
            #    transform(data[ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME]) and \
            #    transform(data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME]) != \
            #    transform(os.path.join(data[ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME], "src")):
            source_root_dirname = transform(data[ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME])
            module_specification_file_dirname = transform(data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME])
            if module_specification_file_dirname.endswith("build"): # TODO this is not generic, but CAB(style)-specific
                module_specification_file_dirname = transform(os.path.join(module_specification_file_dirname,".."))    
            if source_root_dirname.endswith("src") or source_root_dirname.endswith("source"): # TODO this is not generic, but CAB(style)/PRINS-specific
                source_root_dirname = transform(os.path.join(source_root_dirname,".."))    
            if  source_root_dirname != module_specification_file_dirname: 
                            yield DiagnosticResult(level=self.__level,
                                    message="inconsistent %s (%s), expected above or beside %s (%s)" % 
                                            (self._get_parameter_user_name(ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME), 
                                             data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME], 
                                             self._get_parameter_user_name(ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME),
                                             data[ModuleCheckerParameterKeys.SOURCE_ROOT_DIRNAME]),
                                    diagnostic_description = self.__diagnostic_description,
                                    subject = data[ModuleCheckerParameterKeys.BINARY_BASENAME],
                                    subject_type = self.__subject_type) 
    
    def get_diagnostic_description(self):
        return self.__diagnostic_description
               
               
class FilesOutOfPlaceRuleBase(CheckerRuleBase):
    """
    Checks if all check_keys (Files, Modules,...) are in a basedirectory or a 
    subdirectory of a basedirectory or are defined as an exception.
    For all files, for which nothing is true, a message with informations is created.
    """ 
    def __init__(self, expected_base_dir_description, check_key, subject_type, required_parameter_keys=[], level=logging.ERROR, exceptions=[], example=[("","")], *args, **kwargs):
        CheckerRuleBase.__init__(self, 
                                       rule_type = CheckerRuleType.MODULE_RULE,
                                       required_parameter_keys=chain(required_parameter_keys, [check_key]),                                       
                                       *args, **kwargs)
        self.__expected_base_dir_description = expected_base_dir_description
        self.__check_key = check_key
        self.__level = level
        self.__subject_type = subject_type
        self.__exceptions = exceptions
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "%s outside of %s" %(self._get_parameter_user_name(self.__check_key), self._get_parameter_user_name(self.__expected_base_dir_description)),
                description = "Checks whether all %s are in the %s or in a subdirectory of the %s."%(self._get_parameter_user_name(self.__check_key),self._get_parameter_user_name(self.__expected_base_dir_description),self._get_parameter_user_name(self.__expected_base_dir_description)),
                subject_type = self.__subject_type,
                example = example,
                documentation_link = "no documentation so far")
        
    def _get_base_dirs(self, data):
        raise NotImplementedError(self.__class__)
          
        #TODO just the fifth line is tested by unitTests
    def __as_iterable(self, iter_or_string):
        if iter_or_string:
            if isinstance(iter_or_string, basestring):
                return (iter_or_string, )
            else:
                return iter_or_string
        else:
            # TODO is this the correct behaviour?
            return ()        
    
    def _rule_core(self, data):
        transform = lambda x: '' if x == '.' else os.path.normpath(os.path.normcase(x)) 
        expected_base_dirs = map(os.path.normpath, self._get_base_dirs(data))
        ignored_files = list(self.__exceptions)
        out_of_place_sourcefiles = list(sourcefile for sourcefile in self.__as_iterable(data[self.__check_key])
                                         if os.path.basename(sourcefile) not in ignored_files 
                                         and not any(transform(sourcefile).startswith(transform(expected_base_dir)) for expected_base_dir in expected_base_dirs))
        if len(out_of_place_sourcefiles):
            #yield DiagnosticResult(level=self.__level,
            #                       message="%s outside of %s (%s): %s" % (self._get_parameter_user_name(self.__check_key),
            #                                                            self.__expected_base_dir_description,
            #                                                            ", ".join(expected_base_dirs),
            #                                                            ", ".join(out_of_place_sourcefiles), ))
            if self.__subject_type == DiagnosticSubjectTypeParameterKeys.MODULE:
                subject = data[ModuleCheckerParameterKeys.BINARY_BASENAME]
            else:
                subject = RuleUtil.get_module_name(data)
            yield DiagnosticResult(level=self.__level,
                            message="%s outside of %s (%s): %s" % (self._get_parameter_user_name(self.__check_key),
                                                                        self.__expected_base_dir_description,
                                                                        ", ".join(expected_base_dirs),
                                                                        ", ".join(out_of_place_sourcefiles), ),
                            diagnostic_description = self.__diagnostic_description,
                            subject = subject,
                            subject_type = self.__subject_type) 
            
    def get_diagnostic_description(self):
        return self.__diagnostic_description                            
            
                            
class SourceFilesOutOfPlaceRuleBase(FilesOutOfPlaceRuleBase):
    def __init__(self, *args, **kwargs):
        FilesOutOfPlaceRuleBase.__init__(self, check_key=ModuleCheckerParameterKeys.SOURCE_FILES, 
                                         subject_type=DiagnosticSubjectTypeParameterKeys.MODULE_SPECIFICATION_FILE, *args, **kwargs)


class SourceFilesOutOfModuleRule(SourceFilesOutOfPlaceRuleBase):
    """
    Checks if there are Source Files outside of the Module.
    """
    def __init__(self, *args, **kwargs):
        SourceFilesOutOfPlaceRuleBase.__init__(self, 
                                       required_parameter_keys=[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME],
                                       expected_base_dir_description="assumed module base directory",
                                       example= [("CoreAssetBase\\BTC\\RTB2\\Base\\API\\NET\\BTC.CAB.RTB2.Base.API.NET.csproj", "ERROR: source files outside of assumed module base directory (CoreAssetBase\\BTC\\RTB2\\Base\\API\\NET): CoreAssetBase\\BTC\\RTB2\\VersionNET.cs ")], 
                                       *args, **kwargs)
        
    @classmethod
    def _get_base_dirs(cls, data):
        (head, tail) = os.path.split(data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME])
        if tail == "build":
            tail = ""
        # TODO strict: add "src"
        return (os.path.join(head, tail), )


class SourceFilesOutOfRepositoryRule(SourceFilesOutOfPlaceRuleBase):
    """
    Checks if there are Source Files outside of the Repository.
    """
    def __init__(self, *args, **kwargs):
        SourceFilesOutOfPlaceRuleBase.__init__(self, 
                                       required_parameter_keys=[ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS],
                                       expected_base_dir_description="analysis base directories", 
                                       example=[("extern\\cppunit-1.12.1\\build\\TestRunner\\CMakeLists.txt","ERROR: implementation files outside of analysis base directories: extern\\cppunit-1.12.1\\src\\msvc6\\testrunner\\ActiveTest.cpp")],                                           
                                       *args, **kwargs)
        
    @classmethod
    def _get_base_dirs(cls, data):
        return data[ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS]


class ContainedModulesOutOfRepositoryRule(FilesOutOfPlaceRuleBase):
    """
    Checks if there are Modules outside of the Repository.
    """
    def __init__(self, *args, **kwargs):
        FilesOutOfPlaceRuleBase.__init__(self, 
                                       check_key=ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME,
                                       required_parameter_keys=[ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS],
                                       subject_type=DiagnosticSubjectTypeParameterKeys.MODULE,
                                       expected_base_dir_description="analysis base directory",
                                       example=[("BTC.CAB.Test.CppUnit.TestRunner","ERROR: CMakeLists.txt directory outside of analysis base directory: extern\\cppunit-1.12.1\\build\\TestRunner")], 
                                       *args, **kwargs)
        
    @classmethod
    def _get_base_dirs(cls, data):
        return data[ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS]


class ModuleOutOfSolutionRule(CheckerRuleBase):
    """
    Checks if all modules are mapped to at least one solution.
    @param strict: Boolean - Should be examined caseSensitive? 
    """
    def __init__(self,strict=False,*args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__level = logging.WARNING
        self.__strict=strict
        CheckerRuleBase.__init__(self,
                                        rule_type = CheckerRuleType.GLOBAL_RULE,
                                        required_parameter_keys=[],
                                       *args, **kwargs)
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules not contained in any %s"%self._get_parameter_user_name(DiagnosticSubjectTypeParameterKeys.SOLUTION),
                description = "Checks whether all modules are contained in at least one %s."%self._get_parameter_user_name(DiagnosticSubjectTypeParameterKeys.SOLUTION),
                subject_type = DiagnosticSubjectTypeParameterKeys.MODULE,
                example = [("BTC.CAB.CIM.V12.Net.API", "WARNING: module specification file CoreAssetBase\\BTC\\CIM\\V12\\DotNet\\API\\BTC.CAB.CIM.V12.Net.API.csproj is not contained in any .sln file ")],
                documentation_link = "no documentation so far")

    def _rule_core(self, data):
        self.__logger.info("checking module out of solution rule")
        projects_in_solutionfiles = list()
        for solutionfile in data[CheckerParameterKeys.MODULES_IN_SOLUTIONS]:
                for project in data[CheckerParameterKeys.MODULES_IN_SOLUTIONS][solutionfile]:
                    project_fullpath = (os.path.normpath(os.path.join(solutionfile,os.path.pardir,project)))
                    projects_in_solutionfiles.append(project_fullpath)
        self.__logger.info("list of projects in solution files: " + str(projects_in_solutionfiles))
        for module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            module_information = (data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module])
            module_fullname = os.path.normpath(os.path.join(module_information[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME],
                                           module_information[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME]))
            if module_fullname not in projects_in_solutionfiles:
                self.__logger.info("module specification file %s is not contained in any .sln file" %module)
                yield DiagnosticResult(level=self.__level,
                            message="module specification file %s is not contained in any .sln file" %module,
                            subject = module_information[ModuleCheckerParameterKeys.BINARY_BASENAME],
                            diagnostic_description = self.__diagnostic_description,
                            subject_type = DiagnosticSubjectTypeParameterKeys.MODULE)         

    def get_diagnostic_description(self):
        return self.__diagnostic_description
    
    
class DuplicatedModulesRule(CheckerRuleBase):
    #TODO: Is similar to RedundantModulesInSolutionFiles. Should be
    #      generalized.
    def __init__(self, count_distinct_files_func=len, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__level = logging.ERROR
        CheckerRuleBase.__init__(self,
                                       rule_type = CheckerRuleType.GLOBAL_RULE,
                                       required_parameter_keys=[],
                                       *args, **kwargs)
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules defined by multiple module specification files",
                description = "Checks whether a module is specified by more than one .csproj file.",
                subject_type = DiagnosticSubjectTypeParameterKeys.MODULE,
                example = [("BTC.CAB.Commons.Core.NET", "WARNING: module is specified by multiple module specification files: CoreAssetBase\\BTC\\Commons\\Core\\NET\\BTC.CAB.Commons.Core.NET.SL.csproj, CoreAssetBase\\BTC\\Commons\\Core\\NET\\BTC.CAB.Commons.Core.NET.VS10.csproj, CoreAssetBase\\BTC\\Commons\\Core\\NET\\BTC.CAB.Commons.Core.NET.csproj ")],
                documentation_link = "no documentation so far")
        self.__count_distinct_files_func = count_distinct_files_func
    
    def _rule_core(self, data):
        self.__logger.info("Checking for duplicated modules")
        moduleDict = dict()
        for module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            module_binary_basename = data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.BINARY_BASENAME]
            try:
                moduleDict[module_binary_basename].append(module)
            except KeyError:
                moduleDict[module_binary_basename] = list([module,])
        self.__logger.info("module binary basename: module specification file" + str(moduleDict))
        moduleList = moduleDict.items()
        filteredModuleList = ifilter(lambda (assembly_name, files): self.__count_distinct_files_func(files) > 1, list(moduleList))
        # TODO: statt "module specification file" sollte self._get_parameter_user_name(...) verwendet werden
        # -> das koennte auch im Wiki beschrieben werden :)
        for (assembly_name, files) in filteredModuleList:
            self.__logger.info("module is specified by multiple module specification files: %s " %', '.join(files))
            yield DiagnosticResult(level=self.__level,
                            message="module is specified by multiple module specification files: %s " %', '.join(files),
                            diagnostic_description = self.__diagnostic_description,
                            subject = assembly_name,
                            subject_type = DiagnosticSubjectTypeParameterKeys.MODULE) 

    def get_diagnostic_description(self):
        return self.__diagnostic_description
    

class RedundantModulesInSolutionFilesRule(CheckerRuleBase):
    def __init__(self,*args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__level = logging.INFO
        CheckerRuleBase.__init__(self,
                                       rule_type = CheckerRuleType.GLOBAL_RULE,
                                       required_parameter_keys=[],
                                       *args, **kwargs)
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "module specification files referenced by more than one solution file",
                description =  "Checks whether there are .csproj files which are referenced in more than one solution file.",
                subject_type = DiagnosticSubjectTypeParameterKeys.SOLUTION,
                example = [("CoreAssetBase.Net\\BTC\\CoreEngine\\build\\BTC.CAB.CoreEngine.Full.sln, CoreAssetBase.Net\\BTC\\CoreEngine\\build\\BTC.CAB.CoreEngine.sln", "INFO: module CoreAssetBase.Net\\BTC\\CoreEngine\\App\\AllReferences\\BTC.CAB.CoreEngine.App.AllReferences.csproj is contained in more than one solution file. ")],
                documentation_link = "no documentation so far")
        
    def _rule_core(self, data):
        self.__logger.info("checking redundant modules in solution files rule")
        moduleDict = dict()
        for solution_file in data[CheckerParameterKeys.MODULES_IN_SOLUTIONS]:
            for module in data[CheckerParameterKeys.MODULES_IN_SOLUTIONS][solution_file]:
                # TODO: os.path.join(solution_file, os.path.pardir) should be equal to os.path.dirname(solution_file), but the latter is closer to the intended semantics  
                module_fullname = os.path.normpath(os.path.join(solution_file,os.path.pardir,module))
                try:
                    moduleDict[module_fullname].append(solution_file)
                except KeyError:
                    moduleDict[module_fullname] = [solution_file]
        self.__logger.info("solutions : project files" + str(moduleDict))
        moduleList = moduleDict.items()
        filteredModuleList = ifilter(lambda (module, solution_files): len(solution_files) > 1, list(moduleList))
        # TODO: statt "solution file/.sln file" sollte self._get_parameter_user_name(...) verwendet werden
        for (module_name, solution_files) in filteredModuleList:
            yield DiagnosticResult(level=self.__level,
                            message="module %s is contained in more than one solution file."%(module_name),
                            diagnostic_description = self.__diagnostic_description,
                            subject = solution_files,
                            subject_type = DiagnosticSubjectTypeParameterKeys.SOLUTION)

    def get_diagnostic_description(self):
        return self.__diagnostic_description
    

class ExistAllProjectsInSolutionFilesRule(CheckerRuleBase):  
    def __init__(self, module_specification_file_extensions, *args, **kwargs):
        self.__level = logging.ERROR
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__module_specification_file_extensions = module_specification_file_extensions
        CheckerRuleBase.__init__(self,
                                       rule_type = CheckerRuleType.GLOBAL_RULE,
                                       required_parameter_keys=[],
                                       *args, **kwargs)
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "module specification files referenced by a %s outside analysis scope with the extension(s): %s"%(self._get_parameter_user_name(DiagnosticSubjectTypeParameterKeys.SOLUTION),','.join(module_specification_file_extensions)),
                description = "Checks whether all files referenced in a %s with the extension(s): %s were analyzed. If they were not analyzed it may be they do not exist or they are in a directory which is not intended to be analyzed."%(self._get_parameter_user_name(DiagnosticSubjectTypeParameterKeys.SOLUTION),','.join(module_specification_file_extensions)),
                subject_type = DiagnosticSubjectTypeParameterKeys.SOLUTION,
                example = [("CoreAssetBase.Net\\BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln", "ERROR: project file coreassetbase.net\\btc\\loggingwrapper\\btc.cab.commons.loggingwrapper.csproj is referenced in CoreAssetBase.Net\\BTC\\Commons\\BTC.CAB.Commons.LoggingWrapper.sln, but was not analyzed ")],
                documentation_link = "no documentation so far")

    def _rule_core(self, data):
        module_list = list()
        for module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            module_list.append((os.path.normpath(module)).lower())
        self.__logger.info("checking exist all projects in %s rule"%self._get_parameter_user_name(DiagnosticSubjectTypeParameterKeys.SOLUTION))
        self.__logger.info("ignoring" + str(self.__module_specification_file_extensions))
        self.__logger.info("list of all analyzed modules" + str(module_list))
        failing_list = list()
        for solution_file in data[CheckerParameterKeys.MODULES_IN_SOLUTIONS]:
            for project in data[CheckerParameterKeys.MODULES_IN_SOLUTIONS][solution_file]:
                project_fullname = os.path.normpath(os.path.join(solution_file,'..',project))
                if project_fullname.lower().endswith(tuple(self.__module_specification_file_extensions)) and project_fullname.lower() not in module_list:
                    failing_list.append(project_fullname)
        # TODO: statt "project file" sollte self._get_parameter_user_name(...) verwendet werden
        # -> das könnte auch im Wiki beschrieben werden :)
                    yield DiagnosticResult(level=self.__level,
                            message="project file %s is referenced in %s, but was not analyzed (maybe it does not exist or it is not in the analyzed directory)" %(project_fullname, solution_file),
                            diagnostic_description=self.__diagnostic_description,
                            subject = solution_file,
                            subject_type = DiagnosticSubjectTypeParameterKeys.SOLUTION)
        self.__logger.info("list of not found modules" + str(failing_list))              


    def get_diagnostic_description(self):
        return self.__diagnostic_description
    
    
class DirectoryHierarchyRule(CheckerRuleBase):  
    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__level = logging.WARNING
        self.__exceptions = ["test", "net", "cpp" ]
        CheckerRuleBase.__init__(self,
                                       rule_type = CheckerRuleType.GLOBAL_RULE,
                                       required_parameter_keys=[],
                                       *args, **kwargs)
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "inconsistent directory structure",
                description = "Checks whether all modules in one directory with the same granularity have the same directory depth. E.g. BTC/A/B.X, BTC/A/B.Y and BTC/A/C/Z is fine, while BTC/A/B.X, BTC/A/B/Y and BTC/A/C/Z is not fine.",
                subject_type = DiagnosticSubjectTypeParameterKeys.MODULE,
                example = [("BTC.CAB.Utilities.Service.ServiceAddIn.GUI, BTC.CAB.Utilities.Service.ServiceAddIn", "WARNING: the usage of directory CoreAssetBase.Net\\BTC\\Utilities\\Service\\ServiceAddIn\\src\\BTC.CAB.Utilities.Service.ServiceAddIn and directory CoreAssetBase.Net\\BTC\\Utilities\\Service\\ServiceAddIn\\src\\BTC.CAB.Utilities.Service.ServiceAddIn.GUI at the same time is not allowed")],
                documentation_link = "no documentation so far")

    def _rule_core(self, data):
        self.__logger.info("checking directory hierarchy rule")
        directory_module_name_dict = dict()
        for module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            module_dir = data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME]
            module_name = data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.BINARY_BASENAME]
            directory_module_name_dict[RuleUtil.get_dirname(module_dir, delete_build = True)] = module_name
        self.__logger.info("Directory: module name " + str(directory_module_name_dict))
        # Construct list with all dirnames splitted in dirs
        # e.g. A\\B\\C.D and A\\C\\Z -> [['A', 'B','C.D'],['A','C','Z']] 
        list_of_directories = list()
        dict_of_casesensitiv_directories = dict()
        for module_name in directory_module_name_dict:
            dict_of_casesensitiv_directories[module_name.lower()]=module_name
            list_of_directories.append(module_name.lower().split(os.path.sep))
        self.__logger.info(dict_of_casesensitiv_directories)
        self.__logger.info("list of directories to be checked: " + str(list_of_directories))
        if len(list_of_directories) == 0:
            self.__logger.warning("DirectoryHierarchyRule: list of directories is empty for %s" % (data, ))
            return
        # Do as long as there are modules with at least 2 dirparts        
        # TODO this must be refactored, too much nesting...
        for number_of_actual_checked_dirpart in range(max(len(x) for x in list_of_directories)-1):
            # If there is one module with length one, it is critical for the checking.
            # Than it is not allowed that there are any dirparts which are equivalent
            # to the nameparts of the modulename (eg. for BTC.A.B.C: [BTC, BTC.A, BTC.A.B])
            if any(len(directory)==number_of_actual_checked_dirpart+2 for directory in list_of_directories):
                self.__logger.info("there is at least one module of length number_of_actual_checked_dirpart = %s + 2" %number_of_actual_checked_dirpart)
                critical_modules = list((critical_module for critical_module in list_of_directories if len(critical_module)==number_of_actual_checked_dirpart+2))
                self.__logger.info("critical_modules:" + str(critical_modules))
                for critical_module in critical_modules:
                    unallowed_dirparts = self.__get_unallowed_dirparts(number_of_dirpart_to_check = number_of_actual_checked_dirpart+1, critical_module=critical_module)
                    self.__logger.info("critical module" + str(critical_module))
                    if len(unallowed_dirparts):
                        self.__logger.info("unallowed dirparts" + str(unallowed_dirparts))
                        list_directory_greater_equal_critical = self.__get_modules_in_same_directory(list_of_directories, number_of_actual_checked_dirpart, critical_module)
                        self.__logger.info("directory %s and %s are in the same subdirectory until length %i"%(critical_module, list_directory_greater_equal_critical, number_of_actual_checked_dirpart))
                        for directory_greater_equal_critical in list_directory_greater_equal_critical:
                            if directory_greater_equal_critical[number_of_actual_checked_dirpart+1] in unallowed_dirparts \
                                and not self.__check_for_dirparts_exception(directory_greater_equal_critical, unallowed_dirparts, critical_module):
                                    subject_directory_critical = dict_of_casesensitiv_directories[os.path.sep.join(critical_module)]
                                    subject_directory_case = dict_of_casesensitiv_directories[os.path.sep.join(directory_greater_equal_critical)]
                                    self.__logger.info("unallowed: %s and %s"%(os.path.sep.join(directory_greater_equal_critical),os.path.sep.join(critical_module)))
                                    yield DiagnosticResult(level=self.__level,
                                          message = "the usage of directory %s and directory %s at the same time is not allowed"%(subject_directory_critical,subject_directory_case),
                                          diagnostic_description=self.__diagnostic_description,
                                          subject = str(directory_module_name_dict[subject_directory_critical])+", "+str(directory_module_name_dict[subject_directory_case]),
                                          subject_type = DiagnosticSubjectTypeParameterKeys.MODULE)  
    
    def __get_unallowed_dirparts(self, number_of_dirpart_to_check, critical_module):
        critical_namepart = critical_module[number_of_dirpart_to_check].split('.')
        unallowed_dirparts = list()
        for j in range(len(critical_namepart)):
            if j > 0:
                unallowed_dirpart = ''
                for k in range(j):
                    unallowed_dirpart = unallowed_dirpart + critical_namepart[k]
                    if k < j - 1:
                        unallowed_dirpart = unallowed_dirpart + '.'
                
                unallowed_dirparts.append(unallowed_dirpart)
        
        return unallowed_dirparts
    
    def __check_for_dirparts_exception(self, directory_greater_equal_critical, unallowed_dirparts, critical_module):
        if len(critical_module)==len(critical_module):
            number_critical_dir_part = len(critical_module)-1
            if critical_module[number_critical_dir_part] in (".".join((directory_greater_equal_critical[number_critical_dir_part],exception)) for exception in self.__exceptions):
                self.__logger.info("There is a new exception to DirectoryHierarchyRule!")
                self.__logger.info("Compared elements: %s"%str(list((".".join((directory_greater_equal_critical[number_critical_dir_part],exception)) for exception in self.__exceptions))))
                self.__logger.info("directory_greater_equal_critical: " + str(directory_greater_equal_critical))
                self.__logger.info("critical module: " + str(critical_module))
                self.__logger.info("unallowed dirparts: " + str(unallowed_dirparts))
                return True
        return False

    def __get_modules_in_same_directory(self, list_of_directories, number_of_actual_checked_dirpart, critical_module):
        list_directory_greater_equal_critical = list()
        for directory_greater_equal_critical in list_of_directories:
            if len(directory_greater_equal_critical) > number_of_actual_checked_dirpart + 1:
                self.__logger.info("directory to be observed" + str(directory_greater_equal_critical)) # Check if the critical and observed directory are in the same subdirectory.
                match = True
                j = 0 #TODO: Habe gesehen, dass es eine map Funktion gibt, mit welcher das eleganter geloest werden kann.
                while match == True and j < number_of_actual_checked_dirpart + 1:
                    if directory_greater_equal_critical[j] != critical_module[j]:
                        match = False
                    j = j + 1
                if match:
                    list_directory_greater_equal_critical.append(directory_greater_equal_critical)
        return list_directory_greater_equal_critical
           
    def get_diagnostic_description(self):
        return self.__diagnostic_description
    
    
class ExistAllSourceFilesInProjectsRule(CheckerRuleBase):  
    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__level = logging.ERROR
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE_SPECIFICATION_FILE
        CheckerRuleBase.__init__(self,
                                      rule_type = CheckerRuleType.SOURCEFILE_RULE,
                                      required_parameter_keys=[],
                                      *args, **kwargs)
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "source files not found in working copy",
                description = "Checks whether all source files referenced in module specification files can be found in the working copy.",
                subject_type = self.__subject_type,
                example = [("CoreAssetBase.Net\\BTC\\CoreEngine\\Config\\Elements\\BTC.CAB.CoreEngine.Config.Elements.csproj", "ERROR: source file CoreAssetBase.Net\\BTC\\CoreEngine\\Config\\Elements\\API\\IConnection.cs could not be found, but is referenced by Module CoreAssetBase.Net\\BTC\\CoreEngine\\Config\\Elements\\BTC.CAB.CoreEngine.Config.Elements.csproj ")],
                documentation_link = "no documentation so far")
        
    def _rule_core(self, data):
        source_file_list = list((file_in_list.lower() for file_in_list in list(data[CheckerParameterKeys.SOURCE_FILE_LIST])))
        for module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            for source_file in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.SOURCE_FILES]:
                # TODO workaround for duplicate module names; for some reasons '**\*.c' appears in the list of source files then
                if source_file.endswith('*.cs'): 
                    continue
                if source_file.lower() not in source_file_list:
                    yield DiagnosticResult(level=self.__level,
                                            message = "source file %s could not be found, but is referenced by module %s"%(source_file,module),
                                            diagnostic_description=self.__diagnostic_description,
                                            subject = module,
                                            subject_type = self.__subject_type) 
        
    def get_diagnostic_description(self):
        return self.__diagnostic_description
    
    
class SourceFileOutOfProjectsRule(CheckerRuleBase):  
    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__level = logging.WARNING
        CheckerRuleBase.__init__(self,
                                      rule_type = CheckerRuleType.SOURCEFILE_RULE,
                                      required_parameter_keys=[],
                                      *args, **kwargs)
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "source files not in projects",
                description = "Checks whether all source files found in the directory structure are used in at least one project.",
                subject_type = DiagnosticSubjectTypeParameterKeys.SOURCE_FILE,
                example = [("BTC.CAB.EventProcessing.BO", "WARNING: module specification file CAB\\EventProcessing\\BO\\BTC.CAB.EventProcessing.BO.csproj is not contained in any .sln file ")],
                documentation_link = "no documentation so far")
        
    def _rule_core(self, data):
        source_files_in_projects = list()
        for module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            for source_file_in_module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.SOURCE_FILES]: 
                source_files_in_projects.append(source_file_in_module.lower())
        for source_file in list(data[CheckerParameterKeys.SOURCE_FILE_LIST]): 
            if source_file.lower() not in source_files_in_projects:
                yield DiagnosticResult(level=self.__level,
                                            message = "source file %s is not contained in any .csproj file"%(source_file),
                                            diagnostic_description=self.__diagnostic_description,
                                            subject = source_file,
                                            subject_type = DiagnosticSubjectTypeParameterKeys.SOURCE_FILE)
        
    def get_diagnostic_description(self):
        return self.__diagnostic_description

class PrefixRule(CheckerRuleBase):

    @staticmethod
    def __make_wrong_prefix(prefix, sep_char):
        parts = prefix.split(sep_char)
        parts[len(parts)-1] = 'Wrong' if (parts[len(parts)-1] != 'Wrong') else 'Other'
        return sep_char.join(parts)
    
    
    def __init__(self, prefix, sep_char='.', *args, **kwargs):
        CheckerRuleBase.__init__(self, rule_type = CheckerRuleType.MODULE_RULE, required_parameter_keys=[ModuleCheckerParameterKeys.BINARY_BASENAME], *args, **kwargs)    
        self.__level = logging.WARNING
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE
        if prefix.endswith(sep_char):
            self.__prefix = prefix
        else:
            self.__prefix = prefix + sep_char
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules with invalid prefix ",
                description = "This rule checks whether the module starts with the prefix '%s'." % (self.__prefix, ),
                subject_type = self.__subject_type,
                example = [("...\\%sSomeName.csproj" % (self.__make_wrong_prefix(self.__prefix, sep_char),), 
                            "WARNING: assembly name does not start with %s, actual = SomeName" % (self.__prefix, ))],
                documentation_link = "no documentation so far")
        
    def _rule_core(self, data):
        if not data[ModuleCheckerParameterKeys.BINARY_BASENAME].startswith(self.__prefix):
            yield DiagnosticResult(level=self.__level,
                    message="%s does not start with %s, actual = %s" 
                        % (self._get_parameter_user_name(ModuleCheckerParameterKeys.BINARY_BASENAME),
                           self.__prefix, 
                           data[ModuleCheckerParameterKeys.BINARY_BASENAME]),
                    diagnostic_description = self.__diagnostic_description,
                    subject = os.path.sep.join((data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME],
                                                data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME])),
                    subject_type = self.__subject_type)
            
    def get_diagnostic_description(self):
        return self.__diagnostic_description
    

class ModuleGroupNameRule(CheckerRuleBase):
    """
    This rule checks whether all module groups names have the same case sensitivity.
    The seperation character and the element from which on the module group names
    should be checked.
    @param sep_char: The seperation character which seperates the elements of the
                     module group name. e.g.: '.' in BTC.CAB.TimeSeries.
                     Default is '.'
    @param start_element: The number of the element of the first element to start with.
                          This should be adjusted with the PrefixRule, e.g. if BTC.CAB
                          should be the common prefix it is recommended to set the 
                          value 3 for the start_element.
                          Default is 0.
    """
    def __init__(self, sep_char='.', start_element=0, *args, **kwargs):
        CheckerRuleBase.__init__(self, rule_type = CheckerRuleType.GLOBAL_RULE, required_parameter_keys=[], *args, **kwargs)    
        self.__logger = logging.getLogger(self.__class__.__module__)        
        self.__level = logging.INFO
        self.__sep_char = sep_char
        self.__start_element = start_element-1
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules with different (in matters of case sensitivity) module group names ",
                description = "This rule checks whether the module group name is used by all contained module with the same case sensitivity." ,
                subject_type = self.__subject_type,
                example = [("","")],
                documentation_link = "no documentation so far")

    def _rule_core(self, data):
        dict_module_names_lower_to_casesensitiv = dict()
        list_module_names_lower = list()
        list_module_names = list()
        for module in data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER]:
            dict_module_names_lower_to_casesensitiv[data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.BINARY_BASENAME].lower()] = \
                             data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.BINARY_BASENAME]
            list_module_names_lower.append(data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.BINARY_BASENAME].lower().split("."))
            list_module_names.append(data[CheckerParameterKeys.MODULE_CHECKER_PARAMETER][module][ModuleCheckerParameterKeys.BINARY_BASENAME].split("."))
        print list_module_names
        return self.__check_for_failures(list_module_names)

    def __check_for_failures(self, list_module_names, iterator=0):
        name_groups = self.__get_name_groups(list_module_names, iterator)
        (common_name_part_list, name_groups) = name_groups
        self.__logger.info("iterator: " + str(iterator))
        self.__logger.info("common name part list: " + str(common_name_part_list))
        self.__logger.info("name groups: " +str(name_groups))
        if (iterator>=self.__start_element):
            duplicated_list = list(self.__get_duplicated_module_group_names(common_name_part_list))
            if len(duplicated_list):
                for (duplicate_one_key, duplicate_two_key) in duplicated_list:
                    duplicate_two_list = name_groups[duplicate_two_key]
                    duplicate_one_list = name_groups[duplicate_one_key]
                    self.__logger.info("duplicate_one_list: " + str(duplicate_one_list))
                    self.__logger.info("duplicate_two_list: " + str(duplicate_two_list))
                    if (len(duplicate_one_list)<=len(duplicate_two_list)):
                        for duplicate_one in duplicate_one_list:
                            yield self.__create_diagnostic_result(duplicate_one, duplicate_two_list)
                    if (len(duplicate_two_list)<len(duplicate_one_list)):
                        for duplicate_two in duplicate_two_list:
                            yield self.__create_diagnostic_result(duplicate_two, duplicate_one_list)
        for name_group_keyword in name_groups:
            name_group_list = list(name_group for name_group in name_groups[name_group_keyword] if len(name_group)-1>iterator)
            if len (name_group_list):
                results = list(self.__check_for_failures(name_group_list, iterator+1))
                if len (results):
                    for result in results:
                        yield result

    def __get_name_groups(self, list_module_names, iterator):
        """
        Returns a tuple of a list with the common name parts and a dict
        with the common name parts as key and all modules with that name part.
        """
        common_name_part_list = list()
        name_groups = list(((x, list(y)) for (x, y) in (IterTools.sort_and_group(lambda name_parts_list:name_parts_list[iterator], list_module_names))))
        for common_name_part, _module_group_names_with_common_name_part in name_groups:
            common_name_part_list.append(common_name_part)
        return (common_name_part_list, dict(name_groups))

    def __get_duplicated_module_group_names(self, common_name_part_list):
        common_name_part_lower_set = set(name_part.lower() for name_part in common_name_part_list)
        dict_name_parts_lower_casesensitiv = dict()
        if len(common_name_part_lower_set) != len(common_name_part_list):
            for name_part in common_name_part_list:
                if dict_name_parts_lower_casesensitiv.has_key(name_part.lower()):
                    dict_name_parts_lower_casesensitiv[name_part.lower()].append(name_part)
                else:
                    dict_name_parts_lower_casesensitiv[name_part.lower()] = [name_part] 
        return (value for value in dict_name_parts_lower_casesensitiv.values() if len(value)>1)
                    
    def __create_diagnostic_result(self, duplicate_one, duplicate_two_list):  
        duplicate_one_module_name = self.__sep_char.join(duplicate_one)
        duplicate_two_module_name_list = (self.__sep_char.join(duplicate_two) for duplicate_two in duplicate_two_list)
        # TODO modify the names such that the differences are highlighted
        return DiagnosticResult(level=self.__level,
            message="The module group names of the modules %s and %s do not have the same case sensitivity."%(duplicate_one_module_name, ", ".join(duplicate_two_module_name_list)),
            diagnostic_description = self.__diagnostic_description,
            subject = [duplicate_one_module_name],
            subject_type = self.__subject_type)
                
    def get_diagnostic_description(self):
        return self.__diagnostic_description
    
                                                                      
class CheckerRuleFactoryDefault(CheckerRuleFactory):
    """
    A factory creating default rules that are assumed to be sensible for most technologies and 
    development platforms.
    """
    # TODO all methods must be added to the CheckerRuleFactory interface! 
    
    #TODO Is not tested by UnitTests    
    def __init__(self, parameter_user_names, module_specification_file_extensions, module_specification_file_transformation=DefaultParameterMatchRule.DEFAULT_SPECIFICATION_FILE_TRANSFORMATION):
        self.__parameter_user_names = parameter_user_names
        self.__module_specification_file_extensions = module_specification_file_extensions
        self.__module_specification_file_transformation = module_specification_file_transformation
    
    @staticmethod
    def exchange_rule(old_rules, new_rule):
        """
        Replace an instance of a class by another instance of the same class within an iterable of rules.
        TODO: Ist das so beabsichigt? BTCEPMARCH-877
        If there is no instance of the class it just adds the class to the iterable.
        @rtype: iterable
        """
        # TODO this is not specific to rules and could be moved to commons.core_util
        return chain(ifilter(lambda old_rule: not isinstance(old_rule, new_rule.__class__), old_rules), (new_rule,))        
    
    def rules(self):
        warnings.warn("deprecated, use all_rules(self, technology)", DeprecationWarning)
        classes = [HasAssemblyNameRule, 
                   HierarchicalNameRule, 
                   ModuleSpecBelowSourceRootRule, 
                   SourceFilesOutOfModuleRule, 
                   SourceFilesOutOfRepositoryRule, 
                   ContainedModulesOutOfRepositoryRule,
                   partial(DefaultParameterMatchRule, 
                           module_specification_file_extensions=self.__module_specification_file_extensions, 
                           module_specification_file_transformation=self.__module_specification_file_transformation,
                           parameter_user_names=self.__parameter_user_names),
                   ]
        if ModuleCheckerParameterKeys.ROOT_NAMESPACE in self.__parameter_user_names:
            classes.append(HasRootNamespaceNameRule)
        return (class_name(parameter_user_names=self.__parameter_user_names) for class_name in classes)

    def all_rules(self, technology):
        """
        Returns all rules.
        Attention! This method will be overwriten by system specific methods!
        This are:
        systems/amm/checker
        systems/cab/checker
        """
        if technology == TechnologyTypes.DOTNET:
            classes = [ModuleOutOfSolutionRule,
                   DirectoryHierarchyRule,
                   DuplicatedModulesRule,
                   RedundantModulesInSolutionFilesRule,
                   partial(ExistAllProjectsInSolutionFilesRule,
                           module_specification_file_extensions=self.__module_specification_file_extensions,
                           parameter_user_names=self.__parameter_user_names),
                   HasAssemblyNameRule, 
                   HierarchicalNameRule, 
                   SourceFilesOutOfModuleRule, 
                   SourceFilesOutOfRepositoryRule, 
                   partial(DefaultParameterMatchRule, 
                           module_specification_file_extensions=self.__module_specification_file_extensions, 
                           module_specification_file_transformation=self.__module_specification_file_transformation,
                           parameter_user_names=self.__parameter_user_names),
                   ExistAllSourceFilesInProjectsRule,
                   #TODO: Deactived because of too many failures. See BTCEPMARCH-799.
                   ModuleGroupNameRule,           
                   SourceFileOutOfProjectsRule
                   ]
            
        if technology == TechnologyTypes.CPP:
            classes = [HasAssemblyNameRule, 
                   HierarchicalNameRule, 
                   ModuleSpecBelowSourceRootRule, 
                   SourceFilesOutOfModuleRule, 
                   SourceFilesOutOfRepositoryRule, 
                   ContainedModulesOutOfRepositoryRule,
                   DirectoryHierarchyRule,
                   DuplicatedModulesRule,
                   partial(DefaultParameterMatchRule, 
                           module_specification_file_extensions=self.__module_specification_file_extensions, 
                           parameter_user_names=self.__parameter_user_names),
                   ]
        if ModuleCheckerParameterKeys.ROOT_NAMESPACE in self.__parameter_user_names:
            classes.append(HasRootNamespaceNameRule)
        return (class_name(parameter_user_names=self.__parameter_user_names) for class_name in classes)

    def global_rules_cpp(self):
        """
        Returns the global rules which need only GlobalCheckerParameterKeys.MODULE_CHECKER_PARAMETER
        """
        warnings.warn("deprecated, use all_rules(self, technology)", DeprecationWarning)

        classes = [DirectoryHierarchyRule,
                   DuplicatedModulesRule]
        return (class_name(parameter_user_names=self.__parameter_user_names) for class_name in classes)
    
    def source_file_rules(self):
        warnings.warn("deprecated, use all_rules(self, technology)", DeprecationWarning)

        classes = [ExistAllSourceFilesInProjectsRule,
                   SourceFileOutOfProjectsRule
                   ]
        return (class_name(parameter_user_names=self.__parameter_user_names) for class_name in classes)
