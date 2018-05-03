# -*- coding: UTF-8 -*-
'''
Contains basic interfaces for graph data structures.

@todo: This is planned to be replaced by pygraph 

Created on 05.10.2010

@author: SIGIESEC
'''

class Node(object):
    def get_id(self):
        raise NotImplementedError(self.__class__)

class LabelledNode(Node):
    def get_label(self):
        raise NotImplementedError(self.__class__)

    def set_label(self, _label):
        raise NotImplementedError(self.__class__)

class Edge(object):
    """
    Implementations of Edge should implement __hash__, __eq__, __ne__ in addition,
    and  __lt__, __gt__ if sorting should be supported.
    """
    def get_from_node(self):
        raise NotImplementedError(self.__class__)

    def get_to_node(self):
        raise NotImplementedError(self.__class__)
    
    def node_set(self):
        raise NotImplementedError(self.__class__)
    
    def node_tuple(self):
        raise NotImplementedError(self.__class__)


class BasicGraph(object):
    def edges(self):
        raise NotImplementedError(self.__class__)

    def nodeitems_iter(self):
        raise NotImplementedError(self.__class__)

    def nodes_raw(self):
        raise NotImplementedError(self.__class__)
    
    def node_names_iter(self):
        raise NotImplementedError(self.__class__)

    def node_names(self):
        raise NotImplementedError(self.__class__)
    
    def node_count(self):
        raise NotImplementedError(self.__class__)

    def edge_count(self):
        raise NotImplementedError(self.__class__)
    

class MutableGraph(BasicGraph):
    """
    A generic interface for manipulating graphs.
    """

    # TODO A "Node" class should be used for __nodes
    # TODO An "Edge" class should be used for __edges, with a default "SimpleEdge" implementation 

    def add_edge(self, _edge):
        """
        Adds an edge to the graph. The required type of <edge> depends on the implementation.
        """
        raise NotImplementedError(self.__class__)

    def add_node(self, _node, _allowChange = False):
        raise NotImplementedError(self.__class__)

    def change_node(self, node):
        raise NotImplementedError(self.__class__)

    def del_node(self, _node):
        raise NotImplementedError(self.__class__)
