'''
Created on 01.05.2012

@author: SIGIESEC
'''
import unittest
from base.dependency.dependency_default import DefaultDependencyFilter,\
    NullDependencyFilterConfiguration
from commons.graph.attrgraph_util import MutableAttributeGraph

class DefaultDependencyFilterTest(unittest.TestCase):
    def test_filter_nothing_empty_graph_no_modules(self):
        full_graph = MutableAttributeGraph()
        filtered_graph = DefaultDependencyFilter.filter_graph(full_graph.immutable(), 
                                             dependency_filter_config=NullDependencyFilterConfiguration(), 
                                             internal_modules=[])
        self.assertEqual([], sorted(filtered_graph.node_names()))
        self.assertEqual(0, filtered_graph.edge_count())

    def test_filter_nothing_empty_graph_some_modules(self):
        full_graph = MutableAttributeGraph()
        filtered_graph = DefaultDependencyFilter.filter_graph(full_graph.immutable(), 
                                             dependency_filter_config=NullDependencyFilterConfiguration(), 
                                             internal_modules=["a"])
        self.assertEqual(["a"], sorted(filtered_graph.node_names()))
        self.assertEqual(0, filtered_graph.edge_count())

    def test_filter_nothing_nonempty_graph_additional_module(self):
        full_graph = MutableAttributeGraph()
        full_graph.add_edge_and_nodes("a", "b")
        full_graph.add_edge_and_nodes("b", "c")
        full_graph.add_edge_and_nodes("d", "a")
        filtered_graph = DefaultDependencyFilter.filter_graph(full_graph.immutable(), 
                                             dependency_filter_config=NullDependencyFilterConfiguration(), 
                                             internal_modules=["a", "e"])
        self.assertEqual(["a", "b", "c", "d", "e"], sorted(filtered_graph.node_names()))
        self.assertEqual(3, filtered_graph.edge_count())
        
