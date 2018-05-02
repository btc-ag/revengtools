'''
Created on 29.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import (DependencyFilterConfiguration, 
    ModuleGrouper)
from base.dependency.generation_log_output import (
    HTMLGeneratedGraphOverviewWriter)
from base.dependency.module.graph_util import ModuleListHelper
from base.modules_if import ModuleListSupply
from commons.config_if import ConfigDependent
from epm.epm_mapper_util import ModuleTypesTools
from epm.epm_physical_if import PhysicalModuleDescriber
import sys

config_physical_module_describer = PhysicalModuleDescriber()
config_module_list_supply = ModuleListSupply()
config_dependency_filter_config_class = DependencyFilterConfiguration
config_module_grouper_class = ModuleGrouper

class EPMHTMLGeneratedGraphOverviewWriter(HTMLGeneratedGraphOverviewWriter, ConfigDependent):
    def _get_omitted_modules_list(self):
        grouped_modules = ModuleTypesTools.get_omitted_modules_by_type(physical_module_describer=config_physical_module_describer,
                                                                       module_list_supply=config_module_list_supply,
                                                                       dependency_filter_config_class=config_dependency_filter_config_class)
        grouped_modules = list(grouped_modules)
        grouped_formatted_modules = ((", ".join(keyval),
                                      ", ".join("%s (%i)" % (module, size)
                                                for (module, size) in sorted(type_modules, key=lambda (module, size): size)))
                                  for (keyval, type_modules) in grouped_modules
                                  if len(keyval))
        return "<ul>%s</ul>" % ("\n".join("<li>type <b>%s</b>: %s</li>" % (types, modules)
                                          for (types, modules) in grouped_formatted_modules))

    def _get_ungrouped_modules_list(self):
        # TODO Das ist eigentlich nicht EPM-spezifisch
        return ModuleListHelper.get_ungrouped_modules(module_list_supply=config_module_list_supply, 
                                                      module_grouper_class=config_module_grouper_class)

    def _write_config_info(self):
        print >>self._get_output_file(), "<p>Configuration information:<br/><ul>"
        print >>self._get_output_file(), "<li>Modules partially or completely omitted from output: %s</li>" % (self._get_omitted_modules_list(), )
        print >>self._get_output_file(), "<li>Modules without any group: %s</li>" % (", ".join(sorted(self._get_ungrouped_modules_list())), )
        print >>self._get_output_file(), "</ul><hr/>"

    def _write_postamble(self):
        self._write_config_info()
        HTMLGeneratedGraphOverviewWriter._write_postamble(self)
        