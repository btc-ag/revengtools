'''
Created on 31.03.2011

@author: SIGIESEC

TODO this was copied from cpp.csharp.csproj_parser_wrap and has probably lots of duplication!
'''
from __future__ import with_statement
from base.dependency.dependency_if_deprecated import DependencyParser
from base.modules_if import ModuleListSupply
from base.diagnostics_if import ModuleCheckerParameterKeys
from commons.config_if import ConfigDependent
from cpp.msvc.vcxproj_modules import VCXProjModuleListSupply
from base.basic_config_if import BasicConfig
from cpp.msvc.vcxproj_parser import (VCXProjParser, SetModuleResolver)
import logging
import os

# TODO cannot use singleton since this is currently defined in the same module, 
# which leads to initialization order problems
# ??? ist das noch aktuell? das hier ist doch das Singleton...
# TODO:
# Hier muesste weiter oben der Checker angestossen werden. Zudem muesste die 
# Abhaengigkeit vom Dependency Parser, so wie sie im Moment ist, veraendert werden.
# So dass der Dependency Parser eben auch nur als Supply fuer die Regeln angestossen 
# wird und nicht unbedingt auch direkt die Abhaengigkeiten mit parst.

config_basic = BasicConfig()

class VCXProjReferenceDependencyParser(DependencyParser, ConfigDependent):

    def __init__(self, module_list_supply=ModuleListSupply()):
        # TODO actually, this does not require an arbitrary ModuleListSupply, but a VCXProjModuleListSupply, but
        # currently the autowire mechanism does not support analyzing the type hierarchy! 
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__dependencies = dict()
        self.__modules = dict()
        self.__analysis_base_dirs = config_basic.get_local_source_base_dir_subset()
        self.__project_dir_resolver = config_basic.get_local_source_resolver()
        self.__module_checker_parameter = dict()
        self.__vcxproj_checker_class = None
        if not hasattr(module_list_supply, "get_module_spec_files") or not hasattr(module_list_supply, "get_source_files") \
          or not hasattr(module_list_supply, "set_results") or not hasattr(module_list_supply, "set_checked_rules"):
            raise TypeError("VCXProjReferenceDependencyParser requires a %s" % (VCXProjModuleListSupply,))
        self.__module_list_supply = module_list_supply
    
    def __create_module_checker_parameter(self, vcxproj):
        module_checker_parameter = dict()
        assembly_name = ""
        root_namespace = ""
        try:
            root_namespace = vcxproj.get_root_namespace()
        except:
            pass
        try:
            assembly_name = vcxproj.get_assembly_name()
        except:
            pass
        vcxproj_filename = vcxproj.get_filename()
        file_basename = os.path.basename(vcxproj_filename)
        file_dirname = self.__to_relative_name(os.path.dirname(vcxproj_filename))
        data = dict({ModuleCheckerParameterKeys.ANALYSIS_BASE_DIRS: self.__analysis_base_dirs,
                     ModuleCheckerParameterKeys.BINARY_BASENAME: assembly_name,
                     ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_BASENAME: file_basename,
                     ModuleCheckerParameterKeys.MODULE_SPECIFICATION_FILE_DIRNAME: file_dirname,
                     ModuleCheckerParameterKeys.ROOT_NAMESPACE: root_namespace,
                     ModuleCheckerParameterKeys.SOURCE_FILES: list(self.__to_relative_name(res.name()) for res in vcxproj.get_source_files())})
        fullname = os.path.normpath(os.path.join(file_dirname, file_basename))
        module_checker_parameter[fullname] = data
        return module_checker_parameter
  
    def __to_relative_name(self, absolute_name):
        resource = self.__project_dir_resolver.resolve(absolute_name)
        return os.path.relpath(resource.name(), resource.get_resolution_root())
    
    def __process_vcxproj(self, resource):
        parser = VCXProjParser(resource.open())
        module_checker_param = self.__create_module_checker_parameter(parser)
        for element in module_checker_param:
            self.__module_checker_parameter[element] = module_checker_param[element]
        try:
            # TODO: use best module name instead
            from_proj = parser.get_assembly_name()
        except ValueError:
            self.__logger.warning("Cannot determine assembly name for %s, skipping in dependency analysis" % parser.get_filename(), exc_info=1)
            return
        
        # TODO: use best module names instead
        to_projs = set(parser.get_all_references())
        if from_proj in self.__dependencies:
            self.__logger.warning("Duplicate assembly name %s, merging dependencies" % (from_proj, ))
            self.__dependencies[from_proj].update(to_projs)
        else:
            self.__dependencies[from_proj] = to_projs
        self.__modules[resource.name()] = parser.get_assembly_name()

    def process(self):
        for module in self.__module_list_supply.get_module_spec_files():
            self.__process_vcxproj(module)
        #for result in self.__create_checker().check(data):
        #    self._add_irregularity(result)
        #    def __create_checker(self):
        #rule_factory = config_checker_rule_factory_class(parameter_user_names=vcxproj_names, module_specification_file_extensions=[VSConstants.CSPROJ_EXTENSION])
        #rules = rule_factory.rules()
        # #return CheckerRunner(rules=rules)
        # checker = self.__vcxproj_checker_class(module_checker_parameter = self.__module_checker_parameter,
                                            # modules_in_solutions = self.__module_list_supply.get_modules_in_solution_files(),
                                            # source_files = self.__module_list_supply.get_source_files())
        # # TODO the following should be changed... this data should not be added to the module list supply
        # self.__module_list_supply.set_results(list(checker.get_irregularities()))
        # self.__module_list_supply.set_checked_rules(list(checker.get_checked_rules()))
        self.__logger.debug("Target map is %s", self.__modules)
        for from_module in self.__dependencies.keys():
            self.__dependencies[from_module] = SetModuleResolver(self.__modules).calc_resolved_modules(from_module, self.__dependencies[from_module])

        if self.__logger.isEnabledFor(logging.DEBUG):
            self.__logger.debug("Raw dependencies are:\n %s", "\n".join("\n".join("%s,%s" %(from_module,to_module) for to_module in self.__dependencies[from_module]) for from_module in self.__dependencies.keys()))
        
    def __get_dependencies(self):
        return self.__dependencies.iteritems()

    def output(self, outputter):
        for (source, targets) in self.__get_dependencies():
            for target in targets:
                outputter.dependency(source, target) 
        outputter.postamble()
    
# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
