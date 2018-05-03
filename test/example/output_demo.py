"""
A demonstration of outputting a graph using a (Graphical)GraphOutputter with
some decoration.

Created on 30.08.2012

@author: SIGIESEC
"""
from base.dependency.dependency_util import GraphDescriptionImpl
from commons.configurator import Configurator
from commons.graph.attrgraph_if import EdgeAttributes, Colors, NodeAttributes
from commons.graph.attrgraph_util import AttributedEdge, MutableAttributeGraph
from commons.graph.output_base import BaseNodeDecorator
from commons.graph.output_if import (GraphicalGraphOutputter, DecoratorSet)
from epm.cabstyle.dependency_output import (CABStyleFinestLevelModuleGrouperInternal)
import logging
import sys


class MyNodeColorDecorator(BaseNodeDecorator):
    def __init__(self, *args, **kwargs):
        BaseNodeDecorator.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)

    def decorate(self, node):
        if node == "BTC.CAB.Y.B":
            color = Colors.RED
        else:
            color = Colors.WHITE
        self._graph().set_node_attrs(node, {NodeAttributes.FILL_COLOR: color})

class GraphOutputDemo(object):
    def __init__(self, graph_outputter_class):
        self.__graph_outputter_class = graph_outputter_class    
    
    def run(self, output_filename):
        graph = MutableAttributeGraph(edges=(AttributedEdge(from_node="BTC.CAB.X.ClassA", to_node="BTC.CAB.Y.B"),
                                             AttributedEdge(from_node="BTC.CAB.X.ClassC", to_node="BTC.CAB.Y.B"),
                                             AttributedEdge(from_node="BTC.CAB.Z.ClassD", to_node="BTC.CAB.Y.B"),
                                             ))
        graph.lookup_edge("BTC.CAB.X.ClassA", "BTC.CAB.Y.B").set_attrs({EdgeAttributes.COLOR: Colors.RED})
        outfile = open(output_filename, "w")
        outputter = self.__graph_outputter_class(graph=graph, outfile=outfile, 
            decorator_config=DecoratorSet(node_label_decorators=(MyNodeColorDecorator(),),
                                          ), 
            output_groups=True, 
            node_grouper=CABStyleFinestLevelModuleGrouperInternal( 
                              modules=graph.node_names(),
                              internal_modules=graph.node_names(),
                              min_parts=3), 
            description=GraphDescriptionImpl(description="test", basename=output_filename))
        outputter.output_all()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    configurator = Configurator()
    configurator.default()
    GraphOutputDemo(graph_outputter_class=configurator.get_concrete_adapter(GraphicalGraphOutputter)).run(output_filename=sys.argv[1] if len(sys.argv) > 1 else "test")
