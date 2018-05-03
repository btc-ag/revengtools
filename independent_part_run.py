#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 20.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.dependency.dependency_if import (DependencyFilter, 
    DependencyFilterConfiguration)
from base.dependency.dependency_if_deprecated import DependencyParser
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    DependencyFilterOutputterTools)
from base.dependency.dependency_util import (ComponentDependencyMetric, 
    GraphDescriptionImpl)
from base.generic_files_util import GenericFilesTools
from commons.configurator import Configurator
from commons.graph.graph_util import GraphAlgorithms
from commons.graph.output_if import DecoratorSet, GraphicalGraphOutputter
from commons.graph.output_util import NodeGroupDecorator, EdgeGroupDecorator
from itertools import ifilter
from systems.prins.dependency_output import is_prins_classic
import logging
import sys
from commons.config_if import ConfigDependent

config_dependency_filter = DependencyFilter
config_dependency_parser = DependencyParser
config_dependency_filter_config = DependencyFilterConfiguration()
config_dependency_filter_outputter = DependencyFilterOutputter
config_graphical_graph_outputter = GraphicalGraphOutputter
config_basic = BasicConfig()

class ParseLinkDependencies(ConfigDependent):
    def __init__(self, generic_files_tools=GenericFilesTools):
        self._parser = None
        self.__generic_files_tools = generic_files_tools()

    def print_acd(self, graph):
        metric = ComponentDependencyMetric(graph)
        print("relative ACD = %f" % metric.calculate_acd())
        print("NCCD = %f" % metric.calculate_nccd())

    def process(self, show=False):
        self._parser = config_dependency_parser()
        self._parser.process()
        dep_filter = config_dependency_filter(config=config_dependency_filter_config)
        self._parser.output(dep_filter)

        decorator_conf = DecoratorSet(node_tooltip_decorators=[NodeGroupDecorator()],
                                      edge_tooltip_decorators=[EdgeGroupDecorator()])
        basename = self.__generic_files_tools.get_module_link_deps_basename() + '-sub-custom'
        outputter = config_dependency_filter_outputter(decorator_conf)

        graph = dep_filter.graph()
        # TODO Momentan nur ein Test! 
        #start_nodes = ['osapi', 'prio4dyn', 'dyn', 'prid4dynmfc', 'bib']
        if config_basic.get_system() == 'prins':
            start_nodes = set(ifilter(is_prins_classic, graph.node_names())) - set(['osapi'])
            description = GraphDescriptionImpl(description="subgraph: modules independent of legacy PRINS (link deps)")
        elif config_basic.get_system() == 'revengtools':
            start_nodes = set(ifilter(lambda x: x.startswith(('infrastructure', 'cpp', 'python', 'systems', 'commons.graph')), graph.node_names()))
            description = GraphDescriptionImpl(description="subgraph: generic core")
        else:
            raise RuntimeError("Unknown system %s" % config_basic.get_system())
        GraphAlgorithms.remove_subgraph_dependent_on_nodes(graph, start_nodes)
        
        description.set_basename(basename)
        description.set_section('subgraph')

        DependencyFilterOutputterTools.output_detail_and_overview_graph(graph, 
                                                                        outputter,
                                                                        description=description)

#        if show:
#            graphviz_filename = basename + config_graphical_graph_outputter.usual_extension()
#            config_graphical_graph_outputter.render_file(graphviz_filename, show=True)

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    #logging.getLogger("commons.configurator").setLevel(logging.DEBUG)
    Configurator().default()
    show = False
    if len(sys.argv) > 1 and sys.argv[1] == 'show':
        show = True
    Configurator().create_instance(ParseLinkDependencies).process(show=show)

if __name__ == "__main__":
    main()
