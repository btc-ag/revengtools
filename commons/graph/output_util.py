# -*- coding: UTF-8 -*-
'''
Created on 12.10.2010

@author: SIGIESEC
'''
from commons.graph.attrgraph_if import (NodeAttributes, EdgeAttributes,
    GraphShapes, Colors, EdgeStyles)
from commons.graph.attrgraph_util import (NodeGroup, MutableAttributeGraph,
    MultiGraphTools, AttributedEdge)
from commons.graph.graph_if import BasicGraph, Edge
from commons.graph.graph_util import GraphAlgorithms
from commons.graph.output_base import (BaseNodeDecorator, BaseEdgeDecorator,
    BaseGraphElementDecorator)
from commons.graph.output_if import NodeGroupingConfiguration
import logging

class NodeGroupDecorator(BaseNodeDecorator):
    #def __init__(self, *args, **kwargs):
    #    BaseEdgeDecorator.__init__(self, *args, **kwargs)

    def __format(self, nodes_list):
        return ["%s" % node for node in nodes_list]

    def decorate(self, graph_element):
        if NodeAttributes.GROUPED_NODES in self._graph().node_attr_names(graph_element):
            return self.__format(sorted(self._graph().node_attr(graph_element, NodeAttributes.GROUPED_NODES)))
        else:
            return self.__format([graph_element])

class EdgeGroupDecorator(BaseEdgeDecorator):
    #def __init__(self, *args, **kwargs):
    #    BaseEdgeDecorator.__init__(self, *args, **kwargs)

    def __format(self, edges_list):
        return ["%s -> %s" % (edge.get_from_node(), edge.get_to_node()) for edge in edges_list]

    def decorate(self, graph_element):
        if EdgeAttributes.GROUPED_EDGES in graph_element.get_attr_names():
            return self.__format(sorted(graph_element.get_attr(EdgeAttributes.GROUPED_EDGES)))
        else:
            return self.__format([graph_element])

class SubgraphDecorator(BaseEdgeDecorator, BaseNodeDecorator):
    def __init__(self,
                 node_attributes={NodeAttributes.LINE_COLOR: Colors.PURPLE},
                 edge_attributes={EdgeAttributes.COLOR: Colors.PURPLE,
                                  EdgeAttributes.WEIGHT: 5
                                  },
                 start_nodes=None, *args, **kwargs):
        BaseNodeDecorator.__init__(self, *args, **kwargs)
        self.__node_attributes = node_attributes
        self.__edge_attributes = edge_attributes
        self.__start_nodes = start_nodes

    def description(self):
        return "%s(%s)" % (self.__class__.__name__, self.__start_nodes)


    def decorate(self, graph_element):
        if isinstance(graph_element, Edge):
            edge = graph_element
            if edge.get_from_node() in self.__subgraph_nodes and edge.get_to_node() in self.__subgraph_nodes:
                if isinstance(edge, AttributedEdge):
                    edge.set_attrs(self.__edge_attributes)
                else:
                    raise ValueError("Trying to set attributes on non-attributed edge")
        else:
            node = graph_element
            if node in self.__subgraph_nodes:
                self._graph().set_node_attrs(node, self.__node_attributes)

    def subgraph_nodes(self):
        return self.__subgraph_nodes

    def get_start_nodes(self):
        assert self.__start_nodes != None, "Must either set start_nodes in constructor or overwrite get_start_nodes in subclass of SubgraphDecorator"
        return self.__start_nodes

    def attach_graph(self, graph):
        BaseGraphElementDecorator.attach_graph(self, graph)
        start_nodes = self.get_start_nodes()
        self.__subgraph_nodes = GraphAlgorithms.dependent_nodes(graph, start_nodes)

    def detach_graph(self):
        BaseGraphElementDecorator.detach_graph(self)
        self.__subgraph_nodes = None

