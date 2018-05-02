# -*- coding: UTF-8 -*-
'''
Created on 01.10.2010

@author: SIGIESEC
'''
from commons.core_util import CollectionTools, frozendict
from commons.graph.attrgraph_if import NodeAttributes
from commons.graph.graph_if import Node, BasicGraph
from commons.graph.graph_util import SimpleEdge, GraphAlgorithms, SCCHelper
from commons.v26compat_util import compatchain
from copy import deepcopy
from itertools import imap
from types import NoneType
import warnings

class AttributedEdge(SimpleEdge):

    def __init__(self, attrs=None, mutable=True, *args, **kwargs):
        SimpleEdge.__init__(self, *args, **kwargs)
        if attrs == None:
            self.__attrs = dict()
        else:
            self.__attrs = dict(attrs)
        self.__mutable = mutable

    def __repr__(self, *args, **kwargs):
        return "<%s(%s -> %s, attrs=%s)>" % (self.__class__.__name__, 
                                             repr(self.get_from_node()), 
                                             repr(self.get_to_node()), 
                                             self.__attrs)


    def get_attr(self, name):
        return self.__attrs[name]

    def get_attrs(self):
        return dict(self.__attrs)

    def set_attr(self, name, value):
        if self.__mutable:
            self.__attrs[name] = value
        else:
            raise TypeError("Edge is immutable")

    def set_attrs(self, dictionary):
        if self.__mutable:
            self.__attrs.update(dictionary)
        else:
            raise TypeError("Edge is immutable")

    def get_attr_names(self):
        return self.__attrs.keys()

    def __len__(self):
        return len(self.__attrs)

class NodeGroup(Node):
    def __init__(self, name):
        assert isinstance(name, basestring)
        self.__name = name
        
    def name(self):
        return self.__name

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def __str__(self):
        return "<%s>" % self.__name



