 #! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.basic_config_if import BasicConfig
from base.dependency.dependency_output_util import (SCCEdgeDecorator, 
    DependencyFilterOutputter, NodeSizeLabelDecorator, NodeSizeScalingDecorator)
from base.dependency.dependency_util import (ReferencingModules, 
    GraphDescriptionImpl)
from clustering.clustering import (basic_clustering_generic, 
    print_dependencies_order)
from commons.configurator import Configurator
from commons.graph.attrgraph_base import NullNodeGrouper
from commons.graph.attrgraph_if import NodeAttributes
from commons.graph.attrgraph_util import (MutableAttributeGraph, SCCMerger, 
    )
from commons.graph.output_default import DefaultNodeGroupingConfiguration
from commons.graph.output_if import DecoratorSet
from commons.graph.output_util import NodeGroupDecorator
from cpp.cpp_if import FileToModuleMapSupply, VirtualModuleTypes
from cpp.cpp_util import FileNameMapper, PseudoModuleSizer
from cpp.incl_deps.include_deps_if import FileIncludeDepsSupply
from cpp.incl_deps.include_deps_util import (
    FileLevelPseudoModuleDependencyGenerator)
from itertools import chain, product, imap, count
from operator import itemgetter
import logging
import os.path
import sys
from commons.os_util import FixedBaseDirPathResolver

config_basic = BasicConfig()
config_file_include_deps_supply = FileIncludeDepsSupply()
config_file_to_module_map_supply = FileToModuleMapSupply()

class ClusterDependencyLifter(object):
    def __init__(self, mapper):
        self.__mapper = mapper
        self.__pseudomodules_to_node_map = dict()
        self.__ids = count(1)
    
    def __to_pseudomodule_list(self, list_of_filenames):
        return frozenset(self.__mapper.get_output_aggregate_for_individual(filename) 
                         for filename in list_of_filenames)        

    def __make_nodename(self, pseudomodule):
        return "_".join(pseudomodule)
        # TODO Should be something like the following, but other places rely on the _-separation, which 
        # will fail if an individual pseudomodule name contains a "_" 
#        if pseudomodule not in self.__pseudomodules_to_node_map:            
#            self.__pseudomodules_to_node_map[pseudomodule] = NodeGroup("cluster %i" % IterTools.first(self.__ids))
#        return self.__pseudomodules_to_node_map[pseudomodule]

    def get_cluster_dependency_graph(self, clustering_result, base_dependency_graph):
        """
        @param clustering_result: 
        @param base_dependency_graph: A BasicGraph whose nodes are the elements of the clusters.
        @return: An AttributeGraph whose nodes are groups of nodes of the base_dependency_graph according to 
        the clusters.
        """
        cluster_graph = MutableAttributeGraph()
        clusters = clustering_result.values()
        for cluster in clusters:
            pseudomodule = self.__to_pseudomodule_list(cluster)
            cluster_graph.set_node_attrs(self.__make_nodename(pseudomodule), 
                                         {NodeAttributes.GROUPED_NODES: pseudomodule, NodeAttributes.LABEL: ""}, 
                                         True)
        for cluster_pair in product(clusters, clusters):
            if cluster_pair[0] != cluster_pair[1]:
                pseudomodule_pair = map(self.__to_pseudomodule_list, cluster_pair)
                if any(base_dependency_graph.has_edge(edge[0], edge[1]) 
                       for edge in product(pseudomodule_pair[0], pseudomodule_pair[1])):
                    cluster_graph.add_edge_and_nodes(self.__make_nodename(pseudomodule_pair[0]), 
                                                     self.__make_nodename(pseudomodule_pair[1]))
        return cluster_graph

