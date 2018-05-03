# -*- coding: UTF-8 -*-

'''
Created on 12.06.2010

@author: sigiesec
'''
from commons.core_util import CollectionTools
from commons.graph.graph_if import (Node, LabelledNode, Edge, MutableGraph, 
    BasicGraph)
from itertools import imap, chain
from pygraph.algorithms.accessibility import accessibility, mutual_accessibility
from pygraph.algorithms.searching import depth_first_search
from pygraph.classes.digraph import digraph
import collections
import copy

class BaseNode(Node):
    def get_id(self):
        return hash(self)

class SimpleNode(BaseNode, LabelledNode):
    def __init__(self, label):
        LabelledNode.__init__(self)
        self._label = None
        self.set_label(label)

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

class SetNode(SimpleNode):
    def set_label(self, label):
        assert(isinstance(label, collections.Iterable))
        if not isinstance(label, frozenset):
            SimpleNode.set_label(self, frozenset(label))
        else:
            SimpleNode.set_label(self, label)

class TupleNode(SimpleNode):
    def set_label(self, label):
        assert(isinstance(label, collections.Iterable))
        if not isinstance(label, tuple):
            SimpleNode.set_label(self, tuple(label))
        else:
            SimpleNode.set_label(self, label)

class FrozenLabelledNode(BaseNode, LabelledNode):
    def __init__(self, node):
        LabelledNode.__init__(self)
        self._node = copy.copy(node)

    def get_label(self):
        return self._node.get_label()

    def set_label(self, _label):
        raise Exception("Tried to modify frozen node")

class SimpleEdge(Edge):
    def __init__(self, from_node, to_node):
        Edge.__init__(self)
        self.__from = from_node
        self.__to = to_node

    def get_from_node(self):
        return self.__from

    def get_to_node(self):
        return self.__to

    def node_set(self):
        return set((self.__from, self.__to))

    def node_tuple(self):
        return (self.__from, self.__to)

    def __hash__(self, *args, **kwargs):
        return hash((self.__from, self.__to))

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        else:
            return (self.__from, self.__to) == (other.get_from_node(), other.get_to_node())

    def __ne__(self, other):
        if not isinstance(other, Edge):
            return True
        else:
            return (self.__from, self.__to) != (other.get_from_node(), other.get_to_node())

    def __lt__(self, other):
        return (self.__from, self.__to) < (other.get_from_node(), other.get_to_node())

    def __gt__(self, other):
        return (self.__from, self.__to) > (other.get_from_node(), other.get_to_node())

class BaseMutableGraph(MutableGraph):
    def change_node(self, node):
        self.add_node(node, True)

