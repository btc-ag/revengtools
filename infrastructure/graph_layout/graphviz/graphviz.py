#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.dependency.generation_log_if import GenerationLogGenerator
from commons.core_util import CollectionTools
from commons.graph.attrgraph_if import (GraphShapes, Colors, _Color, 
    NodeAttributes, EdgeStyles, EdgeAttributes)
from commons.graph.output_base import (BaseGraphElementDecorator, 
    BaseGraphOutputter, GenericRenderingGraphOutputter, NullRenderExecutor)
from commons.graph.output_if import GraphicalGraphOutputter,\
    GraphicalGraphOutputterFactory
from datetime import datetime
from infrastructure.graph_layout.graphviz.graphviz_config import (
    GraphvizConfiguration, RenderingConfiguration)
from infrastructure.graph_layout.graphviz.graphviz_executor import (
    ScriptInjectingGraphvizRenderExecutor, PipeGraphvizRenderExecutor)
from infrastructure.graph_layout.graphviz.graphviz_internal import (
    GraphvizFormatter, GraphvizFormatterHelper)
from itertools import chain, ifilter
import logging
import re
from commons.config_if import ConfigDependent, ObjectFactory

class GraphvizConstants(object):
    GRAPHVIZ_ATTR_SHAPE = "shape"
    GRAPHVIZ_SHAPE_TAB = "tab"
    GRAPHVIZ_SHAPE_RECT = "box"
    GRAPHVIZ_SHAPE_ELLIPSIS = "ellipse"
    GRAPHVIZ_SHAPE_TRAPEZ = "trapezium"
    GRAPHVIZ_SHAPE_INVTRAPEZ = "invtrapezium"
    GRAPHVIZ_SHAPE_OCTAGON = "octagon"

config_graphviz = GraphvizConfiguration()

class GraphvizGraphElementOutputter(object):
    ShapeMap = dict({GraphShapes.RECTANGLE: GraphvizConstants.GRAPHVIZ_SHAPE_RECT,
                     GraphShapes.ELLIPSIS: GraphvizConstants.GRAPHVIZ_SHAPE_ELLIPSIS,
                     GraphShapes.PACKAGE: GraphvizConstants.GRAPHVIZ_SHAPE_TAB,
                     GraphShapes.BOT: GraphvizConstants.GRAPHVIZ_SHAPE_TRAPEZ,
                     GraphShapes.TOP: GraphvizConstants.GRAPHVIZ_SHAPE_INVTRAPEZ,
                     GraphShapes.TOPBOT: GraphvizConstants.GRAPHVIZ_SHAPE_OCTAGON,
                     })


    def __init__(self, gvoutputter, label_decorators, tooltip_decorators, graph):
        self.__gvoutputter = gvoutputter
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

    def _gvoutputter(self):
        return self.__gvoutputter

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


