#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 05.06.2012

@author: SIGIESEC
'''
from StringIO import StringIO
from base.dependency.dependency_util import GraphDescriptionImpl
from base.dependency.generation_log import NullGenerationLogGenerator
from commons.graph.attrgraph_util import MutableAttributeGraph, AttributeGraph
from commons.graph.graph_util import SimpleEdge
from commons.graph.output_base import TextGraphOutputter
from commons.graph.output_if import DecoratorSet
from functools import partial
from infrastructure.graph_layout.graphml import GraphMLGraphOutputter
import unittest

class TestStringIO(StringIO):
    name = "test"

class GraphOutputTestBase(object):
    def _get_outputter_class(self):
        raise NotImplementedError()

    def _run_with_graph(self, graph):
        outfile = TestStringIO()
        outputter = self._get_outputter_class()(graph=graph, outfile=outfile, 
            decorator_config=DecoratorSet(), 
            output_groups=False, 
            node_grouper=None, 
            description=GraphDescriptionImpl(description="test"))
        outputter.output_all()
    #outfile.close()
        print outfile.getvalue()

    def test_empty(self):
        graph = MutableAttributeGraph()
        self._run_with_graph(graph)

    def test_basic(self):
        graph = AttributeGraph(edges=(SimpleEdge(from_node="a", to_node="b"),))
        self._run_with_graph(graph)
        
class GraphMLGraphOutputterTest(GraphOutputTestBase, unittest.TestCase):
    def _get_outputter_class(self):
        # TODO actually, a dummy generation log should be used
        return partial(GraphMLGraphOutputter, generation_log=NullGenerationLogGenerator())

class TextGraphOutputterTest(GraphOutputTestBase, unittest.TestCase):
    def _get_outputter_class(self):
        # TODO actually, a dummy generation log should be used
        return partial(TextGraphOutputter, generation_log=NullGenerationLogGenerator())
    