#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.basic_config_if import BasicConfig
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    FilenameURLNodeDecorator)
from base.dependency.dependency_util import GraphDescriptionImpl
from commons.configurator import Configurator
from commons.graph.output_default import DefaultNodeGroupingConfiguration
from commons.graph.output_if import DecoratorSet, GraphicalGraphOutputter
from cpp.incl_deps.file_include_deps import FileIncludeDepsProcessor
import logging
import os.path
import sys

config_basic = BasicConfig()
config_graphical_graph_outputter = GraphicalGraphOutputter

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    Configurator().default()

    from_module = sys.argv[1]
    to_module = sys.argv[2]

    fidp = FileIncludeDepsProcessor()
    graph = fidp.graph_for_modules(from_module, to_module)

    basename = os.path.join(config_basic.get_results_directory(), 'include_links_for_modules-%s-%s' % (from_module, to_module))
    decorator_config = DecoratorSet(node_label_decorators=(FilenameURLNodeDecorator(),),
                                    edge_label_decorators=(),
                                    node_tooltip_decorators=(),
                                    edge_tooltip_decorators=())

    description = GraphDescriptionImpl(description="file-level include dependencies",
        basename=basename,
        extra="(%s->%s)" % (from_module, to_module))
    DependencyFilterOutputter(decorator_config).output(
                                       filter=None,
                                       graph=graph,
                                       module_group_conf=DefaultNodeGroupingConfiguration(),
                                       description=description)
    #if len(sys.argv) > 3 and sys.argv[3] == 'show':
#    config_graphical_graph_outputter.render_file(description=description,
#                                                 show=True)

if __name__ == "__main__":
    main()