class PartitionGraph(BaseMutableGraph):
    """
    A graph whose nodes are a partition of some base set. It has the following properties: 
    Nodes are tuples of a name and a tuple-valued label, which must be disjoint across all nodes. 
    Edges are pairs of node names.
    """

    def __init__(self):
        BaseMutableGraph.__init__(self)
        self.__edges = set()
        self.__nodes = dict()

    def check_edge(self, edge):
        if not isinstance(edge, tuple) and len(edge) == 2:
            raise TypeError("Not an edge: %s (%s)" % (str(edge), type(edge)))

    def check_node(self, node):
        if not (isinstance(node, tuple) and len(node) == 2 and
                isinstance(node[0], str) and isinstance(node[1], tuple)):
            raise TypeError(
                "Not a node: %s %s (expected type tuple(str, tuple))"
                % (str(node), type(node)))

    def add_edge(self, edge):
        """
        xxx
        """
        self.check_edge(edge)
        if edge[0] not in self.__nodes:
            raise ValueError("Node not found: %s" % edge[0])
        if edge[1] not in self.__nodes:
            raise ValueError("Node not found: %s" % edge[1])
        if edge[0] != edge[1]:
            self.__edges.update(set([edge]))
        return

    def find_overlapping_nodes(self, node):
        """
        Returns the list of node names that overlap with the label of node <node>.
        
        >>> x = PartitionGraph()
        >>> node = ('node1', ('x', 'y'))
        >>> x.add_node(node)
        >>> list(x.find_overlapping_nodes(node))
        []
        >>> node = ('node2', ('x', 'y'))
        >>> list(x.find_overlapping_nodes(node))
        ['node1']
        """
        self.check_node(node)
        return (x for x in self.__nodes
                if x != node[0] and set(self.__nodes[x]).intersection(set(node[1])))

    def add_node(self, node, allowChange=False):
        """
        >>> x = PartitionGraph()
        >>> x.add_node(("node", ("label",)))
        >>> x.add_node(("node", ("label",))) 
        >>> x.node_count()
        1
        >>> x.add_node(("node", ("label2",))) # doctest:+ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Inserting node with different value: old = ('label',), new = ('label2',)
        """
        self.check_node(node)
        if node[0] in self.__nodes:
            if not allowChange and self.__nodes[node[0]] != node[1]:
                raise ValueError("Inserting node with different value: old = %s, new = %s" % (self.__nodes[node[0]], node[1]))

        overlaps = list(self.find_overlapping_nodes(node))
        if len(overlaps) > 0:
            raise ValueError("Overlapping node exists: new = %s:%s, old = %s:%s"
                             % (node[0], node[1], overlaps,
                                imap(self.__nodes, overlaps)))
        self.__nodes.update({node[0]: node[1]})
        return

    def in_links(self, nodeName):
        """
        Returns the number of incoming links of the node named <nodeName>.
        
        >>> x = PartitionGraph()
        >>> x.add_node(("node", ("label",)))
        >>> x.add_node(("node2", ("label2",)))
        >>> x.add_edge(("node", "node2"))
        >>> x.in_links("node")
        0
        >>> x.in_links("node2")
        1
        """
        return sum(1 for edge in self.__edges if edge[1] == nodeName)

    def out_links(self, nodeName):
        """
        Returns the number of outgoing links of the node named <nodeName>.
        
        >>> x = PartitionGraph()
        >>> x.add_node(("node", ("label",)))
        >>> x.add_node(("node2", ("label2",)))
        >>> x.add_edge(("node", "node2"))
        >>> x.out_links("node")
        1
        >>> x.out_links("node2")
        0
        """
        return sum(1 for edge in self.__edges if edge[0] == nodeName)

    def _missing_nodes(self):
        """
        Returns __nodes that are referenced in an edge but not contained in the list of __nodes. 
        Result should always be empty.
        """
        missingNodes = list()
        for (fromNode, toNode) in self.__edges:
            if fromNode not in self.__nodes:
                missingNodes.append(fromNode)
            if toNode not in self.__nodes:
                missingNodes.append(toNode)
        return missingNodes

    def del_node(self, nodeName):
        if nodeName in self.__nodes:
            self.__edges.difference_update(set(edge
                                               for edge in self.__edges
                                               if edge[1] == nodeName or edge[0] == nodeName))
            del self.__nodes[nodeName]
        else:
            raise ValueError("Node %s not found" % (nodeName))

    def join_nodes(self, targetNodeName, sourceNodeName):
        """
        
        @param targetNodeName:
        @type targetNodeName:
        @param sourceNodeName:
        @type sourceNodeName:
        
        >>> x = PartitionGraph()
        >>> x.add_node(("node", ("label",)))
        >>> x.add_node(("node2", ("label2",)))
        >>> x.add_node(("node3", ("label3",)))
        
        >>> y = copy.deepcopy(x) 
        >>> y.add_edge(("node2", "node3"))
        >>> y.join_nodes("node", "node2")
        >>> y.node_count()
        2
        >>> y.edge_count()
        1
        
        >>> y = copy.deepcopy(x)       
        >>> y.add_edge(("node2", "node2"))
        >>> y.join_nodes("node", "node2")
        >>> y.node_count()
        2
        
        # see comment below
        #>>> y.edge_count()
        #1

        >>> y = copy.deepcopy(x) 
        >>> y.add_edge(("node2", "node2"))
        >>> y.add_edge(("node", "node"))
        >>> y.join_nodes("node", "node2")
        >>> y.node_count()
        2

        # see comment below
        #>>> y.edge_count()
        #1

        >>> y = copy.deepcopy(x) 
        >>> y.add_edge(("node", "node2"))
        >>> y.join_nodes("node", "node2")
        >>> y.node_count()
        2
        >>> y.edge_count()
        1
        """
        if sourceNodeName not in self.__nodes:
            raise ValueError("Source node %s not found" % (sourceNodeName,))
        if targetNodeName not in self.__nodes:
            raise ValueError("Target node %s not found" % (targetNodeName,))

        # TODO Wie soll das Verhalten sein, wenn es eine Kanten des sourceNode 
        #      auf sich selbst gab? Nach der derzeitigen Implementierung 
        #      verschwindet diese, aber eigentlich müsste sie durch eine Kante
        #      des targetNode auf sich selbst ersetzt werden.
        self.__edges.update(set((edge[0], targetNodeName)
                               for edge in self.__edges
                               if edge[1] == sourceNodeName
                               and edge[0] != sourceNodeName))

        self.__edges.update(set((targetNodeName, edge[1])
                               for edge in self.__edges
                               if edge[0] == sourceNodeName
                               and edge[1] != sourceNodeName))

        self.__nodes.update({targetNodeName: tuple(sorted(list(self.__nodes[targetNodeName])
                                                    + list(self.__nodes[sourceNodeName])))})
        self.del_node(sourceNodeName)

    def node_count(self):
        return len(self.__nodes)

    def edge_count(self):
        return len(self.__edges)