class GraphCollapser(object):
    def __init__(self, inputgraph, node_group_conf):
        assert isinstance(inputgraph, BasicGraph)
        self.__inputgraph = inputgraph
        self.__node_group_conf = node_group_conf
        self.__resultgraph = None
        self.__original_nodes = None
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.debug("%s: inputgraph=%s, node_group_conf=%s" % (self.__class__.__name__, repr(inputgraph), repr(node_group_conf)))


    def __get_node_group_prefix_if_collapsing(self, node):
        node_group_prefix = self.__node_group_conf.get_node_grouper().get_node_group_prefix(node)
        do_collapse_node = node_group_prefix != None and self.__node_group_conf.collapse_node_group(node_group_prefix)
        if do_collapse_node:
            return node_group_prefix
        else:
            return None
        
    def __get_node_group_if_collapsing(self, node):
        node_group_prefix = self.__get_node_group_prefix_if_collapsing(node)
        if node_group_prefix:
            node_group = NodeGroup(node_group_prefix)
            if not self.__resultgraph.has_node(node_group):
                # TODO normalerweise sollte das nur beim Anlegen des Nodes geschehen, wenn aber
                # ein Node den gleichen Namen hat wie ein nicht kollabierter Node,
                # dann gibt es ihn schon. Vielleicht dafür sorgen, dass die Namen sich unterscheiden.
                self.__resultgraph.add_node(node_group)
                self.__resultgraph.set_node_attrs(node_group, {NodeAttributes.GROUPED_NODES: set()})
            else:
                if NodeAttributes.GROUPED_NODES not in self.__resultgraph.node_attr_names(node_group):
                    self.__logger.debug("weird... existing group node %s has no GROUPED_NODES attribute" % (node_group))
                    self.__resultgraph.set_node_attrs(node_group, {NodeAttributes.GROUPED_NODES : set()})
            self.__resultgraph.set_node_attrs(node_group,
                                              {NodeAttributes.SHAPE: GraphShapes.PACKAGE})
            return node_group
        else:
            return None

    def __check_replace_by_node_group(self, node):
        node_group = self.__get_node_group_if_collapsing(node)
        if node_group:
            return node_group
        else:
            return node


    def __collapse_edge(self, edge, source_new, target_new):
        edge_attrs = edge.get_attrs()
        self.__resultgraph.remove_edge(edge=edge)
        if source_new != target_new:
            new_edge = self.__resultgraph.lookup_edge(source_new, target_new)
            if new_edge == None:
                # TODO das wäre etwas einfacher, wenn man die Kante hier erzeugen würde
                self.__resultgraph.add_edge(source_new, target_new)
                new_edge = self.__resultgraph.lookup_edge(source_new, target_new)
                new_edge.set_attrs(edge_attrs)
            else:
                self.__logger.debug("group edge %s -> %s already existed, ignoring attributes of edge %s -> %s" % (source_new, target_new, edge.get_from_node(), edge.get_to_node()))
            if EdgeAttributes.GROUPED_EDGES not in new_edge.get_attr_names():
                new_edge.set_attrs({EdgeAttributes.GROUPED_EDGES:set()})
            new_edge.get_attr(EdgeAttributes.GROUPED_EDGES).add(edge)

    def __collapse_module_groups(self):
        # TODO nicht Kanten durchlaufen, sondern Knotengruppen. Operation zum Collapsen einer Knotengruppe im Graph vorsehen
        # TODO wenn man die Kanten durchläuft
        for edge in self.__resultgraph.edges():
            source = edge.get_from_node()
            target = edge.get_to_node()
            source_new = self.__check_replace_by_node_group(source)
            target_new = self.__check_replace_by_node_group(target)
            # TODO das collapsen als Operation des Graphen vorsehen, damit __leaves auch aktuell gehalten werden kann
            if (source_new != source) or (target_new != target):
                self.__collapse_edge(edge, source_new, target_new)

    def __remove_original_nodes(self):
        for node in list(self.__resultgraph.nodes_raw()):
            if not isinstance(node, NodeGroup):
                node_group = self.__get_node_group_if_collapsing(node)
                if node_group:
                    self.__resultgraph.node_attr(node_group, NodeAttributes.GROUPED_NODES).add(node)
                    self.__resultgraph.remove_node(node)

    def _get(self):
        if self.__resultgraph == None:
            self.__resultgraph = MutableAttributeGraph(graph=self.__inputgraph)
            self.__original_nodes = set()
            self.__collapse_module_groups()
            self.__remove_original_nodes()
            self.__node_group_conf = None
            #self.__resultgraph.delete_unconnected_nodes()
        return self.__resultgraph

    @staticmethod
    def get_collapsed_graph(inputgraph, node_group_conf):
        assert isinstance(inputgraph, BasicGraph)
        assert isinstance(node_group_conf, NodeGroupingConfiguration)
        node_group_conf.get_node_grouper().configure_nodes(inputgraph.nodes_raw())
        return GraphCollapser(inputgraph, node_group_conf)._get()

class OutputMultiGraphTools(object):
    @staticmethod
    def construct_superfluous_missing_multigraph(base_graph,
                                                 superfluous_deps_edges,
                                                 missing_deps_edges,
                                                 node_group_conf=None,
                                                 superfluous_color=Colors.RED,
                                                 missing_color=Colors.BLUE):
        superfluous_deps_graph = MutableAttributeGraph(edges=superfluous_deps_edges)
        missing_deps_graph = MutableAttributeGraph(edges=missing_deps_edges)

        if node_group_conf != None:
            base_graph = GraphCollapser.get_collapsed_graph(base_graph, node_group_conf)
            superfluous_deps_graph = GraphCollapser.get_collapsed_graph(superfluous_deps_graph, node_group_conf)
            missing_deps_graph = GraphCollapser.get_collapsed_graph(missing_deps_graph, node_group_conf)

        additional_graphs = [(superfluous_deps_graph,
                              {EdgeAttributes.COLOR:superfluous_color,
                               EdgeAttributes.WEIGHT:5,
                               EdgeAttributes.STYLE:EdgeStyles.DASHED},
                              True),
                             (missing_deps_graph,
                              {EdgeAttributes.COLOR:missing_color,
                               EdgeAttributes.WEIGHT:5,
                               EdgeAttributes.STYLE:EdgeStyles.DASHED},
                              False)]
        multigraph = MultiGraphTools.construct_generic_multigraph(base_graph, additional_graphs)
        return multigraph
