'''
Created on 18.05.2012

@author: SIGIESEC
'''
from base.diagnostics_util import (CheckerRuleBase, 
    ModuleCheckerParameterKeys, DiagnosticResult, CheckerRuleFactoryDefault,
    SourceFilesOutOfModuleRule, PrefixRule, ModuleGroupNameRule,
    DuplicatedModulesRule)
from base.diagnostics_if import DiagnosticSubjectTypeParameterKeys, DiagnosticDescription, CheckerRuleType
from commons.core_util import CollectionTools
import itertools
import logging
import os.path

class CABRuleTools(object):
    @staticmethod
    def get_rparts(dirname, num, strict=False, pathmodule=os.path):
        dirname_parts = dirname.rsplit(pathmodule.sep, num+1)
        len_dirname = len(list(CollectionTools.flatten(dir_part.split('.') for dir_part in dirname_parts)))

        # TODO perhaps the "build" should be required?
        if not strict and dirname_parts[len(dirname_parts)-1].lower() == "build":
            del dirname_parts[len(dirname_parts)-1]
        if len_dirname > num:
            return dirname_parts[len_dirname-num:]
        else:
            return dirname_parts
        
    @staticmethod
    def get_dirshort(dirname, num, strict=False, pathmodule=os.path):
        dirname_parts = dirname.rsplit(pathmodule.sep, num+1)
        # TODO perhaps the "build" should be required?
        if not strict and dirname_parts[len(dirname_parts)-1].lower() == "build":
            del dirname_parts[len(dirname_parts)-1]
        if len(dirname_parts) > num:
            return pathmodule.sep.join(dirname_parts[len(dirname_parts)-num:])
        else:
            return pathmodule.sep.join(dirname_parts)
    

    @staticmethod
    def get_correct_directory_parts(module_name):
        module_name_parts = list(module_name.split("."))
        # The following additional rule was applied before BTC.CAB.Commons 1.7
        #if len(module_name_parts)>2 and module_name_parts[1].upper() == "CAB":
        #    del module_name_parts[1]
        return module_name_parts
        
    @staticmethod 
    def get_correct_directory(module_name, pathmodule=os.path):
        # TODO this could take into account the existing directories, and reduce the number of candidates heuristically (at least to provide a hint a la "did you mean")
        correct_directory_parts = CABRuleTools.get_correct_directory_parts(module_name)
        first_two_parts = list(x.lower() for x in correct_directory_parts[0:2])
        if first_two_parts == ['btc', 'cab']:
            correct_directory_parts = correct_directory_parts[2:]
            common_prefix = pathmodule.sep.join(["BTC", "CAB", ""])
        else:
            common_prefix = ''
        for separator_sequence in itertools.product('.' + pathmodule.sep, repeat=len(correct_directory_parts) - 1):
            y = zip(correct_directory_parts, separator_sequence)
            yield common_prefix + ''.join(''.join(z) for z in y) + correct_directory_parts[-1]
        
    # TODO is there a check among the set of all directories that it is illegal to have a combination of directories 
    # such as BTC/CAB/ServiceComm.SQ and BTC/CAB/ServiceComm/SQ ???

    @staticmethod
    def check_path(module_name, dirname, strict=False, pathmodule=os.path):
        #print "module_name=%s, dirname=%s, strict=%s, pathmodule=%s" % (module_name, dirname, strict, pathmodule.__name__)
        # TODO should be case sensitive
        if strict:
            map_func = lambda x: x
        else:
            map_func = lambda x: x.lower() 
        expected_parts = (list(map_func(expected_part).split(pathmodule.sep) for expected_part in CABRuleTools.get_correct_directory(module_name, pathmodule)))
        if expected_parts:
            max_lenght_expected_parts = max(len(expected_part) for expected_part in expected_parts)
        else:
            max_lenght_expected_parts = 0;
        dirname = list(CABRuleTools.get_rparts(map_func(dirname), max_lenght_expected_parts, strict=strict, pathmodule=pathmodule))
        expected_parts = list((list(expected_part[len(expected_part)-len(dirname):]) for expected_part in expected_parts))
        return ((dirname in expected_parts) or (dirname in (expected_part.append("build") for expected_part in expected_parts)))
        
    @staticmethod
    def is_copy_target(module_name):
        # TODO check in addition if the module without the .Copy suffix also exists
        return module_name.endswith(".Copy")
    
    __versionfragments = ('-net3.5', '-net4.0', '-net4.5', '.3.5', '.4.0', '.4.5', '-sl5')
    
    @staticmethod
    def transform_project_file_name(filename):
        filename_without_extension = os.path.splitext(filename)[0] # strips the regular extension such as .csproj
        # TODO in the future only remove the version fragments immediately before the extension!
        for fragment in CABRuleTools.__versionfragments:
            if filename_without_extension.find(fragment) != -1:
                return filename_without_extension.replace(fragment, '')
        return filename_without_extension
    
    @staticmethod
    def count_distinct_files(filenames):
        return len(set(map(CABRuleTools.transform_project_file_name, filenames)))
    
