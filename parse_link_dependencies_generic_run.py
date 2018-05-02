#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 20.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.dependency.dependency_default import NullDependencyFilterConfiguration
from base.dependency.dependency_if import (DependencyFilter, 
    DependencyFilterConfiguration, ModuleGrouper)
from base.dependency.dependency_if_deprecated import DependencyParser
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    SCCEdgeDecorator, DependencyFilterOutputterTools, PerGroupOutputter)
from base.dependency.dependency_util import (ComponentDependencyMetric, 
    GraphDescriptionImpl, DependencyFilterHelper)
from base.dependency.generation_log_if import GenerationLogGenerator
from base.generic_files_util import GenericFilesTools
from base.module_lister import HTMLModuleLister
from base.rule_lister import HTMLRuleLister, HTMLRuleListerOutputType, XMLRuleListerOutputType, XMLRuleLister
from base.modules_if import ModuleListSupply
from commons.configurator import Configurator
from commons.graph.output_if import GraphicalGraphOutputter, DecoratorSet
from commons.graph.output_util import NodeGroupDecorator, EdgeGroupDecorator
from optparse import OptionParser
import logging
import os.path
import sys

config_dependency_filter = DependencyFilter
config_dependency_parser = DependencyParser
config_dependency_filter_config_class = DependencyFilterConfiguration
config_dependency_filter_outputter = DependencyFilterOutputter
config_graphical_graph_outputter = GraphicalGraphOutputter
config_module_grouper_class = ModuleGrouper
config_module_list = ModuleListSupply()
config_generation_log = GenerationLogGenerator()
config_basic = BasicConfig()

class ParseLinkDependencies(object):
    BASE_DESCRIPTION = "module-level link dependencies"
    
    def __init__(self, generic_files_tools=GenericFilesTools):
        self._parser = None
        self.__generic_files_tools = generic_files_tools()

    def print_acd(self, graph):
        metric = ComponentDependencyMetric(graph)
        print("relative ACD = %f" % metric.calculate_acd())
        print("NCCD = %f" % metric.calculate_nccd())

    def process(self, show, focus_on_each_group, generate_graphs):
        self._parser = config_dependency_parser()
        self._parser.process()
        dep_filter = config_dependency_filter(config=NullDependencyFilterConfiguration(), module_list=config_module_list.get_module_list())
        self._parser.output(dep_filter)
        if generate_graphs:
            self.generate_graphs(dep_filter, focus_on_each_group, show)
        
    def generate_graphs(self,dep_filter, focus_on_each_group, show):
        full_link_deps_graph = dep_filter.graph()
        link_deps_graph = DependencyFilterHelper.filter_graph(dependency_filter_configuration=config_dependency_filter_config_class(modules=full_link_deps_graph.node_names_iter()), 
                                                              graph=full_link_deps_graph)

        decorator_conf = DecoratorSet(node_tooltip_decorators=[NodeGroupDecorator()],
                                      edge_tooltip_decorators=[EdgeGroupDecorator()],
                                      edge_label_decorators=[SCCEdgeDecorator()])
        basename = self.__generic_files_tools.get_module_link_deps_basename()
        outputter = config_dependency_filter_outputter(decorator_conf)
        description = GraphDescriptionImpl(description=self.BASE_DESCRIPTION,
                                       basename=basename)
        basenames = DependencyFilterOutputterTools.output_detail_and_overview_graph(graph=link_deps_graph,
                                                                        outputter=outputter,
                                                                        description=description)

        # TODO das sollte nur auf dem nicht kollabierten Graphen ausgeführt werden.
        #TODO bei Verwendung des CABDependsParsers ist hier stdout geschlossen... strange
        #self.print_acd(dep_filter.graph())

        if focus_on_each_group:
            PerGroupOutputter.output_focus_on_each_group(module_grouper=config_module_grouper_class(modules=full_link_deps_graph.node_names()),
                                       full_graph=full_link_deps_graph,
                                       base_name=basename,
                                       base_description=self.BASE_DESCRIPTION,
                                       dependency_filter_config_class=config_dependency_filter_config_class
                                       )