class AttributeGraph(BasicGraph):
    # TODO hier ist ein wenig durcheinander... Unterscheiden, ob ein Graph nur SimpleEdges besitzt oder auch
    # andere...
    # TODO eigentlich müsste klar definiert sein, was der Schlüssel eines Knoten bzw. einer Kante ist.

    def __copy_graph(self, graph, do_deepcopy):
        assert isinstance(graph, BasicGraph)
        if do_deepcopy:
            self.__edges = deepcopy(set(graph.edges()))
            self.__nodes = deepcopy(dict(graph.nodeitems_iter()))
        else:
            self.__edges = set(graph.edges())
            self.__nodes = dict(graph.nodeitems_iter())
        for node in self.__nodes:
            if isinstance(node, NodeGroup):
                self.__leaves.update(self.__nodes[node].get(NodeAttributes.GROUPED_NODES))
            else:
                self.__leaves.add(node)

    def __copy_edges_and_node(self, nodes, edges, do_deepcopy):
        if edges != None:
            if do_deepcopy:
                self.__edges = deepcopy(set(edges))
            else:
                self.__edges = edges
            #self.__edges = set([AttributedEdge(source, target) for (source, target) in edges])
            if nodes == None:
                self.__nodes = dict()
                for node in CollectionTools.union_all(edge.node_set() for edge in self.__edges):
                    self.__nodes[node] = dict()

        if nodes != None:
            if do_deepcopy:
                self.__nodes = deepcopy(nodes)
            else:
                self.__nodes = nodes
            if edges == None:
                self.__edges = set()

    def __init__(self, nodes=None, edges=None, graph=None, do_deepcopy=True, default_edge_attrs=dict()):
        self.__default_edge_attrs = default_edge_attrs
        self.__leaves = set()
        self.__edges = None
        self.__nodes = None
        if graph != None:
            self.__copy_graph(graph, do_deepcopy)
        elif nodes != None or edges != None:
            self.__copy_edges_and_node(nodes, edges, do_deepcopy)
        else:
            self.__edges = set()
            self.__nodes = dict()

    def __repr__(self, *args, **kwargs):
        return "<%s(%i nodes, %i edges)>" % (self.__class__.__name__, len(self.__nodes), len(self.__edges))

    def node_names_iter(self):
        return imap(str, self.__nodes.iterkeys())

    def node_count(self):
        return len(self.__nodes)

    def node_names(self):
        return tuple(self.node_names_iter())

    def leaf_names(self):
        return tuple(self.__leaves)

    def nodes_raw(self):
        return tuple(self.__nodes.keys())

    def edgeitems(self):
        raise NotImplementedError("use individual edges")

    def nodeitems_iter(self):
        return self.__nodes.iteritems()

    def edges(self):
        return frozenset(self._edges())

    def _edges(self):
        return self.__edges

    def _nodes(self):
        return self.__nodes

    def _remove_node(self, node):
        remove_edges = []
        for edge in self.__edges:
            if edge.get_from_node() == node or edge.get_to_node() == node:
                remove_edges.append(edge)
        self.__edges.difference_update(remove_edges)
        self._del_node_only(node)

    def _del_node_only(self, node):
        del self.__nodes[node]
        self.__leaves.discard(node)

    def _add_node(self, node):
        if node not in self._nodes():
            self.__nodes[node] = dict()
            if not isinstance(node, NodeGroup):
                self.__leaves.add(node)

    def _add_edge(self, source, target):
        if SimpleEdge(source, target) not in self.__edges:
            self.__edges.add(AttributedEdge(attrs=dict(self.__default_edge_attrs),
                                            from_node=source,
                                            to_node=target))

    def _remove_edge(self, source=None, target=None, edge=None):
        if not isinstance(edge, NoneType):
            self.__edges.remove(edge)
        else:
            self.__edges.remove(SimpleEdge(source, target))


    def has_node(self, node):
        return node in self.__nodes

    def has_edge(self, source, target):
        return SimpleEdge(source, target) in self.__edges

    def lookup_edge(self, source, target):
        # TODO das ist unnötig ineffizient (O(n)), vielleicht doch besser ein dict für die Kanten benutzen?
        for edge in self.__edges:
            if edge == SimpleEdge(source, target):
                return edge
        return None

    def edge_attr_names(self, source, target):
        warnings.warn("use edge.get_attr_names instead", DeprecationWarning)
        return self.lookup_edge(source, target).get_attr_names()

    def edge_attr(self, source, target, attr):
        warnings.warn("use edge.get_attr/set_attr/get_attr_names instead", DeprecationWarning)
        return self.lookup_edge(source, target).get_attr(attr)

    def _node_attrs(self, node, create=False):
        if node not in self.__nodes and create:
            self.__nodes[node] = dict()
        return self.__nodes[node]

    def node_attr_names(self, node):
        return self._node_attrs(node, False).keys()

    def node_attr(self, node, attr):
        return self._node_attrs(node).get(attr)

    def node_attrs(self, node):
        return frozendict(self._node_attrs(node))

    def edge_count(self):
        return len(self.__edges)

    def immutable(self):
        """
        Returns an immutable view of the graph. It is not a copy of the graph, i.e. if the object 
        that immutable is called on is mutable and is modified, these modifications will be visible
        on the immutable view.
        
        @rtype: AttributeGraph  
        """
        
        if type(self) == AttributeGraph:
            return self
        else:
            return AttributeGraph(graph=self, do_deepcopy=False)

    def mutable_copy(self):
        """
        Creates a mutable clone of this graph.
        
        @rtype: MutableAttributeGraph
        """
        return MutableAttributeGraph(graph=self)