class GraphvizNodeOutputter(GraphvizGraphElementOutputter):
    def __init__(self, *args, **kwargs):
        GraphvizGraphElementOutputter.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)


    def wrap_camel_case(self, nodename):
        # TODO das ist ein böser Hack
        matches = re.match(r"^([a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[a-z0-9_]+)?([A-Z]+[A-Za-z0-9_]*)?$", nodename)
        if matches != None:
            result = "\\n".join(ifilter(lambda match:match != None, matches.groups()))
        else:
            result = nodename #[matches.group(i) for i in range(1, matches.groups())])
        return result

    def _render_node_name(self, nodename):
        # TODO das gehört besser in GraphvizFormatter und müsste natürlich angepasst werden
        # TODO Sollbruchstellen und Bandbreite für Zeichen pro Zeile definieren 
        if nodename.find("/") != -1:
            return nodename.replace("/", "/\\n")
        elif nodename.find(".") != -1:
            return nodename.replace(".", ".\\n")
        elif nodename.find("::") != -1:
            return nodename.replace("::", "::\\n")
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

    def __get_graphviz_node_attributes(self, node):
        attrs = dict()

        attrs["label"] = self.limited_str(self._node_label(node))
        attrs["tooltip"] = self.limited_str(self._tooltip(node))
        node_attrs = self._graph().node_attr_names(node)
        for (in_attr) in node_attrs:
            in_value = self._graph().node_attr(node, in_attr)
            # TODO Mapping definieren
            if in_attr == NodeAttributes.SHAPE:
                attrs[GraphvizConstants.GRAPHVIZ_ATTR_SHAPE] = GraphShapes.map(self.ShapeMap, in_value)
                if attrs[GraphvizConstants.GRAPHVIZ_ATTR_SHAPE] == GraphvizConstants.GRAPHVIZ_SHAPE_TAB \
                    and NodeAttributes.HEIGHT not in node_attrs:
                    attrs["width"] = str(4.0 * float(config_graphviz.get_node_scale()))
                    attrs["height"] = str(4.0 * float(config_graphviz.get_node_scale()))
            elif in_attr == NodeAttributes.HEIGHT:
                attrs["height"] = str(float(in_value) * float(config_graphviz.get_node_scale()))
            elif in_attr == NodeAttributes.WIDTH:
                attrs["width"] = str(float(in_value) * float(config_graphviz.get_node_scale()))
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
        return attrs

    def render_node(self, node):
        attrs = self.__get_graphviz_node_attributes(node)
        rendered_node = self._gvoutputter().dot_node_dict(node, attrs)
        return rendered_node

class GraphvizEdgeOutputter(GraphvizGraphElementOutputter):

    def __init__(self, *args, **kwargs):
        GraphvizGraphElementOutputter.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)

    StyleMap = dict({EdgeStyles.SOLID: "solid",
                     EdgeStyles.DASHED: "dashed",
                     EdgeStyles.DOTTED: "dotted",
                     })

    def __get_graphviz_edge_attributes(self, edge):
        attrs = dict({"minlen":"4",
                "penwidth":"2"})
        attrs["label"] = self.limited_str(self._edge_label(edge))
        # TODO zu langes tooltip/edgetooltip führt bei Graphviz dazu, dass fehlerhaftes SVG erzeugt wird
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

    def render_edge(self, edge):
        edge_string = self._gvoutputter().dot_edge_dict(edge.get_from_node(),
                                                       edge.get_to_node(),
                                                       self.__get_graphviz_edge_attributes(edge))
        return edge_string

config_generation_log = GenerationLogGenerator()

class GraphvizGraphOutputterFactory(GraphicalGraphOutputterFactory, ConfigDependent):
    def __init__(self, object_factory=ObjectFactory()):
        self.__object_factory = object_factory 

    def usual_extension(self):
        return GraphvizGraphOutputter.usual_extension()

    def get_name(self):
        return GraphvizGraphOutputter.__name__

    def create_instance(self, *args, **kwargs):
        return self.__object_factory.create_instance(xxclsxx=GraphvizGraphOutputter, *args, **kwargs)