class DirectoryRule(CheckerRuleBase):
    def __init__(self, strict=False, *args, **kwargs):
        CheckerRuleBase.__init__(self, rule_type = CheckerRuleType.MODULE_RULE, required_parameter_keys=[ModuleCheckerParameterKeys.BINARY_BASENAME, ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME], *args, **kwargs)
        self.__strict = strict
        self.__level = logging.WARNING
        self.__subject_type = DiagnosticSubjectTypeParameterKeys.MODULE_SPECIFICATION_FILE
        self.__diagnostic_description=DiagnosticDescription(
                dynamic_ID = str(self.__class__.__name__),
                severity = self.__level,
                view_name = "modules with inconsistent directories ",
                description ="This rule checks whether the directory of the module corresponds to the name of the module. It is checked only for the CAB.",
                subject_type = self.__subject_type,
                example = [("BTC\\CAB\\TimeSeries\\WcfServiceAPI\\TimeSeries.WcfServiceAPI.Contracts\\TimeSeries.WcfServiceAPI.Contracts.csproj", "WARNING: project (.csproj) file directory is inconsistent with assembly name BTC.CAB.TimeSeries.WcfServiceAPI.Contracts, expected = BTC\\CAB\\TimeSeries\\WcfServiceAPI\\Contracts\\build (or, until stricter rules apply, BTC\\CAB\\TimeSeries\\WcfServiceAPI\\Contracts), actual = BTC\\CAB\\TimeSeries\\WcfServiceAPI\\TimeSeries.WcfServiceAPI.Contracts")],
                documentation_link = "no documentation so far")    
    
    def _rule_core(self, data):
        assembly_name = data[ModuleCheckerParameterKeys.BINARY_BASENAME]
        if not CABRuleTools.is_copy_target(assembly_name) and not CABRuleTools.check_path(assembly_name, data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME], strict=self.__strict):
            yield DiagnosticResult(level=self.__level,
                    message="%s is inconsistent with %s %s, expected = %s%s, actual = %s" %(self._get_parameter_user_name(ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME), 
                         self._get_parameter_user_name(ModuleCheckerParameterKeys.BINARY_BASENAME), 
                         data[ModuleCheckerParameterKeys.BINARY_BASENAME],
                         ', '.join(list(os.path.sep.join((dirname, "build")) for dirname in CABRuleTools.get_correct_directory(assembly_name))),
                         "" if self.__strict else " (or, until stricter rules apply, %s)" % (', '.join(list(CABRuleTools.get_correct_directory(assembly_name), ))),
                         data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME]),
                    diagnostic_description = self.__diagnostic_description,
                    subject = os.path.sep.join((data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME],
                                                data[ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME])),
                    subject_type = self.__subject_type)                                   

    def get_diagnostic_description(self):
        return self.__diagnostic_description
    
class CABCheckerRuleFactory(CheckerRuleFactoryDefault):
    def __init__(self, parameter_user_names, *args, **kwargs):
        self.__parameter_user_names = parameter_user_names
        CheckerRuleFactoryDefault.__init__(self, parameter_user_names, module_specification_file_transformation=CABRuleTools.transform_project_file_name, *args, **kwargs)
    
    def all_rules(self, technology):
        return  self.exchange_rule(
                self.exchange_rule(
                self.exchange_rule(itertools.chain(CheckerRuleFactoryDefault.all_rules(self, technology),
                               (PrefixRule(parameter_user_names=self.__parameter_user_names, prefix='BTC.CAB'),
                                DirectoryRule(parameter_user_names=self.__parameter_user_names),)),
                                SourceFilesOutOfModuleRule(parameter_user_names=self.__parameter_user_names,
                                                           exceptions=["SharedAssemblyInfo.cs"])),
                                ModuleGroupNameRule(parameter_user_names=self.__parameter_user_names, start_element=3)),
                                DuplicatedModulesRule(parameter_user_names=self.__parameter_user_names, count_distinct_files_func=CABRuleTools.count_distinct_files))
    