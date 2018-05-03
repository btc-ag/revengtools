#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 23.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import DependencyFilter
from commons.graph.graph_util import GraphConversions
from cpp.cpp_if import VirtualModuleTypes
from cpp.incl_deps.include_link_lifter_if import ModuleLinks
import logging
import re

class ModuleLinksImpl(ModuleLinks):
    FROM = 0
    TO = 1
    
    def __init__(self, combined_modules, node_restriction_in = None):
        self.combined_modules = combined_modules
        self.node_restriction_in = node_restriction_in
        self.__links = set()
        self.__incoming_link_counts = dict()
        self.__logger = logging.getLogger("cpp.incl_deps.include_link_lifter")

    def __initialize_universal_output(self):
        # TODO das sollte nur einmal gemacht werden. Anschließend darf add oder rename_node 
        # nicht mehr aufgerufen werden.
        all_nodes = GraphConversions.nodes_in_edge_list(self.__links) 
        decl_nodes = set(node 
                         for node in all_nodes 
                         if node.endswith(VirtualModuleTypes.DeclarationModule.suffix()))
        all_node_map = dict(
            [(node, node) 
             for node in all_nodes 
             if node not in decl_nodes] + \
            [(node, node.replace(VirtualModuleTypes.DeclarationModule.suffix(), "")) 
             for node in decl_nodes])
        return all_nodes, all_node_map, decl_nodes

    def universal_output(self, outputter):
        all_nodes, all_node_map, _decl_nodes = self.__initialize_universal_output()
        
        node_restriction = None
        if self.node_restriction_in != None:
            node_restriction = [node 
                                for node in all_nodes 
                                if any([re.match(regexp, node) for regexp in self.node_restriction_in])]
            if len(node_restriction) > 0:
                all_nodes = node_restriction
            else:
                self.__logger.warning("Node restriction %s does not match any node!" % (self.node_restriction_in,))
        for (from_node, to_node) in sorted(list(self.__links)):
            if self.combined_modules:
                from_node = all_node_map[from_node]
                to_node = all_node_map[to_node]
                    
            if from_node != to_node and (node_restriction == None or (from_node in node_restriction or to_node in node_restriction)):
                outputter.dependency(from_node, to_node)
        outputter.postamble()
        
    def get_incoming_link_counts(self):
        all_nodes, all_node_map, decl_nodes = self.__initialize_universal_output()
        for to_node in all_nodes:
            if (all_node_map[to_node] not in all_nodes or \
                (to_node not in decl_nodes  \
                 and self.combined_modules)):
                incoming_link_count = len([from_node2 
                                           for (from_node2, to_node2) in self.__links 
                                           if all_node_map[to_node] == all_node_map[to_node2]])
                self.__incoming_link_counts[all_node_map[to_node]] = incoming_link_count 
        return self.__incoming_link_counts

    def rename_node(self, old_name, new_name):
        self.__links |= set([(from_node, new_name) 
                             for (from_node, to_node) in self.__links 
                             if to_node == old_name])
        self.__links -= set([(from_node, to_node) 
                             for (from_node, to_node) in self.__links 
                             if to_node == old_name])
        self.__links |= set([(new_name, to_node) 
                             for (from_node, to_node) in self.__links 
                             if from_node == old_name])
        self.__links -= set([(from_node, to_node) 
                             for (from_node, to_node) in self.__links 
                             if from_node == old_name])
        
    def __incoming_links(self, node):
        return len(filter(lambda edge: edge[self.TO] == node, self.__links))
    
    def __outgoing_links(self, node):
        return len(filter(lambda edge: edge[self.FROM] == node, self.__links))
        
    def join_regular_incs(self):
        for inc_module in [to_node 
                           for (_from_node, to_node) in self.__links
                           if to_node.endswith(VirtualModuleTypes.HeaderModule.suffix()) 
                           and self.__incoming_links(to_node) == 1 
                           and self.__outgoing_links(to_node) == 0 
                           and (to_node.replace(VirtualModuleTypes.HeaderModule.suffix(), ''), to_node,) in self.__links]:
            self.__logger.info("Joining inc module %s with base module" % (inc_module,))
            self.__links.remove((inc_module.replace(VirtualModuleTypes.HeaderModule.suffix(), ''), 
                                 inc_module,))
            self.rename_node(inc_module.replace(VirtualModuleTypes.HeaderModule.suffix(), ''), 
                             inc_module.replace(VirtualModuleTypes.HeaderModule.suffix(), '_INC'))

    def add(self, element):
        assert isinstance(element, tuple) and len(element) == 2
        self.__links.add(element)


    
    
