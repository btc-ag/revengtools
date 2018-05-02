#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
A graph output class able to generate GraphML output with the yEd attributing extensions.

Created on 05.06.2012

@status: This is currently incomplete. It is based on a copy of 
  infrastructure.graph_layout.graphviz; when it has matures, the common parts 
  of both implementations should be extracted.
@author: SIGIESEC
'''
from base.dependency.generation_log_if import GenerationLogGenerator
from commons.core_util import CollectionTools
from commons.graph.attrgraph_if import (GraphShapes, Colors, _Color, 
    NodeAttributes, EdgeStyles, EdgeAttributes)
from commons.graph.output_base import (BaseGraphElementDecorator, 
    BaseGraphOutputter)
from commons.graph.output_if import GraphicalGraphOutputter
from itertools import ifilter
from xml.dom.minidom import DOMImplementation
import logging
import re

class GraphMLConstants(object):
    GRAPHML_NS="http://graphml.graphdrawing.org/xmlns/graphml"
    YED_NS="http://www.yworks.com/xml/graphml"

    GraphML_ATTR_SHAPE = "shape"
    GraphML_SHAPE_TAB = "tab"
    GraphML_SHAPE_RECT = "box"
    GraphML_SHAPE_ELLIPSIS = "ellipse"
    GraphML_SHAPE_TRAPEZ = "trapezium"
    GraphML_SHAPE_INVTRAPEZ = "invtrapezium"
    GraphML_SHAPE_OCTAGON = "octagon"

class MyGraphMLConstants(object):
    NODE_GRAPHICS_KEY = "d0"
    EDGE_GRAPHICS_KEY = "d1"

class GraphMLGraphElementOutputter(object):
    ShapeMap = dict({GraphShapes.RECTANGLE: GraphMLConstants.GraphML_SHAPE_RECT,
                     GraphShapes.ELLIPSIS: GraphMLConstants.GraphML_SHAPE_ELLIPSIS,
                     GraphShapes.PACKAGE: GraphMLConstants.GraphML_SHAPE_TAB,
                     GraphShapes.BOT: GraphMLConstants.GraphML_SHAPE_TRAPEZ,
                     GraphShapes.TOP: GraphMLConstants.GraphML_SHAPE_INVTRAPEZ,
                     GraphShapes.TOPBOT: GraphMLConstants.GraphML_SHAPE_OCTAGON,
                     })


    def __init__(self, label_decorators, tooltip_decorators, graph):
        self.__label_decorators = label_decorators
        self.__tooltip_decorators = tooltip_decorators
        self.__graph = graph

    @staticmethod
    def limited_str(p_str):
        if p_str == None:
            return None
        else:
            MAX_LENGTH = 256
            if len(p_str) > MAX_LENGTH - 3:
                return p_str[:(MAX_LENGTH - 3)] + '...'
            else:
                return p_str

    def _graph(self):
        return self.__graph

    def _label_decorators(self):
        return self.__label_decorators

    def _tooltip_decorators(self):
        return self.__tooltip_decorators

    ColorMap = dict({Colors.BLUE: "blue",
                     Colors.RED: "red",
                     Colors.WHITE: "white",
                     Colors.BLACK: "black",
                     Colors.PURPLE: "mediumorchid",
                     Colors.GREEN: "green1",
                     Colors.DARKPURPLE: "purple",
                     Colors.DARKGREEN: "green3",
                     Colors.GREENYELLOW: "greenyellow",
                     Colors.SALMON: "salmon",
                     Colors.YELLOW: "yellow"
                     })

    def map_color(self, in_value):
        if isinstance(in_value, _Color):
            return Colors.map(self.ColorMap, in_value)
        else:
            return in_value

    def _tooltip(self, graph_element):
        if len(self._tooltip_decorators()) > 0:
            # TODO wie erzeuge ich einen Zeilenumbruch im Tooltip??
            return ", ".join(CollectionTools.flatten(BaseGraphElementDecorator.decorations(self._tooltip_decorators(), graph_element)))
        else:
            return ""
        # TODO folgendes in einen SimpleEdgeDecorator auslagern
        # return "%s -> %s" % (str(edge.get_from_node()), str(edge.get_to_node()))


class GraphMLNodeOutputter(GraphMLGraphElementOutputter):
    def __init__(self, dom, *args, **kwargs):
        GraphMLGraphElementOutputter.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__dom = dom


    def wrap_camel_case(self, nodename):
        # TODO das ist ein böser Hack
        matches = re.match(r"([a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[A-Za-z0-9_]+)?", nodename)
        if matches != None:
            result = "\\n".join(ifilter(lambda match:match != None, matches.groups()))
        else:
            result = nodename #[matches.group(i) for i in range(1, matches.groups())])
        return result

    def _render_node_name(self, nodename):
        # TODO das gehört besser in GraphMLFormatter und müsste natürlich angepasst werden
        # TODO Sollbruchstellen und Bandbreite für Zeichen pro Zeile definieren 
        if nodename.find("/") != -1:
            return nodename.replace("/", "/\\n")
        elif nodename.find(".") != -1:
            return nodename.replace(".", ".\\n")
        elif nodename.startswith("<"):
            return "<%s>" % self._render_node_name(nodename.strip("<>")).strip()
        else:
            result = self.wrap_camel_case(nodename)
            return result

    def _node_label(self, node):
        nodename = str(node)
        if self._graph().node_attr(node, NodeAttributes.LABEL) != None:
            label = self._render_node_name(self._graph().node_attr(node, NodeAttributes.LABEL))
        else:        
            label = self._render_node_name(nodename)
        if len(self._label_decorators()) > 0:
            if len(label):
                label += "\\n"
            label += "\\n".join(CollectionTools.flatten(BaseGraphElementDecorator.decorations(self._label_decorators(), node)))
        return label


    def __create_label_node(self, node):
        label_node = self.__dom.createElementNS(GraphMLConstants.YED_NS, "y:NodeLabel")
        label_node.appendChild(self.__dom.createTextNode(self.limited_str(self._node_label(node))))
        return label_node

    def __make_node_attributes(self, node):
        data_node = self.__dom.createElementNS(GraphMLConstants.GRAPHML_NS, "data")
        data_node.setAttribute("key", MyGraphMLConstants.NODE_GRAPHICS_KEY)
        shape_node = self.__dom.createElementNS(GraphMLConstants.YED_NS, "y:ShapeNode")
        data_node.appendChild(shape_node)
        attrs = dict() # TODO eliminate attrs

        shape_node.appendChild(self.__create_label_node(node))
        attrs["tooltip"] = self.limited_str(self._tooltip(node))
        node_attrs = self._graph().node_attr_names(node)
        for (in_attr) in node_attrs:
            in_value = self._graph().node_attr(node, in_attr)
            # TODO Mapping definieren
            if in_attr == NodeAttributes.SHAPE:
                attrs[GraphMLConstants.GraphML_ATTR_SHAPE] = GraphShapes.map(self.ShapeMap, in_value)
                if attrs[GraphMLConstants.GraphML_ATTR_SHAPE] == GraphMLConstants.GraphML_SHAPE_TAB \
                    and NodeAttributes.HEIGHT not in node_attrs:
                    attrs["width"] = str(4.0)
                    attrs["height"] = str(4.0)
            elif in_attr == NodeAttributes.HEIGHT:
                attrs["height"] = str(float(in_value))
            elif in_attr == NodeAttributes.WIDTH:
                attrs["width"] = str(float(in_value))
            elif in_attr == NodeAttributes.LINE_COLOR:
                attrs["color"] = self.map_color(in_value)
                # TODO sinnvoll? 
                attrs["penwidth"] = 3
            elif in_attr == NodeAttributes.FILL_COLOR:
                attrs["fillcolor"] = self.map_color(in_value)
            elif in_attr == NodeAttributes.LINK:
                attrs["href"] = in_value
            elif in_attr in [NodeAttributes.GROUPED_NODES, NodeAttributes.SKIPPED_FROM_EDGE, NodeAttributes.SKIPPED_TO_EDGE, NodeAttributes.LABEL]:
                pass
            else:
                self.__logger.warning("Unknown node attributes %s=%s" % (in_attr, in_value))
        return data_node

    def process_node(self, node, xml_node):
        #rendered_node = self._gvoutputter().dot_node_dict(node, attrs)
        rendered_node_label = self._node_label(node)
        xml_childnode = self.__dom.createElement("node")
        xml_childnode.setAttribute("id", str(node))
        xml_node.appendChild(xml_childnode)
        xml_childnode.appendChild(self.__make_node_attributes(node))

class GraphMLEdgeOutputter(GraphMLGraphElementOutputter):

    def __init__(self, dom, *args, **kwargs):
        GraphMLGraphElementOutputter.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__dom = dom

    StyleMap = dict({EdgeStyles.SOLID: "solid",
                     EdgeStyles.DASHED: "dashed",
                     EdgeStyles.DOTTED: "dotted",
                     })

    def __get_GraphML_edge_attributes(self, edge):
        attrs = dict({"minlen":"4",
                "penwidth":"2"})
        attrs["label"] = self.limited_str(self._edge_label(edge))
        # TODO zu langes tooltip/edgetooltip führt bei GraphML dazu, dass fehlerhaftes SVG erzeugt wird
        attrs["tooltip"] = self.limited_str(self._tooltip(edge))
        edge_attrs = edge.get_attr_names()
        for (in_attr) in edge_attrs:
            in_value = edge.get_attr(in_attr)
            if in_attr == EdgeAttributes.COLOR:
                attrs["color"] = self.map_color(in_value)
            elif in_attr == EdgeAttributes.WEIGHT:
                attrs["penwidth"] = in_value
            elif in_attr == EdgeAttributes.STYLE:
                attrs["style"] = EdgeStyles.map(self.StyleMap, in_value)
            elif in_attr == EdgeAttributes.LABEL:
                attrs["label"] = in_value
            elif in_attr in [EdgeAttributes.GROUPED_EDGES]:
                pass
            else:
                self.__logger.warning("Unknown edge attributes %s=%s" % (in_attr, in_value))
        return attrs

    def _edge_label(self, edge):
        if len(self._label_decorators()) > 0:
            return "\\n".join(CollectionTools.flatten(BaseGraphElementDecorator.decorations(self._label_decorators(), edge)))
        else:
            return None

    def render_edge(self, edge, xml_node):
#        edge_string = self._gvoutputter().dot_edge_dict(edge.get_from_node(),
#                                                       edge.get_to_node(),
#                                                       self.__get_GraphML_edge_attributes(edge))
        edge_id = "%s!:!%s" % (edge.get_from_node(),
                               edge.get_to_node())
        edge_node = self.__dom.createElementNS(GraphMLConstants.GRAPHML_NS, "edge")
        xml_node.appendChild(edge_node)
        edge_node.setAttribute("id", edge_id)
        edge_node.setAttribute("source", str(edge.get_from_node()))
        edge_node.setAttribute("target", str(edge.get_to_node()))

config_generation_log = GenerationLogGenerator()


class GraphMLGraphOutputter(BaseGraphOutputter, GraphicalGraphOutputter):
    # TODO do not inherit from BaseGraphOutputter!
    
    def __init__(self, description, outfile, graph, generation_log=config_generation_log, *args, **kwargs):
        self.__logger = logging.getLogger(self.__module__)
        BaseGraphOutputter.__init__(self,
                                    description=description,
                                    outfile=outfile,
                                    graph=graph,
                                    generation_log=generation_log, 
                                    *args, **kwargs)
        GraphicalGraphOutputter.__init__(self, *args, **kwargs)
        self._supports_grouping = False # TODO
        self.__dom = DOMImplementation().createDocument(GraphMLConstants.GRAPHML_NS, "graphml", None)
        self.__edge_outputter = GraphMLEdgeOutputter(self.__dom, self._edge_label_decorators(),
                                                      self._edge_tooltip_decorators(),
                                                      self._graph())
        self.__node_outputter = GraphMLNodeOutputter(self.__dom, self._node_label_decorators(),
                                                      self._node_tooltip_decorators(),
                                                      self._graph())

    @staticmethod
    def usual_extension():
        return '.graphml'

    def _process_edge(self, edge, xml_node):
        self.__edge_outputter.render_edge(edge, xml_node)

#    def _output_group(self, group_name, processed_nodes):
#        self.__logger.debug("Outputting group %s" % (group_name))
#        print >>self.file(), "subgraph cluster_%s  {" % (GraphMLFormatterHelper.sanitize_node_name(group_name),)
#        print >>self.file(), ("colorscheme=\"pastel28\"; bgcolor=\"%i\"; label=\"%s\""
#              % (hash(group_name) % 8 + 1, group_name))
#        for node in processed_nodes:
#            print >>self.file(), "%s;" % (GraphMLFormatterHelper.sanitize_node_name(node),)
#        print >>self.file(), "}"

    def _process_node(self, node, xml_node):
        self.__node_outputter.process_node(node, xml_node)

    def _output_edges(self, xml_node):
        for edge in sorted(self._graph().edges()):
            self._process_edge(edge, xml_node)            

    def _output_nodes(self, xml_node):
        for node in self._graph().nodes_raw():
            if node != None:
                self._process_node(node, xml_node)
            else:
                self.__logger.debug("node == None in _output_nodes")

    def _output_head(self, xml_node):
#  <key id="d0" for="node" yfiles.type="nodegraphics"/>  
#  <key id="d1" for="edge" yfiles.type="edgegraphics"/>
        key1 = self.__dom.createElementNS(GraphMLConstants.GRAPHML_NS, "key")
        key1.setAttribute("id", MyGraphMLConstants.NODE_GRAPHICS_KEY)
        key1.setAttribute("for", "node")
        key1.setAttribute("yfiles.type", "nodegraphics")
        xml_node.appendChild(key1)
        key2 = self.__dom.createElementNS(GraphMLConstants.GRAPHML_NS, "key")
        key2.setAttribute("id", MyGraphMLConstants.EDGE_GRAPHICS_KEY)
        key2.setAttribute("for", "edge")
        key2.setAttribute("yfiles.type", "edgegraphics")
        xml_node.appendChild(key2)
#        description = self.description()
#        print >>self.file(), ("label=\"%s (graph date %s)\\n%s\\n%s\\n%s\";" %
#              (description if description else "no graph description",
#               datetime.now().strftime("%Y-%m-%d %H:%M"),
#               "\\n".join(deco.decorate_graph(self._graph()) for deco in self._decorator_config().get_graph_decorators()),
#               ", ".join(chain.from_iterable(((deco.description() for deco in self._node_label_decorators()),
#                                             ("%s (T)" % deco.description() for deco in self._node_tooltip_decorators())
#                                             ))),
#               ", ".join(chain.from_iterable(((deco.description() for deco in self._edge_label_decorators()),
#                                             ("%s (T)" % deco.description() for deco in self._edge_tooltip_decorators())
#                                             ))),
#               ))

    def _output_tail(self):
        self.__dom.writexml(self.file(), newl="\n")

    def output_all(self):
        self.register_log()
        self.__logger.debug("Outputting graph %s using node grouper %s" % (self._graph(),
                                                                           self._node_grouper()))
        root_node = self.__dom.getElementsByTagName("graphml")[0]
        root_node.setAttribute("xmlns", GraphMLConstants.GRAPHML_NS) # TODO why is this necessary?
        root_node.setAttribute("xmlns:y", GraphMLConstants.YED_NS) # TODO why is this necessary?
        self._output_head(root_node)
        #self._output_groups() # TODO output nodes by groups
        self._attach_decorators()
        graph_node = self.__dom.createElementNS(GraphMLConstants.GRAPHML_NS, "graph")
        graph_node.setAttribute("id", "G")
        graph_node.setAttribute("edgedefault", "directed")
        root_node.appendChild(graph_node)
        try:
            self._output_nodes(graph_node)
            self._output_edges(graph_node)
        finally:
            self._detach_decorators()
        self._output_tail()

#    def register_log(self):
#        pass
