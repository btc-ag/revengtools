#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 24.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.core_util import List, CollectionTools
from commons.graph.attrgraph_if import NodeAttributes
from commons.graph.attrgraph_util import MutableAttributeGraph, NodeGroup
from commons.graph.graph_util import SimpleEdge
from commons.graph.output_base import BaseEdgeDecorator
from commons.os_util import FileTools, NormalizedPathsIter
from cpp.cpp_if import (FileToModuleMapSupply, VirtualModuleTypes, 
    HeaderListSupply, CppFileConfiguration)
from cpp.cpp_util import IncludePathMapping
from cpp.incl_deps.include_deps_if import (ModuleIncludeDepsSupply, 
    FileIncludeDepsSupply)
import logging
import os.path
import warnings
import weakref
from commons.config_if import ConfigDependent
from cpp.cpp_util_wrap import get_default_include_path_mapping

config_basic = BasicConfig()

class FilenameUtility(ConfigDependent):
    @staticmethod
    def get_include_deps_filename(basename):
        return os.path.join(config_basic.get_results_directory(), "IncludeDeps", basename)

class FileModuleIncludeDepsSupply(ModuleIncludeDepsSupply, ConfigDependent):

    def get_module_include_deps_basename(self):
        return FilenameUtility.get_include_deps_filename("module_include_deps")

    def get_module_include_deps_dot_filename(self):
        warnings.warn("deprecated, use get_module_include_deps_basename", DeprecationWarning)
        return self.get_module_include_deps_basename() + ".dot"

    def get_module_include_deps_csv_filename(self):
        warnings.warn("deprecated, use get_module_include_deps_basename", DeprecationWarning)
        return self.get_module_include_deps_basename() + ".csv"

    def get_module_include_deps(self):
        return FileTools.create_csv_reader(filename=self.get_module_include_deps_csv_filename(),
                                           what="module-level include dependencies",
                                           delimiter=',')
    
class FileFileIncludeDepsSupply(FileIncludeDepsSupply):
    def __init__(self):
        self.__file_include_deps = lambda: None
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def __include_dependencies_filename(self):
        return FilenameUtility.get_include_deps_filename("include_statements")

    def get_file_include_deps(self):
        # TODO use IncludeDependencyGenerator to (re)generate if necessary
        o = self.__file_include_deps()
        if o == None:
            o = List(NormalizedPathsIter.create(self.__include_dependencies_filename(), 
                    "file-level include dependencies", 
                    delimiter=','))
            self.__file_include_deps = weakref.ref(o, lambda _x: self.__logger.debug("file-level include dependencies got garbage collected"))
        return o

config_file_include_deps_supply = FileIncludeDepsSupply()
config_file_to_module_map_supply = FileToModuleMapSupply()
config_cpp_file_configuration = CppFileConfiguration()

class IncludeLinksHeaderListSupply(HeaderListSupply, ConfigDependent): 
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__) 

    def get_header_list(self):
        '''
        Returns a list of all headers that are referenced in any implementation file that is defined
        in a module specification.
        '''
        all_files = set(CollectionTools.flatten(config_file_include_deps_supply.get_file_include_deps()))
        result = [x for x in all_files if config_cpp_file_configuration.is_header_file(x)]
        # TODO filter only headers. Where is the list of valid header extensions defined?
        self.__logger.info("%i headers referenced in module spec implementation files" % (len(result)))
        return result