class MutableAttributeGraph(AttributeGraph):

    def set_node_attrs(self, node, dictionary, create=False):
        self._node_attrs(node, create).update(dictionary)

    def set_edge_attrs(self, source, target, dictionary, create=False):
        warnings.warn("Deprecated, use edge.set_attrs instead")
        if create and not self.has_edge(source, target):
            self._add_edge(source, target)
        self.lookup_edge(source, target).set_attrs(dictionary)

    def override_edge_attrs(self, dictionary):
        for edge in self._edges():
            edge.set_attrs(dictionary)

    def add_node(self, node):
        self._add_node(node)

    def add_edge_and_nodes(self, source, target):
        if source not in self._nodes():
            self._add_node(source)
        if target not in self._nodes():
            self._add_node(target)
        self._add_edge(source, target)

    def add_edge(self, source, target):
        assert source in self._nodes(), "Source node %s does not exist" % source
        assert target in self._nodes(), "Target node %s does not exist" % target
        self._add_edge(source, target)

    def remove_edge(self, *args, **kwargs):
        self._remove_edge(*args, **kwargs)

    def remove_node(self, node):
        self._remove_node(node)

    def __del_node_only(self, node):
        """
        Delete only node, assume that it is unconnected.
        """
        self._del_node_only(node)

    def has_removed_edge(self, node):
        return any(attribute in self.node_attr_names(node) 
                   for attribute in
                   [NodeAttributes.SKIPPED_FROM_EDGE, NodeAttributes.SKIPPED_TO_EDGE])


    def connected_nodes(self):
        return CollectionTools.union_all(edge.node_set() for edge in self._edges())

    def unconnected_nodes(self):
        return set(self.nodes_raw()) - self.connected_nodes()

    def delete_unconnected_nodes(self, exception_func=lambda x: False):
        unconnected_nodes = self.unconnected_nodes()
        for node in unconnected_nodes:
            # TODO gehört das hierher?
            removed_edge_cond = self.has_removed_edge(node)
            exception_cond = not exception_func(node) 
            if removed_edge_cond and exception_cond:
                self.__del_node_only(node)


class AttributedMultiEdge(AttributedEdge):
    def __init__(self, multi_id, *args, **kwargs):
        AttributedEdge.__init__(self, *args, **kwargs)
        self.__multi_id = multi_id

    def _multi_id(self):
        return self.__multi_id

    def __hash__(self, *args, **kwargs):
        return hash((AttributedEdge.__hash__(self, *args, **kwargs), self.__multi_id))

    def __eq__(self, other):
        return AttributedEdge.__eq__(self, other) and self.__multi_id == other._multi_id()

    def __ne__(self, other):
        return AttributedEdge.__ne__(self, other) or self.__multi_id != other._multi_id()


class MultiGraph(BasicGraph):
    def __init__(self, input_graphs):
        assert all(isinstance(graph, AttributeGraph) for graph in input_graphs)
        self.__graphs = input_graphs
        self.__edges = None
        self.__nodes = None
        self.__attrs = dict()

    def __repr__(self, *args, **kwargs):
        return "<%s(%s)>" % (self.__class__.__name__,
                             ",".join(imap(repr, self.__graphs)))

    def node_count(self):
        return len(self.node_names())

    def edge_count(self):
        return len(self.edges())

    def nodeitems_iter(self):
        for node in self.nodes_raw():
            node_attrs = dict()
            for attr in self.node_attr_names(node):
                node_attrs[attr] = self.node_attr(node, attr)
            yield (node, node_attrs)

    def node_names_iter(self):
        return imap(str, self.nodes_raw())

    def node_names(self):
        return tuple(self.node_names_iter())

    def edges(self):
        # TODO Man darf aus dem Ergebnis aber keine Menge bilden!!
        if self.__edges == None:
            self.__edges = tuple(compatchain.from_iterable(graph.edges()
                                                     for graph in self.__graphs))
        return self.__edges

    def edge_iter(self):
        return compatchain.from_iterable(graph.edges() for graph in self.__graphs)

    def get_edges(self, source, target):
        result = []
        for graph in self.__graphs:
            if graph.has_edge(source, target):
                result.append(graph.lookup_edge(source, target))
        return result

    def nodes_raw(self):
        if self.__nodes == None:
            self.__nodes = frozenset(CollectionTools.union_all(graph.nodes_raw()
                                                               for graph in self.__graphs))
        return self.__nodes

    def node_attr_names(self, node):
        # TODO hier sieht man wie unsinnig das ist, die Attribute müssten ja bei allen gleich sein, 
        # dann kann man sie auch erst für den Multigraph berechnen.
        attr_names = set()
        for graph in self.__graphs:
            if graph.has_node(node):
                attr_names.update(graph.node_attr_names(node))
        if node in self.__attrs:
            attr_names.update(self.__attrs[node].keys())
        return attr_names

    def node_attr(self, node, attr):
        if node in self.__attrs and attr in self.__attrs[node]:
            return self.__attrs[node][attr]
        for graph in self.__graphs:
            if graph.has_node(node):
                node_attrs = graph.node_attr(node, attr)
                if node_attrs != None:
                    return node_attrs
        return None

    def set_node_attrs(self, node, attrs):
        if node not in self.__attrs:
            self.__attrs[node] = dict()
        self.__attrs[node].update(attrs)