class GraphConversions(object):
    @staticmethod
    def nodes_in_edge_list(edge_list):
        """
        >>> sorted(GraphConversions.nodes_in_edge_list([('a', 'b'), ('b', 'c')]))        
        ['a', 'b', 'c']
        """
        nodes = CollectionTools.union_all(((source for (source, _target) in edge_list),
                                           (target for (_source, target) in edge_list)))
        return nodes

    @staticmethod
    def edge_list_to_pygraph(edge_list, ignore_duplicate_edges=False):
        graph = digraph()
        nodes = GraphConversions.nodes_in_edge_list(edge_list)
        for node in nodes:
            graph.add_node(node)

        for edge in edge_list:
            if not ignore_duplicate_edges or not graph.has_edge(edge): 
                graph.add_edge(edge)

        return graph

    @staticmethod
    def graph_to_pygraph(graph, inverse=False):
        assert isinstance(graph, BasicGraph)
        pygraph = digraph()
        pygraph.add_nodes(graph.node_names())
        for edge in graph.edges():
            cur_tuple = edge.node_tuple()
            if inverse:
                cur_tuple = (cur_tuple[1], cur_tuple[0])
            if not pygraph.has_edge(cur_tuple):
                pygraph.add_edge(cur_tuple)
        return pygraph

class GraphAlgorithms(object):
    @staticmethod
    def accessibility_matrix_from_graph(graph, inverse=False):
        pygraph = GraphConversions.graph_to_pygraph(graph, inverse=inverse)
        accessibility_matrix = accessibility(pygraph)
        return accessibility_matrix

    @staticmethod
    def transitive_closure_from_pygraph_as_edge_list(pygraph):
        accessibility_matrix = accessibility(pygraph)
        result = set()
        for from_node, to_nodes in accessibility_matrix.iteritems():
            for to_node in to_nodes:
                if from_node != to_node:
                    result.add((from_node, to_node))

        return result

    @staticmethod
    def transitive_closure(edge_list):
        """
        Transitive, non-reflexive closure as a list of edges.
        
        >>> sorted(GraphAlgorithms.transitive_closure([('a', 'b'), ('b', 'c')]))
        [('a', 'b'), ('a', 'c'), ('b', 'c')]
        """
        pygraph = GraphConversions.edge_list_to_pygraph(edge_list, ignore_duplicate_edges=True)
        result = GraphAlgorithms.transitive_closure_from_pygraph_as_edge_list(pygraph)
        return result

    @staticmethod
    def dependent_nodes(graph, start_nodes):
        """
        >>> graph = GraphConversions.edge_list_to_pygraph([('a', 'b'), ('b', 'c'), ('a', 'c')])
        >>> sorted(GraphAlgorithms.dependent_nodes(graph, ['c']))
        ['a', 'b', 'c']
        """
        if isinstance(graph, BasicGraph): 
            accessibility_matrix = GraphAlgorithms.accessibility_matrix_from_graph(graph, inverse=True)
        elif isinstance(graph, digraph):
            accessibility_matrix = accessibility(graph.reverse())
        else:
            raise TypeError("%s is not a known graph type", graph)
