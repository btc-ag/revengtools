#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.basic_config_if import BasicConfig
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    SCCEdgeDecorator, NodeSizeScalingDecorator, NodeSizeLabelDecorator)
from base.dependency.dependency_util import (GraphDescriptionImpl, 
    ComponentDependencyMetric)
from commons.configurator import Configurator
from commons.graph.attrgraph_util import SCCMerger
from commons.graph.output_default import DefaultNodeGroupingConfiguration
from commons.graph.output_if import DecoratorSet, GraphicalGraphOutputter
from commons.graph.output_util import NodeGroupDecorator
from commons.os_util import FixedBaseDirPathResolver
from cpp.cpp_if import FileToModuleMapSupply
from cpp.cpp_util import FileBasedNodeGrouper, FileNameMapper, PseudoModuleSizer
from cpp.incl_deps.include_deps_util import (
    FileLevelPseudoModuleDependencyGenerator)
import logging
import os.path
import sys

config_basic = BasicConfig()
config_graphical_graph_outputter = GraphicalGraphOutputter
config_node_grouper_class = FileBasedNodeGrouper
config_file_to_module_map_supply = FileToModuleMapSupply()

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    Configurator().default()
    
    if len(sys.argv) < 1:
        print("usage: %s <comma-separated list of module names> <comma-separated list of options>" % (sys.argv[0]))
        print("valid options:")
        print("  graph: Output a graph (otherwise, only dependency metrics are calculated)")
        print("  external: Include include dependency across module bounds")
        print("  merge: Merge cycles into one node")
        sys.exit(1)

    output_graph = False
    ignore_external = True
    merge_sccs = False
    
    exceptions = set()
    modulenames = set(sys.argv[1].split(","))
    # TODO !!!
    if  "BtcCommonsCore" in modulenames:
        exceptions = set((("stringnumconvint", "hashmap"), ))
        pass
    
    if len(sys.argv)>2:
        options = set(sys.argv[2].split(","))
        if 'graph' in options:
            output_graph=True
        if 'external' in options:
            ignore_external=False
        if 'merge' in options:
            merge_sccs=True

    file_to_module_map = config_file_to_module_map_supply.generate_file_to_module_map()
    file_name_mapper = FileNameMapper(file_to_module_map, modulenames)
    generator = FileLevelPseudoModuleDependencyGenerator(file_to_module_map=file_to_module_map)
    merged_graph = generator.get_file_level_pseudomodule_graph(modulenames=modulenames,
                                                               mapper=file_name_mapper, 
                                                               ignore_external=ignore_external, 
                                                               exceptions=exceptions)
    
    logging.debug(merged_graph)
    cdm = ComponentDependencyMetric(merged_graph)
    print("Internal file-level CCD of %s is %i, nCCD=%f, ACD=%f" % (", ".join(modulenames), cdm.calculate_ccd(), cdm.calculate_nccd(), cdm.calculate_acd()))

    if merge_sccs:
        merger = SCCMerger(merged_graph)
        merged_graph = merger.get_scc_merged_graph()
        if merger.get_sccs_iter():
            print("SCCs:")
            for (i, scc) in enumerate(merger.get_sccs_iter()):
                print("  SCC %i: %s" % (i, ", ".join(scc)))
                print()

    if output_graph:    
        node_grouper = config_node_grouper_class()
        node_grouper.configure_nodes(merged_graph.node_names_iter())
        basename = os.path.join(config_basic.get_results_directory(),
                                'include_links_for_module-%s' % ("-".join(modulenames),))
        size_fun = PseudoModuleSizer(file_name_mapper, 
                                     path_resolver=FixedBaseDirPathResolver(config_basic.get_local_source_base_dir())).module_size
        decorator_config = DecoratorSet(node_label_decorators=(
                                                               NodeSizeLabelDecorator(size_func=size_fun),
                                                               NodeGroupDecorator(), 
                                                               NodeSizeScalingDecorator(min_render_size=1.5, 
                                                                                        max_render_size=8, 
                                                                                        size_func=size_fun),
                                                               ),
                                        edge_label_decorators=(SCCEdgeDecorator(), ),
                                        node_tooltip_decorators=(),
                                        edge_tooltip_decorators=())
    
        description = GraphDescriptionImpl(description="file-level pseudomodule include dependencies",
            basename=basename,
            extra="(%s->*)" % (", ".join(modulenames),))
        DependencyFilterOutputter(decorator_config).output(
                                           filter=None,
                                           graph=merged_graph,
                                           module_group_conf=DefaultNodeGroupingConfiguration(node_grouper=node_grouper),
                                           description=description)
    #if len(sys.argv) > 3 and sys.argv[3] == 'show':
#    config_graphical_graph_outputter.render_file(description=description,
#                                                 show=True)

if __name__ == "__main__":
    main()