class MyClusteringProcessor(object):
    # TODO Separate Processing and Output
    
    # TODO Merge nodes in a SCC a) before reducing cluster or b) just before output
    
    def __init__(self, 
                 target_modules, 
                 module_name_filter=VirtualModuleTypes.remove_suffixes,
                 output_filename_filter=os.path.basename):
        if isinstance(target_modules, basestring):
            target_modules = (target_modules, )
        self.__target_modules = target_modules
        self.__target_files = None
        self.__module_name_filter = module_name_filter
        self.__output_filename_filter = output_filename_filter
        self.__referencing_modules = ReferencingModules(file_dependencies=config_file_include_deps_supply.get_file_include_deps(),
                 file_to_module_map=config_file_to_module_map_supply.generate_file_to_module_map(False),
                 module_name_filter=self.__module_name_filter
                 )
        self.__clustering_result = None
    
    def __get_target_files(self):
        if self.__target_files == None:
            self.__target_files = tuple(filename 
                            for (module, filename) in config_file_to_module_map_supply.get_module_to_header_file_map_final() 
                            if self.__module_name_filter(module) in self.__target_modules)
            
        return iter(self.__target_files)

    def get_clustering_result(self):
        if self.__clustering_result == None:
            inputReader = chain.from_iterable((dict({'calledFile':filename, 'callingModule':module}) 
                                               for module in self.__referencing_modules.get_referencing_modules_iter(filename)) 
                                               for filename in self.__get_target_files())
            self.__clustering_result = basic_clustering_generic(inputReader, (), 0.5, 5, len)
        return self.__clustering_result

    def output_clusters(self):
        clustering_result = self.get_clustering_result()
        # TODO inject output_filename_filter here
        print_dependencies_order(clustering_result,
                                 order = lambda dependencies: lambda x, y: cmp(len(y), len(x)))
        
    def output_refcounts(self):
        target_file_refcount = ((target_file, self.__referencing_modules.get_referencing_module_count(target_file)) 
                                for target_file in self.__get_target_files())
        for (target_file, count) in sorted(target_file_refcount, key=itemgetter(1)):
            print(count, self.__output_filename_filter(target_file))        

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    Configurator().default()

    if len(sys.argv) == 1:
        print("call: list_module_include_deps_per_target_file TargetModule")
        return
    modulenames = set(sys.argv[1].split(","))
    
    exceptions = ()
    if "BtcCommonsCore" in modulenames:
        exceptions = set((("stringnumconvint", "hashmap"), ))
    file_to_module_map = config_file_to_module_map_supply.generate_file_to_module_map()
    file_name_mapper = FileNameMapper(file_to_module_map, modulenames)
    generator = FileLevelPseudoModuleDependencyGenerator(file_to_module_map=file_to_module_map)
    merged_graph = generator.get_file_level_pseudomodule_graph(modulenames=modulenames,
                                                               mapper=file_name_mapper, 
                                                               ignore_external=True, 
                                                               exceptions=exceptions)
    clustering_processor = MyClusteringProcessor(modulenames)
    clustering_processor.output_clusters()
    cluster_graph = ClusterDependencyLifter(file_name_mapper).get_cluster_dependency_graph(clustering_result=clustering_processor.get_clustering_result(), 
                                                                           base_dependency_graph=merged_graph)
    cluster_graph = SCCMerger(cluster_graph).get_scc_merged_graph()
    basename = os.path.join(config_basic.get_results_directory(),
                            'cluster_graph_for_module-%s' % ("-".join(modulenames),))
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

    description = GraphDescriptionImpl(description="file-level pseudomodule cluster graph based on include dependencies",
        basename=basename,
        extra="(%s)" % (", ".join(modulenames),))
    DependencyFilterOutputter(decorator_config).output(
                                       filter=None,
                                       graph=cluster_graph,
                                       module_group_conf=DefaultNodeGroupingConfiguration(node_grouper=NullNodeGrouper()),
                                       description=description)
    clustering_processor.output_refcounts()
    
    # TODO After clustering: extend clusters by reachable pseudomodules, and remove these from other clusters
    
# TODO Pseudomodules that are not referenced from outside the module are missing!
# TODO add incoming dependency count     

if __name__ == "__main__":
    main()