#        dependent_nodes = set()
#        for start_node in start_nodes:
#            if start_node in accessibility_matrix:
#                dependent_nodes.update(accessibility_matrix[start_node])
#        return dependent_nodes

        # TODO ist das effizienter als
        return CollectionTools.union_all(accessibility_matrix[start_node]
                                         for start_node in start_nodes
                                         if start_node in accessibility_matrix)


    @staticmethod
    def remove_subgraph_dependent_on_nodes(graph, start_nodes):
        dependent_nodes = GraphAlgorithms.dependent_nodes(graph, start_nodes)

        for node in dependent_nodes:
            # TODO hierbei betroffene Knoten mit SKIPPED_FROM_EDGE/SKIPPED_TO_EDGE markieren!
            graph.remove_node(node)

        graph.delete_unconnected_nodes()
        
    @classmethod
    def cut_branches(cls, cut_obj_ids, edges):
        return set(edge for edge in edges if edge[0] not in set(cut_obj_ids))
        
#        graph = GraphConversions.edge_list_to_pygraph(edges, ignore_duplicate_edges=False) # TODO this is also done in drop_unreachable!
#        
#        remove_edges = set()
#        for cut_obj_id in cut_obj_ids:
#            if graph.has_node(cut_obj_id):
#                spanning_tree = depth_first_search(graph, root=cut_obj_id)[0]
#                for node in spanning_tree.iterkeys():
#                    neighbors = graph.neighbors(node)
#                    remove_edges.update((node,target) for target in neighbors)
#        
#        return set(edges).difference(remove_edges)

    @classmethod
    def remove_branches(cls, cut_nodes, edges, target_nodes):
        new_edges = cls.cut_branches(cut_nodes, edges)
        nodes = set(GraphAlgorithms.dependent_nodes(GraphConversions.edge_list_to_pygraph(new_edges), start_nodes=target_nodes))
        return set(edge for edge in new_edges if edge[1] in nodes)


class SCCHelper(object):
    def __init__(self, graph):
        pygraph = GraphConversions.graph_to_pygraph(graph)
        self.__mutual_acc = mutual_accessibility(pygraph)
        self.__sccs = sorted(set(tuple(scc)
                                 for scc in self.__mutual_acc.values()
                                 if len(scc) > 1))
        
    def get_sccs_iter(self):
        return iter(self.__sccs)
        
    def get_scc_number_of_node(self, node):
        mutual_acc = self.get_mutual_acc(node)
        if len(mutual_acc) > 1:
            return self.get_scc_index_of_mutual_acc(mutual_acc)
        else:
            return None
    
    def get_mutual_acc(self, node):
        return tuple(self.__mutual_acc[node])
    
    def get_scc_index_of_mutual_acc(self, scc):
        return self.__sccs.index(tuple(scc))
    
    def get_scc_number_of_edge(self, edge):
        scc_candidate = self.get_mutual_acc(edge.get_from_node())
        if edge.get_to_node() in scc_candidate:
            return self.get_scc_index_of_mutual_acc(scc_candidate)
        else:
            return None
    
    def __str__(self):
        return str(self.__sccs)


# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()