#        if show:
#            graphviz_filename = basenames[1] + config_graphical_graph_outputter.usual_extension()
#            config_graphical_graph_outputter.render_file(graphviz_filename, show=True)


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    #logging.getLogger("commons.configurator").setLevel(logging.DEBUG)
    Configurator().default()
    
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
#    parser.add_option("-s", "--show", dest="show",
#                      help="open the resulting graph output after generation")
    parser.add_option("", "--no_graphs",
                      action="store_false", dest="generate_graphs",
                      help="disable graph generation completely")
    parser.add_option("-g", "--focus_on_each_group",
                      action="store_true", dest="focus_on_each_group",
                      help="output separate graphs for each module group")
    parser.add_option("-l", "--list_modules",
                      action="store_true", dest="list_modules",
                      help="generate a module list")
    parser.set_defaults(
                       show=False, 
                       focus_on_each_group=False,
                       list_modules=False,
                       generate_graphs=True
                       )
    (options, _args) = parser.parse_args()

    Configurator().create_instance(ParseLinkDependencies).process(show=options.show, focus_on_each_group=options.focus_on_each_group, generate_graphs=options.generate_graphs)

    if options.list_modules:
        generation_logger = config_generation_log
        
        #TODO: Kann das schoener über eine for Schleife geloest werden?
        report_filename = os.path.join(config_basic.get_results_directory(),
                                   "module_list.html")
        if (HTMLModuleLister(output_file=open(report_filename, "w"), analysis_info=(config_basic.get_system(),config_basic.get_version(), "Unknown"), module_list_supply=config_module_list).write()):
            description = GraphDescriptionImpl(description="module list",
                                               category="report")
            generation_logger.add_generated_file(description=description,
                                                 filename=report_filename)
            
        report_filename = os.path.join(config_basic.get_results_directory(),
                                   "results_per_rule_list.html")
        if (HTMLRuleLister(output_file=open(report_filename, "w"), analysis_info=(config_basic.get_system(),config_basic.get_version(), "Unknown",), module_list_supply=config_module_list, output_type = HTMLRuleListerOutputType.RESULTS_PER_RULE).write()):
            description = GraphDescriptionImpl(description="results per rule",
                                               category="report")
            generation_logger.add_generated_file(description=description,
                                                 filename=report_filename)
            
        report_filename = os.path.join(config_basic.get_results_directory(),
                                   "results_per_subject_list.html")      
        if (HTMLRuleLister(output_file=open(report_filename, "w"), analysis_info=(config_basic.get_system(),config_basic.get_version(), "Unknown"), module_list_supply=config_module_list, output_type = HTMLRuleListerOutputType.RESULTS_PER_SUBJECT).write()):
            description = GraphDescriptionImpl(description="results per subject",
                                               category="report")
            generation_logger.add_generated_file(description=description,
                                                 filename=report_filename)
        
        report_filename = os.path.join(config_basic.get_results_directory(),
                                   "rule_overview.html")    
        if (HTMLRuleLister(output_file=open(report_filename, "w"), analysis_info=(config_basic.get_system(),config_basic.get_version(), "Unknown"), module_list_supply=config_module_list, output_type = HTMLRuleListerOutputType.RULE_OVERVIEW).write()):
            description = GraphDescriptionImpl(description="rules",
                                               category="overview")
            generation_logger.add_generated_file(description=description,
                                                 filename=report_filename)

        report_filename = os.path.join(config_basic.get_results_directory(),
                                   "checkstyle_result.xml")    
        if (XMLRuleLister(output_file=open(report_filename, "w"), module_list_supply=config_module_list, output_type = XMLRuleListerOutputType.CHECKSTYLE_XML).write()):
            description = GraphDescriptionImpl(description="results per subject",
                                               category="report")
            generation_logger.add_generated_file(description=description,
                                                 filename=report_filename)
        report_filename = os.path.join(config_basic.get_results_directory(),
                                   "revengtools_result.xml")               
        if (XMLRuleLister(output_file=open(report_filename, "w"), module_list_supply=config_module_list, output_type = XMLRuleListerOutputType.REVENGTOOLS_XML).write()):
            description = GraphDescriptionImpl(description="results per subject",
                                               category="report")
            generation_logger.add_generated_file(description=description,
                                                 filename=report_filename)
        report_filename = os.path.join(config_basic.get_results_directory(),
                                   "revengtools.xsd")
        description = GraphDescriptionImpl(description="results per subject",
                                               category="overview")
        generation_logger.add_generated_file(description=description,
                                                 filename=report_filename)

if __name__ == "__main__":
    main()
    #Profiling will increase the computing time. Use only if intended to do so and remove afterwards!
    #import hotshot
    #prof = hotshot.Profile("hotshot_edi_stats")
    #prof.runcall(main)
    #prof.close()
    #from hotshot import stats
    #s = stats.load("hotshot_edi_stats")
    #s.sort_stats("time").print_stats()