# TODO diese Klasse ist eigentlich überflüssig, es sollte die GraphOutputter verwendet werden
class FileIncludeDepsProcessor(ConfigDependent):
    def __init__(self, file_include_deps=None, file_to_module_map=None, file_to_module_map_supply=None, include_internal_links=False):
        if file_include_deps == None:
            file_include_deps = config_file_include_deps_supply.get_file_include_deps()
        if file_to_module_map == None:
            if file_to_module_map_supply == None:
                file_to_module_map_supply = config_file_to_module_map_supply
            self.__individual_to_input_aggregate_map = file_to_module_map_supply.generate_file_to_module_map()
        else:
            self.__individual_to_input_aggregate_map = file_to_module_map
        self.__file_include_dependencies = file_include_deps
        self.__module_map = dict()
        self.__include_path_mapper = get_default_include_path_mapping()
        self.__edges_for_modules = None
        self.__graph = None
        self.__include_internal_links = include_internal_links

    def remove_suffixes(self, module):
        if module not in self.__module_map:
            self.__module_map[module] = VirtualModuleTypes.remove_suffixes(module)
        return self.__module_map[module]

    def process_for_all_file_deps(self, process_func):
        for from_file, to_file in self.__file_include_dependencies:
            if from_file in self.__individual_to_input_aggregate_map and \
               to_file in self.__individual_to_input_aggregate_map and \
               (self.__include_internal_links or self.__individual_to_input_aggregate_map[from_file] != self.__individual_to_input_aggregate_map[to_file]):
                from_file_module = self.remove_suffixes(self.__individual_to_input_aggregate_map[from_file])
                to_file_module = self.remove_suffixes(self.__individual_to_input_aggregate_map[to_file])
                process_func(from_file, from_file_module, to_file, to_file_module)

    def process_for_all_file_deps_matching_modules(self, process_func, from_module, to_module):
        self.process_for_all_file_deps(lambda from_file, from_file_module, to_file, to_file_module: \
                                       process_func(from_file, to_file) if from_module == from_file_module and to_module == to_file_module else None)


    def __create_edge(self, edges, from_file, to_file):
        # TODO strip external absolute base dirs and replace by <name of external module>
        from_file_stripped = self.__include_path_mapper.map_dir_to_external_module(from_file)
        to_file_stripped = self.__include_path_mapper.map_dir_to_external_module(to_file)
        edges.append(SimpleEdge(from_file_stripped, to_file_stripped))

    def __create_edge_2(self, from_file, from_file_module, to_file, to_file_module):
        if (from_file_module, to_file_module) not in self.__edges_for_modules:
            self.__edges_for_modules[(from_file_module, to_file_module)] = []
        self.__create_edge(self.__edges_for_modules[(from_file_module, to_file_module)], from_file, to_file)

    def __create_edges_for_modules(self):
        self.__edges_for_modules = dict()
        self.process_for_all_file_deps(self.__create_edge_2)

    def edges_for_modules(self, from_module, to_module):
        if self.__edges_for_modules == None:
            self.__create_edges_for_modules()
        if (from_module, to_module) in self.__edges_for_modules: 
            retval = self.__edges_for_modules[(from_module, to_module)]
        else:
            retval = ()
        #del self.__edges_for_modules[(from_module, to_module)]
        # TODO ist das sicher so?
        return retval

    def graph_for_modules(self, from_module, to_module):
        graph = MutableAttributeGraph()
        self.__graph = graph
        self.process_for_all_file_deps_matching_modules(graph.add_edge_and_nodes, from_module, to_module)        
        self.__graph = None
        return graph

    def graph_for_from_module(self, from_modules):
        if isinstance(from_modules, basestring):
            from_modules = (from_modules, )
        graph = MutableAttributeGraph()
        self.__graph = graph
        self.process_for_all_file_deps(lambda from_file, from_file_module, to_file, to_file_module: \
                                       graph.add_edge_and_nodes(from_file, to_file) if from_file_module in from_modules else None)
        self.__graph = None
        return graph

    
class ModuleIncludeLinkDetailsDecorator(BaseEdgeDecorator):
    def __init__(self, fidp):
        BaseEdgeDecorator.__init__(self)
        assert isinstance(fidp, FileIncludeDepsProcessor)
        self.__fidp = fidp
        
    def _format_file_pair(self, pair):
        return "%s -> %s" % pair

    def __format(self, edges_list):
#        if len(edges_list) > 0 and isinstance(edges_list[0], tuple):
#            return set(self._format_file_pair(edge) for edge in edges_list)
#        else:
        return set(self._format_file_pair((edge.get_from_node(), edge.get_to_node())) 
                   for edge in edges_list) 
         
    
    def as_iterable(self, node):
        if isinstance(node, NodeGroup):
            nodes = self._graph().node_attr(node, NodeAttributes.GROUPED_NODES)
        else:
            nodes = (node,) 
        return nodes

    def decorate(self, graph_element):
        
        from_nodes = self.as_iterable(graph_element.get_from_node())
        to_nodes = self.as_iterable(graph_element.get_to_node())
        
        result = list()
        for from_node in from_nodes:
            for to_node in to_nodes:
                # TODO das ist so nicht ganz richtig, eigentlich müsste das schon bei den Knoten
                # selbst ersetzt werden, und zwar wohl nur für die Quell-, nicht für die Zielknoten
                result.extend(self.__fidp.edges_for_modules(VirtualModuleTypes.remove_suffixes(from_node),
                                                            VirtualModuleTypes.remove_suffixes(to_node)))
        
        return list(self.__format(result))

class ModuleIncludeLinkTargetDetailsDecorator(ModuleIncludeLinkDetailsDecorator):
    
    def _format_file_pair(self, pair):
        return "%s" % (pair[1])

    def decorate(self, graph_element):
        return ["[from module %s]" % graph_element.get_from_node()] + \
            ModuleIncludeLinkDetailsDecorator.decorate(self, graph_element)