class GraphvizGraphOutputter(BaseGraphOutputter, GraphicalGraphOutputter, ConfigDependent):
    def __init__(self, description, outfile, graph, generation_log=config_generation_log, *args, **kwargs):
        self.__logger = logging.getLogger(self.__module__)
        BaseGraphOutputter.__init__(self,
                                    description=description,
                                    outfile=outfile,
                                    graph=graph,
                                    generation_log=generation_log, 
                                    *args, **kwargs)
        GraphicalGraphOutputter.__init__(self, *args, **kwargs)
        self.__gvoutputter = GraphvizFormatter()
        self.__edge_outputter = GraphvizEdgeOutputter(self.__gvoutputter,
                                                      self._edge_label_decorators(),
                                                      self._edge_tooltip_decorators(),
                                                      self._graph())
        self.__node_outputter = GraphvizNodeOutputter(self.__gvoutputter,
                                                      self._node_label_decorators(),
                                                      self._node_tooltip_decorators(),
                                                      self._graph())

    @staticmethod
    def usual_extension():
        return '.dot'

    def _render_edge(self, edge):
        return self.__edge_outputter.render_edge(edge)

    def _output_group(self, group_name, processed_nodes):
        self.__logger.debug("Outputting group %s" % (group_name))
        print >>self.file(), "subgraph cluster_%s  {" % (GraphvizFormatterHelper.sanitize_node_name(group_name),)
        print >>self.file(), ("colorscheme=\"pastel28\"; bgcolor=\"%i\"; label=\"%s\""
              % (hash(group_name) % 8 + 1, group_name))
        for node in processed_nodes:
            print >>self.file(), "%s;" % (GraphvizFormatterHelper.sanitize_node_name(node),)
        print >>self.file(), "}"

    def _render_node(self, node):
        return self.__node_outputter.render_node(node)

    def _output_head(self):
        description = self.description()
        print >>self.file(), self.__gvoutputter.head()
        print >>self.file(), ("label=\"%s (graph date %s)\\n%s\\n%s\\n%s\";" %
              (description if description else "no graph description",
               datetime.now().strftime("%Y-%m-%d %H:%M"),
               "\\n".join(deco.decorate_graph(self._graph()) for deco in self._decorator_config().get_graph_decorators()),
               ", ".join(chain.from_iterable(((deco.description() for deco in self._node_label_decorators()),
                                             ("%s (T)" % deco.description() for deco in self._node_tooltip_decorators())
                                             ))),
               ", ".join(chain.from_iterable(((deco.description() for deco in self._edge_label_decorators()),
                                             ("%s (T)" % deco.description() for deco in self._edge_tooltip_decorators())
                                             ))),
               ))

    def _output_tail(self):
        print >>self.file(), self.__gvoutputter.tail()

    def register_log(self):
        pass

class GraphvizRenderingGraphOutputterFactory(GraphicalGraphOutputterFactory):
    def __init__(self, object_factory=ObjectFactory()):
        self.__object_factory = object_factory 

    def usual_extension(self):
        return GraphvizRenderingGraphOutputter.usual_extension()

    def get_name(self):
        return GraphvizRenderingGraphOutputter.__name__

    def create_instance(self, *args, **kwargs):
        return self.__object_factory.create_instance(xxclsxx=GraphvizRenderingGraphOutputter, *args, **kwargs)


class GraphvizRenderingGraphOutputter(GenericRenderingGraphOutputter):
    BE_PESSIMISTIC = True
    
    def __init__(self, *args, **kwargs):
        GenericRenderingGraphOutputter.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)

    def _rendering_configurations(self):
        if self.BE_PESSIMISTIC and (self._graph().node_count() > 300 or self._graph().edge_count() > 1000):
            self.__logger.warning("Graph is too complex to render, just outputting .dot file %s", 
                                  self._dot_outfile().name)
            rendering_configurations = RenderingConfiguration(aspect_ratio=None, output_format='dot'), 
        else:
            # TODO das könnte auch noch in die Basisklasse wandern, wenn man aus GraphvizConfiguration die generischen Teile herauslöst
            rendering_configurations = config_graphviz.get_rendering_configurations()

        return rendering_configurations
        
    @classmethod
    def _get_renderer_input_generator_graph_outputter(cls):
        return GraphvizGraphOutputter

    def _get_executor_class_and_outfile(self, rendering_configuration):
        output_format = rendering_configuration.get_output_format().lower()
        render_executor_class = NullRenderExecutor
        if output_format != 'dot':
            if output_format == 'svg':
                render_executor_class = ScriptInjectingGraphvizRenderExecutor
            else:
                render_executor_class = PipeGraphvizRenderExecutor
        return render_executor_class
        

# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
