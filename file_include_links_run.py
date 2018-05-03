#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.basic_config_if import BasicConfig
from base.dependency.dependency_base import (BaseSuffixModuleGrouper, 
    BaseDependencyFilterConfiguration)
from base.dependency.dependency_default import DefaultDependencyFilter
from base.dependency.dependency_output_util import (
    DependencyFilterOutputterTools, SCCEdgeDecorator, NodeSizeLabelDecorator, 
    NodeSizeScalingDecorator, ScalingTypes, DependencyFilterOutputter, 
    ModuleColorNodeDecorator)
from base.dependency.dependency_util import (GraphDescriptionImpl, 
    DependencyFilterHelper)
from commons.configurator import Configurator
from commons.core_util import CollectionTools, SuffixMapper
from commons.graph.attrgraph_util import AttributeGraph, AttributedEdge
from commons.graph.output_base import BaseNodeGroupingConfiguration
from commons.graph.output_if import DecoratorSet
from commons.os_util import FileTools
from cpp.cpp_if import FileToModuleMapSupply, VirtualModuleTypes
from cpp.incl_deps.include_deps_if import FileIncludeDepsSupply
from epm.dependency_output import EPMNodeColorer
import logging
import os.path
import sys

config_basic = BasicConfig()
config_file_to_module_map_supply = FileToModuleMapSupply()
config_file_include_deps_supply = FileIncludeDepsSupply()
#config_graphical_graph_outputter = GraphicalGraphOutputter

class MyNodeGrouper(BaseSuffixModuleGrouper):
    ########################################################
    # Parameters
    defined_module_group_prefixes = [
                                    ]
    defined_module_group_suffixes = {
                                    'streamwrapper': 'streamwrapper',
                                    'exception': 'exception',
                                    'stream': 'stream_impl',
                                    'string': 'string',
                                    'list': 'collection_impl',
                                    'vector': 'collection_impl',
                                    'set': 'collection_impl',
                                    'stack': 'collection_impl',
                                    'collection': 'collectionAPI',
                                    'logger': 'logger',
                                    'cookie': 'cookie',
                                    'formatter': 'formatter',
                                    'map': 'map_impl',
                                    'number': 'basictype',
                                    'numberformatexception': 'basictype',
                                    'basictype': 'basictype',
                                    'boolean': 'basictype',
                                    'integer': 'number_impl',
                                    'float': 'number_impl',
                                    'long': 'number_impl',
                                    'double': 'number_impl',
                                    'timestamp': 'time_timestamp',
                                    'predicate': 'predicate',
                                    'date': 'time_timestamp',
                                    'time': 'time_timestamp',
                                    'countedobject': 'cookie',
                                    'ref': 'cookie',
                                    'sink': 'sourcesink',
                                    'source': 'sourcesink',
                                    'lock': 'lock',
                                    'waitable': 'sync',
                                    'signallable': 'sync',
                                    'result': 'sync',
                                    'object': 'corecore',
                                    'pair': 'pair',
                                    'serializable': 'corecore',
                                    'comparable': 'corecore',
                                    'buffer': 'buffer',
                                    'conditionfactory': 'sync',
                                    'conditionvariable': 'sync',
                                    'condition': 'sync',
                                    'process': 'sync',
                                    'processfactory': 'sync',
                                    'action': 'action',
                                    'memory': 'memory',
                                    'allocator': 'memory',
                                    'mutex': 'mutex',
                                    'mutexfactory': 'mutex',
                                    'sharedmemoryfactory': 'memory',
                                    'selfrefclass': 'cookie',
                                    'connectionfactory': 'connection',
                                    'sharedmemorysocket': 'connection',
                                    'clock': 'time_clock',
                                    'environment': 'sys',
                                    'comparator': 'predicate',
                                    'autoptr': 'autoptr',
                                    'autoarrayptr': 'autoptr',
                                    'fifo': 'sync',
                                    'dynamiclinkloader': 'dll',
                                    'dynalinklibrary': 'dll',
                                    'cachedlinkloader': 'dll',
                                    'iterator': 'iteration',
                                    'iterable': 'iteration',
                                    'manipulator': 'iteration',
                                    'startableactionfactory': 'action_start',
                                    'actionstarter': 'action_start',
                                    'listener': 'corecore',
                                    'typeconverter': 'types_extended',
                                    'stdtypes': 'types_extended',
                                    'stringnumconv': 'types_extended',
                                    'filefactory': 'sys',
                                    'filetools': 'sys',
                                    'pathfinder': 'sys',
                                    'calendar': 'time_clock',
                                    'timemeasure': 'time',
                                    'stringtools': 'string',
                                    'bitstring': 'string_bit',
                                    'iteratorcookie': 'iteration',
                                    'manipulatorcookie': 'iteration',
                                    'filteritercookie': 'filteriterator',
                                    'filtercompareitercookie': 'filteriterator',
                                    'context': 'contextAPI',
                                    'codewhere': 'codewhere',
                                    'fastbuffer': 'buffer_fast',
                                    'fastbufferstream': 'buffer_fast',
                                    'fastvector': 'buffer_fast',
                                    'memoryblockstream': 'memoryblock',
                                    'memoryblock': 'memoryblock',
                                    'streamforewarder': 'streamforewarder',
                                    'sessionid': 'context',
                                    'class': 'class',
                                    }
    module_group_exceptions = \
        dict({'stringdata': 'stringAPI',
              'map': 'mapAPI',           
              'nulldevice': 'stream_impl',
              'stream': 'streamAPI',   
              'istream': 'streamAPI',   
              'ostream': 'streamAPI',   
              'basestream': 'streamAPI',   
              'basicstring': 'stringAPI',
              'hashset': 'map_impl',
              'defformatter.x': 'formatter',
              'swapper': 'formatter',
              })
    ########################################################

    def __init__(self):
        BaseSuffixModuleGrouper.__init__(self, None)
        self.__suffix_mapper = SuffixMapper(CollectionTools.identity_dict(self._determine_node_group_suffixes()))

    def get_node_group_prefix(self, filename):
        # TODO why is commons/core hardcoded here?
        filename = filename.replace('commons/core/', '')
        if filename.startswith('include/'):
            filename = filename.replace('include/', '')
        elif filename.startswith('src/'):
            filename = filename.replace('src/', '')
        (basename, _ext) = os.path.splitext(filename)
        if basename in self.module_group_exceptions:
            return self.module_group_exceptions[basename]
        else:
            suffix_map = self.__suffix_mapper.get_value(basename)
            if suffix_map:
                return self.defined_module_group_suffixes[suffix_map]
            else:
                return BaseSuffixModuleGrouper.get_node_group_prefix(self, filename)

    def _determine_node_group_prefixes(self, nodes):
        #EPMDependencyFilterConfiguration.node_group_prefixes(self, modules)
        # TODO currently ignores nodes parameter...
        return sorted(self.defined_module_group_prefixes, key=lambda x:-len(x))

    def _determine_node_group_suffixes(self):
        #EPMDependencyFilterConfiguration.node_group_prefixes(self, modules)
        # TODO currently ignores nodes parameter...
        return sorted(self.defined_module_group_suffixes.keys(), key=lambda x:-len(x))

    def node_group_prefixes(self):
        return CollectionTools.union_all((BaseSuffixModuleGrouper.node_group_prefixes(self),
                                          set(self.defined_module_group_suffixes.values())))