class MultiGraphTools(object):
    @staticmethod
    def construct_generic_multigraph(base_graph, additional_graphs):
        assert isinstance(base_graph, AttributeGraph)

        mutable_base_graph = base_graph.mutable_copy()
        all_graphs = [mutable_base_graph]
        for graph, edge_attrs, remove_edges_from_basegraph in additional_graphs:
            graph.override_edge_attrs(edge_attrs)
            if remove_edges_from_basegraph:
                for edge in graph.edges():
                    mutable_base_graph.remove_edge(edge=edge)

            all_graphs.append(graph)

        multigraph = MultiGraph(all_graphs)
        return multigraph


class AttributeGraphAlgorithms(object):

    @staticmethod
    def transitive_closure_from_graph(graph):
        accessibility_matrix = GraphAlgorithms.accessibility_matrix_from_graph(graph)
        #result_graph = MutableAttributeGraph(nodes=graph.nodes_raw())
        result = set()
        for from_node, to_nodes in accessibility_matrix.iteritems():
            for to_node in to_nodes:
                if from_node != to_node:
                    # TODO Muss ich hier eine AttributedEdge nehmen, tut es nicht auch eine SimpleEdge?
                    result.add(AttributedEdge(from_node=from_node, to_node=to_node))
        return result

    @staticmethod
    def set_node_attrs_subgraph_dependent_on_nodes(graph, start_nodes, attrs):
        dependent_nodes = GraphAlgorithms.dependent_nodes(graph, start_nodes)

        for node in dependent_nodes:
            graph.set_node_attrs(node, attrs)

    @staticmethod
    def set_edge_attrs_subgraph_dependent_on_nodes(graph, start_nodes, attrs):
        dependent_nodes = GraphAlgorithms.dependent_nodes(graph, start_nodes)

        for edge in graph.edges():
            if edge.get_from_node() in dependent_nodes and edge.get_to_node() in dependent_nodes:
                if isinstance(edge, AttributedEdge):
                    edge.set_attrs(attrs)
                else:
                    raise ValueError("Trying to set attributes on non-attributed edge")

class SCCMerger(object):
    """
    Merges strongly connected components in a graph.
    """
    
    def __init__(self, base_graph):
        self.__scc_helper = SCCHelper(base_graph)
        self.__base_graph = base_graph
        
    def get_sccs_iter(self):
        return self.__scc_helper.get_sccs_iter()
        
    def get_scc_node_name(self, scc):
        return "_".join(sorted(compatchain.from_iterable(x.split("_") for x in scc)))

    def get_node_name(self, node):
        scc = self.__scc_helper.get_mutual_acc(node)
        if len(scc) == 1:
            return node
        else:
            return self.get_scc_node_name(scc)


    def __get_grouped_nodes(self, node):
        attr_group = self.__base_graph.node_attr(node, NodeAttributes.GROUPED_NODES)
        if attr_group:
            return attr_group
        else:
            return (node, )

    def get_scc_merged_graph(self):
        result_graph = MutableAttributeGraph()
        for node in self.__base_graph.node_names_iter():
            if self.__scc_helper.get_scc_number_of_node(node) == None:
                result_graph.add_node(node)
                result_graph.set_node_attrs(node, self.__base_graph.node_attrs(node))
                result_graph.set_node_attrs(node, {NodeAttributes.LABEL: ""})
        for scc in self.__scc_helper.get_sccs_iter():
            node_name = self.get_scc_node_name(scc)
            result_graph.add_node(node_name)
            all_base_nodes = CollectionTools.union_all(self.__get_grouped_nodes(node) 
                                                       for node in scc)
            result_graph.set_node_attrs(node_name, {NodeAttributes.GROUPED_NODES: all_base_nodes, NodeAttributes.LABEL: ""})
            
        for edge in self.__base_graph.edges():
            source = self.get_node_name(edge.get_from_node())
            target = self.get_node_name(edge.get_to_node())
            if source != target:
                result_graph.add_edge(source, target)
        return result_graph


# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
