#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 23.09.2010

@author: SIGIESEC
'''

from base.basic_config_if import BasicConfig
from base.dependency.dependency_default import NullDependencyFilterConfiguration
from base.dependency.dependency_if import (DependencyFilterConfiguration, 
    ModuleGrouper)
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    GenericGraphOutputter, PerGroupOutputter)
from base.dependency.dependency_util import DependencyFilterHelper
from base.dependency.generation_log_if import GenerationLogGenerator
from base.dependency.module.otf_linkdeps import OnTheFlyModuleLinkDepsSupply
from commons.configurator import Configurator
from commons.graph.output_if import (NodeGroupingConfiguration, 
    GraphicalGraphOutputter)
from cpp.incl_deps.consistency_check import ConsistencyChecker
from cpp.incl_deps.consistency_check_output import (
    ConsistencyCheckerReportOutputter, ConsistencyCheckerGraphOutputter)
from cpp.incl_deps.file_include_deps import FileModuleIncludeDepsSupply
from cpp.incl_deps.otf_include_deps import OnTheFlyModuleIncludeDepsSupply
from cpp.otf_module_file_map import (
    OnTheFlyHeaderExceptionOnlyFileToModuleMapSupply)
import logging
import os.path
import sys

# TODO Das Reexport-Problem besteht auch in Python!!! Prüfung hierfür schreiben

config_basic = BasicConfig()
config_dependency_filter_outputter = DependencyFilterOutputter
config_module_grouper = ModuleGrouper
config_node_group_conf = NodeGroupingConfiguration
config_graphical_graph_outputter = GraphicalGraphOutputter
config_generation_log = GenerationLogGenerator()

class IncludeDepsGraphOutputter(object):
    # TODO this class should be inlined

    BASE_DESCRIPTION = "module-level include dependencies"

    def __init__(self, module_grouper):
        assert isinstance(module_grouper, ModuleGrouper)
        self.__module_grouper = module_grouper


    def output_include_deps_graph(self, include_deps_graph,
                                  more_description="", section="",
                                  module_group_conf=None,
                                  suffix=''
                                  ):
        base_description = self.BASE_DESCRIPTION
        base_name = FileModuleIncludeDepsSupply().get_module_include_deps_basename()

        if module_group_conf == None:
            module_group_conf = config_node_group_conf(self.__module_grouper)

        GenericGraphOutputter.output_graph(include_deps_graph,
                          base_description,
                          more_description,
                          section,
                          module_group_conf,
                          base_name,
                          suffix)



def main(show_combined_graph):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    configurator = Configurator()
    configurator.default()

    dependency_filter_config_class=Configurator().get_concrete_adapter(DependencyFilterConfiguration)
    dep_filter_config = dependency_filter_config_class()
    file_to_module_map_supply = OnTheFlyHeaderExceptionOnlyFileToModuleMapSupply()

    link_deps_supply = OnTheFlyModuleLinkDepsSupply(dep_filter_config)


    link_deps_graph = link_deps_supply.get_module_link_deps_graph()
    full_include_graph = OnTheFlyModuleIncludeDepsSupply(outputter_config=NullDependencyFilterConfiguration(),
                                        file_to_module_map_supply=file_to_module_map_supply).get_module_include_deps_graph()
    module_grouper = config_module_grouper(modules=full_include_graph.node_names())

    include_deps_graph = DependencyFilterHelper.filter_graph(dependency_filter_configuration=dep_filter_config, 
                                                             graph=full_include_graph)
    ec = ConsistencyChecker(link_deps_graph,
                            include_deps_graph,
                            node_group_conf=config_node_group_conf(module_grouper))

    report_filename = os.path.join(config_basic.get_results_directory(),
                                   "IncludeDeps",
                                   "include_link_dep_consistency_report.txt")
    report_output = configurator.create_instance(cls=ConsistencyCheckerReportOutputter, 
                                                 file_to_module_map_supply=file_to_module_map_supply,
                                                 module_grouper=module_grouper,
                                                 report_filename=report_filename)
    report_output.print_all(missing_link_deps_graph=ec.get_missing_link_deps_graph(),
                            irregular_link_deps_graph=ec.get_irregular_link_deps_graph())

    IncludeDepsGraphOutputter(module_grouper=module_grouper).output_include_deps_graph(ec.get_module_include_deps_graph())

    result_output = configurator.create_instance(cls=ConsistencyCheckerGraphOutputter,
                                                 file_to_module_map_supply=file_to_module_map_supply,
                                                 module_grouper=module_grouper)

    result_output.output_combined_graph(show_combined_graph,
                                        ec.get_combined_graph(),
                                        ec.get_overview_combined_graph(),
                                        )

    if '--focus_on_each_group' in sys.argv:
        PerGroupOutputter.output_focus_on_each_group(module_grouper=module_grouper,
                                   full_graph=full_include_graph,
                                   base_name=FileModuleIncludeDepsSupply().get_module_include_deps_basename(),
                                   base_description=IncludeDepsGraphOutputter.BASE_DESCRIPTION,
                                   dependency_filter_config_class=dependency_filter_config_class
                                   )

if __name__ == '__main__':
    main(show_combined_graph=len(sys.argv) > 1 and sys.argv[1] == "show")
