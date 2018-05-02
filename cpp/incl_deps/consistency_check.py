#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 24.09.2010

@author: SIGIESEC
'''
from commons.graph.attrgraph_util import AttributedEdge, AttributeGraph, \
    AttributeGraphAlgorithms
from commons.graph.output_util import OutputMultiGraphTools
from cpp.cpp_if import VirtualModuleTypes

class RawConsistencyChecker(object):
    def __init__(self):
        self.__irregular_link_deps = None
        self.__missing_link_deps = None

    @staticmethod
    def __calculate_missing_link_deps(module_link_deps, module_include_deps):
        missing_link_deps = set(module_include_deps) - set(module_link_deps)
        for edge in list(missing_link_deps):
            assert isinstance(edge, AttributedEdge)
            to_module = str(edge.get_to_node())
            if to_module.endswith(VirtualModuleTypes.HeaderModule.suffix() + 
                                  VirtualModuleTypes.ExtensionSubmodule.suffix()):
                missing_link_deps.remove(edge)
            # TODO move this exception to a proper location
            if to_module.startswith("BTC.CAB.Commons.CoreX"):
                missing_link_deps.remove(edge)
                
        return missing_link_deps

    @staticmethod
    def __calculate_irregular_link_deps(module_link_deps, module_include_deps):
        module_include_deps_graph = AttributeGraph(edges=module_include_deps, do_deepcopy=False)
        return module_link_deps - AttributeGraphAlgorithms.transitive_closure_from_graph(module_include_deps_graph)

    def check_consistency(self, module_link_deps, module_include_deps):
        # TODO diese Method ist eigentlich überflüssig
        self.__missing_link_deps = self.__calculate_missing_link_deps(module_link_deps, module_include_deps)
        self.__irregular_link_deps = self.__calculate_irregular_link_deps(module_link_deps, module_include_deps)

    def get_missing_link_deps(self):
        return self.__missing_link_deps
    
    def get_irregular_link_deps(self):
        return self.__irregular_link_deps

class ConsistencyChecker(object):
    def __init__(self, link_deps_graph, include_deps_graph, node_group_conf):
        self.__combined_graph = None
        self.__overview_combined_graph = None
        self.__module_link_deps_graph = link_deps_graph
        self.__module_include_deps_graph = include_deps_graph
        self.__missing_link_deps_graph = None
        self.__irregular_link_deps_graph = None
        self.__node_group_conf = node_group_conf
        self.__calculate_everything()
    
    def __get_combined_include_link_deps_graph(self, checker, include_deps_graph, overview):
        assert isinstance(checker, RawConsistencyChecker)
        base_graph = include_deps_graph.immutable()
        superfluous_deps = checker.get_missing_link_deps() # missing link deps are superfluous links w.r.t. include graph
        missing_deps = checker.get_irregular_link_deps() # irregular link deps are missing in include graph
        
        if overview:
            node_group_conf=self.__node_group_conf
        else:
            node_group_conf=None
        
        multigraph = OutputMultiGraphTools.construct_superfluous_missing_multigraph(base_graph,
                                                                              superfluous_deps,
                                                                              missing_deps,
                                                                              node_group_conf=node_group_conf,
                                                                              )
        return multigraph

    
    def __calculate_everything(self):
        checker = RawConsistencyChecker()
        checker.check_consistency(module_link_deps=self.__module_link_deps_graph.edges(),
                                  module_include_deps=self.__module_include_deps_graph.edges())
        self.__combined_graph = self.__get_combined_include_link_deps_graph(checker, 
                                                                            self.__module_include_deps_graph,
                                                                            False)
        self.__overview_combined_graph = self.__get_combined_include_link_deps_graph(checker, 
                                                                            self.__module_include_deps_graph,
                                                                            True)
        self.__missing_link_deps_graph = AttributeGraph(edges=checker.get_missing_link_deps())
        self.__irregular_link_deps_graph = AttributeGraph(edges=checker.get_irregular_link_deps())
    
    def get_combined_graph(self):
        return self.__combined_graph

    def get_overview_combined_graph(self):
        return self.__overview_combined_graph

    def get_module_link_deps_graph(self):
        return self.__module_link_deps_graph

    def get_module_include_deps_graph(self):
        return self.__module_include_deps_graph

    def get_missing_link_deps_graph(self):
        return self.__missing_link_deps_graph

    def get_irregular_link_deps_graph(self):
        return self.__irregular_link_deps_graph