class MyNodeGroupingConfiguration(BaseNodeGroupingConfiguration):
    collapse_all_module_groups = True

    def collapse_node_group(self, module_group_prefix):
        return self.collapse_all_module_groups

class MyDependencyFilterConfiguration(BaseDependencyFilterConfiguration):
    SKIP_FILES = set(['commons/core/include/export.h'])

    def skip_module(self, filename):
        return  filename in self.SKIP_FILES
    
    def _create_module_grouper(self, modules):
        return MyNodeGrouper()

class FileSizer(object):
    @staticmethod
    def get_file_size(filename):
        return FileTools.file_len(os.path.join(config_basic.get_local_source_base_dir(), filename))

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    Configurator().default()

    module_name = 'BtcCommonsCore'
    restrict_to_headers = False

    file_to_module_map = config_file_to_module_map_supply.generate_file_to_module_map(False)
    all_file_links = config_file_include_deps_supply.get_file_include_deps()
    module_file_links = (AttributedEdge(from_node=from_file, to_node=to_file)
                         for (from_file, to_file) in all_file_links
                         if from_file in file_to_module_map and \
                         VirtualModuleTypes.remove_suffixes(file_to_module_map[from_file]) == module_name and \
                         (not restrict_to_headers or from_file.endswith('.h')))
    #pprint(list(module_file_links))
    # TODO is this correct? does the output graph contain anything if the module list is empty?
    dependency_filter = DefaultDependencyFilter(config=MyDependencyFilterConfiguration(),
                                                module_list=()) 
                                                #module_list=set(edge.get_from_node() for edge in module_file_links))
    graph = DependencyFilterHelper.filter_graph(dependency_filter=dependency_filter, 
                                                graph=AttributeGraph(edges=module_file_links))

    decorator_config = DecoratorSet(edge_label_decorators=[SCCEdgeDecorator()],
                                    node_label_decorators=[NodeSizeLabelDecorator(size_func=FileSizer.get_file_size),
                                                           NodeSizeScalingDecorator(size_func=FileSizer.get_file_size,
                                                                                    min_render_size=3,
                                                                                    max_render_size=14,
                                                                                    scale_type=ScalingTypes.RADICAL),
                                                            ModuleColorNodeDecorator(EPMNodeColorer()),
                                                           ])
    graph_description = GraphDescriptionImpl(description="internal include dependencies of %s" % module_name,
                                             basename=os.path.join(config_basic.get_results_directory(), module_name),
                                             section='module-internal')
    DependencyFilterOutputterTools.output_detail_and_overview_graph(graph=graph,
                                                                    #decorator_config=decorator_config,
                                                                    description=graph_description,
                                                                    outputter=DependencyFilterOutputter(decorator_config=decorator_config),
                                                                    module_group_conf=MyNodeGroupingConfiguration(MyNodeGrouper())
                                                                    )

if __name__ == "__main__":
    main()
