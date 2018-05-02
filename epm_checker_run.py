#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 30.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import ModuleGrouper
from base.dependency.dependency_output_util import DependencyFilterOutputter
from base.dependency.dependency_util import GraphDescriptionImpl
from base.dependency.module.linkdeps_if import ModuleLinkDepsSupply
from base.generic_files_util import GenericFilesTools
from commons.configurator import Configurator
from commons.graph.attrgraph_if import Colors
from commons.graph.attrgraph_util import AttributeGraph
from commons.graph.output_default import DefaultNodeGroupingConfiguration
from commons.graph.output_if import (NodeGroupingConfiguration, DecoratorSet, 
    GraphicalGraphOutputter, TextualGraphOutputter,
    GraphicalGraphOutputterFactory, TextualGraphOutputterFactory)
from commons.graph.output_util import (NodeGroupDecorator, EdgeGroupDecorator, 
    OutputMultiGraphTools)
from epm.dependency_output import EPMModuleTypeEdgeDecorator
from epm.epm_checker_if import EPMArchitecturalStyleChecker
import logging
import sys
from commons.config_if import ConfigDependent

config_module_link_deps_supply = ModuleLinkDepsSupply
config_module_grouper = ModuleGrouper
config_node_group_conf = NodeGroupingConfiguration
config_dependency_filter_outputter = DependencyFilterOutputter
config_style_checker = EPMArchitecturalStyleChecker
config_graphical_graph_outputter_factory = GraphicalGraphOutputterFactory()
config_textual_graph_outputter_factory = TextualGraphOutputterFactory()

class EPMRuleCheckerOutputter(ConfigDependent):
    def __init__(self, rule_violations, module_link_deps_graph, generic_files_tools=GenericFilesTools):
        self.__module_link_deps_graph = module_link_deps_graph.immutable()
        self.__rule_violations = rule_violations
        self.__generic_files_tools = generic_files_tools()

    def __get_description(self):
        dot_filename = self.__generic_files_tools.get_module_link_deps_basename() + "-epm-rules"
        description = GraphDescriptionImpl(basename=dot_filename,
            description="EPM physical rule violations based on module-level link dependencies")
        return description

    def __output_combined_graph(self, show_combined_graph, multigraph, multigraph_overview, node_group_conf):
        decorator_conf = DecoratorSet(node_tooltip_decorators=[NodeGroupDecorator()],
                                      edge_tooltip_decorators=[EdgeGroupDecorator(), EPMModuleTypeEdgeDecorator()],
                                      )
        description = self.__get_description()
        # TODO wieso wird hier nicht output_detail_and_overview_graph benutzt?
        #DependencyFilterOutputterTools.output_detail_and_overview_graph(dep_filter.graph(), basename, outputter, module_group_conf)
        node_group_conf.get_node_grouper().configure_nodes(multigraph.node_names())
        config_dependency_filter_outputter(decorator_conf).output_graph \
            (description=description,
             graph_outputter_factory=config_graphical_graph_outputter_factory,
             graph=multigraph,
             node_group_conf=node_group_conf,
             collapse=False)
        description.set_category('overview')
        config_dependency_filter_outputter(decorator_conf).output_graph \
            (description=description,
             graph_outputter_factory=config_graphical_graph_outputter_factory,
             graph=multigraph_overview,
             node_group_conf=node_group_conf,
             collapse=True)
        #if show_combined_graph:
        #    config_graphical_graph_outputter.render_file(dot_filename + '-overview' + config_graphical_graph_outputter.usual_extension(),
        #                                                 show=show_combined_graph)


    def output_report(self):
        description = self.__get_description()
        description.set_category("report")
        config_dependency_filter_outputter(DecoratorSet(edge_label_decorators=[EPMModuleTypeEdgeDecorator()])).output_graph \
            (description=description,
             graph_outputter_factory=config_textual_graph_outputter_factory,
             graph=AttributeGraph(edges=self.__rule_violations),
             collapse=False)


    def __construct_combined_graphs(self, node_group_conf):
        base_graph = self.__module_link_deps_graph
        superfluous_deps = self.__rule_violations
        missing_deps = ()
        multigraph = OutputMultiGraphTools.construct_superfluous_missing_multigraph(base_graph, 
            superfluous_deps, 
            missing_deps, 
            node_group_conf=DefaultNodeGroupingConfiguration(config_module_grouper()), 
            superfluous_color=Colors.DARKPURPLE)
        multigraph_overview = OutputMultiGraphTools.construct_superfluous_missing_multigraph(base_graph, 
            superfluous_deps, 
            missing_deps, 
            node_group_conf=node_group_conf, 
            superfluous_color=Colors.DARKPURPLE)
        return multigraph, multigraph_overview

    def output_graph(self):
        node_group_conf = config_node_group_conf(config_module_grouper())
        multigraph, multigraph_overview = self.__construct_combined_graphs(node_group_conf)
        self.__output_combined_graph(len (sys.argv) > 1 and sys.argv[1] == "show",
                              multigraph,
                              multigraph_overview,
                              node_group_conf)

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    Configurator().default()
    print "Checking EPM physical module dependency rules..."
    module_link_deps_supply = config_module_link_deps_supply()
    #module_link_deps_supply = OnTheFlyModuleLinkDepsSupply()
    module_link_deps_graph = module_link_deps_supply.get_module_link_deps_graph()
    module_grouper = config_module_grouper(modules=module_link_deps_graph.node_names())
    rule_violations = config_style_checker(module_grouper).physical_rule_violations(module_link_deps_supply)
    rule_checker_outputter = Configurator().create_instance(EPMRuleCheckerOutputter, rule_violations,
                                                     module_link_deps_graph)
    rule_checker_outputter.output_report()
    #for edge in sorted(rule_violations):
    #    print "%s -> %s" % (edge.get_from_node(), edge.get_to_node())

    rule_checker_outputter.output_graph()


if __name__ == "__main__":
    main()
