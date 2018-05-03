#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 12.05.2011

@author: SIGIESEC
'''
from commons.core_util import CollectionTools
from commons.graph.attrgraph_if import (EdgeAttributes, EdgeStyles, 
    NodeAttributes, Colors, _Color)
from commons.graph.output_base import (BaseGraphOutputter, 
    BaseGraphElementDecorator)
from commons.graph.output_if import GraphicalGraphOutputter
from org.eclipse.draw2d import Label
from org.eclipse.zest.core.widgets import (Graph, GraphConnection, GraphNode, 
    ZestStyles)
from org.eclipse.zest.layouts.algorithms import (CompositeLayoutAlgorithm, 
    HorizontalShift, TreeLayoutAlgorithm)
from org.eclipse.zest.layouts import LayoutStyles
from org.eclipse.swt import SWT
from org.eclipse.swt.widgets import Display
import logging

# TODO add missing support for subgraphs/groups
# ToDO add missing support for attributes

class ZestHelper(object):
    @staticmethod
    def configure_layouter(graph):
        return graph.setLayoutAlgorithm(CompositeLayoutAlgorithm(LayoutStyles.NO_LAYOUT_NODE_RESIZING, [
                    TreeLayoutAlgorithm(
                        LayoutStyles.NO_LAYOUT_NODE_RESIZING), 
                    HorizontalShift(
                        LayoutStyles.NO_LAYOUT_NODE_RESIZING)]), True)

class ZestGraphOutputter(BaseGraphOutputter, GraphicalGraphOutputter):
    ColorMap = dict({Colors.BLUE: SWT.COLOR_BLUE,
                     Colors.RED: SWT.COLOR_RED,
                     Colors.WHITE: SWT.COLOR_WHITE,
                     Colors.BLACK: SWT.COLOR_BLACK,
                     Colors.PURPLE: SWT.COLOR_MAGENTA,
                     Colors.GREEN: SWT.COLOR_GREEN,
                     Colors.DARKPURPLE: SWT.COLOR_DARK_MAGENTA,
                     Colors.DARKGREEN: SWT.COLOR_DARK_GREEN,
                     Colors.GREENYELLOW: SWT.COLOR_GREEN, # TODO 
                     Colors.YELLOW: SWT.COLOR_YELLOW,
                     Colors.SALMON: SWT.COLOR_DARK_RED, # TODO
                     })
    
    def __init__(self, description, outfile, graph, zest_parent=None, zest_style=0, *args, **kwargs):
        self.__logger = logging.getLogger(self.__module__)
        BaseGraphOutputter.__init__(self,
                                    description=description,
                                    outfile=outfile,
                                    graph=graph,
                                    *args, **kwargs)
        GraphicalGraphOutputter.__init__(self, *args, **kwargs)
        self.__node_to_zest_map = dict()
        self.__parent = zest_parent
        self.__style = zest_style
#        self.__gvoutputter = GraphvizFormatter()
#        self.__edge_outputter = GraphvizEdgeOutputter(self.__gvoutputter,
#                                                      self._edge_label_decorators(),
#                                                      self._edge_tooltip_decorators(),
#                                                      self._graph())
#        self.__node_outputter = GraphvizNodeOutputter(self.__gvoutputter,
#                                                      self._node_label_decorators(),
#                                                      self._node_tooltip_decorators(),
#                                                      self._graph())

    @staticmethod
    def usual_extension():
        return None

    def edges_before_nodes(self):
        return False

    EdgeStyleMap = dict({EdgeStyles.SOLID: ZestStyles.CONNECTIONS_SOLID,
                     EdgeStyles.DASHED: ZestStyles.CONNECTIONS_DASH,
                     EdgeStyles.DOTTED: ZestStyles.CONNECTIONS_DOT,
                     })


    def map_color(self, in_value):
        if isinstance(in_value, _Color):
            return Colors.map(self.ColorMap, in_value)
        else:
            self.__logger.warning("value %s is not a color" % in_value)
            return None
        
    def map_swt_color(self, in_value, default=SWT.COLOR_BLUE):
        color_constant = self.map_color(in_value)
        if color_constant:
            return Display.getCurrent().getSystemColor(color_constant)
        else:
            return Display.getCurrent().getSystemColor(default)

    def _set_edge_attributes(self, edge, gc):
        if len(self._edge_label_decorators()) > 0:
            gc.setText("\n".join(CollectionTools.flatten(BaseGraphElementDecorator.decorations(self._edge_label_decorators(), edge))))
        # TODO zu langes tooltip/edgetooltip führt bei Graphviz dazu, dass fehlerhaftes SVG erzeugt wird
        if len(self._edge_tooltip_decorators()) > 0:
            # TODO wie erzeuge ich einen Zeilenumbruch im Tooltip??
            gc.setTooltip(Label(", ".join(CollectionTools.flatten(BaseGraphElementDecorator.decorations(self._edge_tooltip_decorators(), edge)))))

        edge_attrs = edge.get_attr_names()
        for (in_attr) in edge_attrs:
            in_value = edge.get_attr(in_attr)
            if in_attr == EdgeAttributes.COLOR:
                gc.setLineColor(self.map_swt_color(in_value))
            elif in_attr == EdgeAttributes.WEIGHT:
                gc.setLineWidth(in_value)
            elif in_attr == EdgeAttributes.STYLE:
                gc.setLineStyle(EdgeStyles.map(self.StyleMap, in_value))
            elif in_attr in [EdgeAttributes.GROUPED_EDGES]:
                pass
            else:
                logging.warning("Unknown edge attributes %s=%s" % (in_attr, in_value))

    def _set_node_attributes(self, node, gn):
        if len(self._node_label_decorators()) > 0:
            gn.setText(str(node) + " " + " ".join(CollectionTools.flatten(BaseGraphElementDecorator.decorations(self._node_label_decorators(), node))))
        else:
            gn.setText(str(node))        
        # TODO zu langes tooltip/edgetooltip führt bei Graphviz dazu, dass fehlerhaftes SVG erzeugt wird
        if len(self._node_tooltip_decorators()) > 0:
            # TODO wie erzeuge ich einen Zeilenumbruch im Tooltip??
            gn.setTooltip(Label(", ".join(CollectionTools.flatten(BaseGraphElementDecorator.decorations(self._node_tooltip_decorators(), node)))))
        
        height = None
        width = None
        node_attrs = self._graph().node_attr_names(node)
        for (in_attr) in node_attrs:
            in_value = self._graph().node_attr(node, in_attr)
            # TODO Mapping definieren
            if in_attr == NodeAttributes.SHAPE:
                pass
                #attrs[GraphvizConstants.GRAPHVIZ_ATTR_SHAPE] = GraphShapes.map(self.ShapeMap, in_value)
                #if attrs[GraphvizConstants.GRAPHVIZ_ATTR_SHAPE] == GraphvizConstants.GRAPHVIZ_SHAPE_TAB \
                #    and NodeAttributes.HEIGHT not in node_attrs:
                    #attrs["width"] = str(4.0 * float(config_graphviz.get_node_scale()))
                    #attrs["height"] = str(4.0 * float(config_graphviz.get_node_scale()))
            elif in_attr == NodeAttributes.HEIGHT:
                height = float(in_value)
                # str(float(in_value) * float(config_graphviz.get_node_scale()))
            elif in_attr == NodeAttributes.WIDTH:
                width = float(in_value)
                # str(float(in_value) * float(config_graphviz.get_node_scale()))
            elif in_attr == NodeAttributes.LINE_COLOR:
                gn.setBorderColor(self.map_swt_color(in_value, SWT.COLOR_BLACK))
            elif in_attr == NodeAttributes.FILL_COLOR:
                gn.setBackgroundColor(self.map_swt_color(in_value, SWT.COLOR_WHITE))
            elif in_attr == NodeAttributes.LINK:
                pass
                #attrs["href"] = in_value
            elif in_attr in [NodeAttributes.GROUPED_NODES, NodeAttributes.SKIPPED_FROM_EDGE, NodeAttributes.SKIPPED_TO_EDGE, NodeAttributes.LABEL]:
                pass
            else:
                self.__logger.warning("Unknown node attributes %s=%s" % (in_attr, in_value))
        if width:
            gn.setSize(width*40, height*40)        
        

    def _render_edge(self, edge):
        gc = GraphConnection(self.__graph,
                        ZestStyles.CONNECTIONS_DIRECTED, 
                        self.__node_to_zest_map[edge.get_from_node()],
                        self.__node_to_zest_map[edge.get_to_node()])
        
        self._set_edge_attributes(edge, gc)
        return ""

    def _output_group(self, group_name, processed_nodes):
        pass
#        self.__logger.debug("Outputting group %s" % (group_name))
#        print >>self.file(), "subgraph cluster_%s  {" % (GraphvizFormatterHelper.sanitize_node_name(group_name),)
#        print >>self.file(), ("colorscheme=\"pastel28\"; bgcolor=\"%i\"; label=\"%s\""
#              % (hash(group_name) % 8 + 1, group_name))
#        for node in processed_nodes:
#            print >>self.file(), "%s;" % (GraphvizFormatterHelper.sanitize_node_name(node),)
#        print >>self.file(), "}"

    def _render_node(self, node):
        gn = GraphNode(self.__graph,
                  ZestStyles.NONE)
        #gn.getFigure().setStyle(SWT.WRAP) #getFigure is not public
        self._set_node_attributes(node, gn)
        self.__node_to_zest_map[node] = gn
        return ""

    def _output_head(self):
        self.__graph = Graph(self.__parent, self.__style)
        ZestHelper.configure_layouter(self.__graph)        
#        description = self.description()
#        print >>self.file(), self.__gvoutputter.head()
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
        pass

    def register_log(self):
        pass

    def set_parent(self, parent):
        self.__parent = parent
    
    def set_style(self, style):
        self.__style = style

    def get_output_zest_graph(self):
        return self.__graph
    
