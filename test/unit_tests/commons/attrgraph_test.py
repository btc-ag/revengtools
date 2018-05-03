'''
Created on 02.10.2010

@author: SIGIESEC
'''
import unittest
from commons.graph.attrgraph_util import MutableAttributeGraph, MultiGraph,\
    AttributedEdge
from commons.graph.attrgraph_if import EdgeAttributes, Colors, \
    EdgeStyles


class AttributeGraphHelper(object):
    @staticmethod
    def construct_graph(source, target, color):
        attr_graph = MutableAttributeGraph(default_edge_attrs=dict({EdgeAttributes.COLOR:color}))
        attr_graph.add_node(source)
        attr_graph.add_node(target)
        attr_graph.add_edge(source, target)
        return attr_graph

class AttributeGraphTest(unittest.TestCase):
    source = "source"
    target = "target"
    color = Colors.BLUE


    def setUp(self):
        attr_graph = AttributeGraphHelper.construct_graph(self.source, self.target, self.color)
        self.attr_graph = attr_graph

    def tearDown(self):
        pass

    def test_default_edge_attributes(self):
        edge = self.attr_graph.lookup_edge(self.source, self.target)
        self.assertEquals(edge.get_attr(EdgeAttributes.COLOR), self.color)
        
    def test_edges_equals(self):
        self.assertEqual(AttributedEdge(from_node='a', to_node='c', attrs={}),
                         AttributedEdge(from_node='a', to_node='c', attrs={EdgeAttributes.STYLE: EdgeStyles.SOLID}),)
    
    def test_edges_directed(self):
        self.assertNotEqual(AttributedEdge(from_node='a', to_node='c', attrs={}),
                         AttributedEdge(from_node='c', to_node='a', attrs={}))
            
    def test_sorting_edges_lower_case(self):
        edges = (AttributedEdge(from_node='a', to_node='c'), 
                 AttributedEdge(from_node='b', to_node='c'), 
                 AttributedEdge(from_node='a', to_node='b'), )
        sorted_edges = tuple(sorted(edges))
        self.assertEqual(sorted_edges, (edges[2], edges[0], edges[1]))
        
        #TODO:Big fonts before small fonts?
    def test_sorting_edges_case_sensitive(self):
        edges = (AttributedEdge(from_node='a', to_node='c'), 
                 AttributedEdge(from_node='A', to_node='b'), 
                 AttributedEdge(from_node='a', to_node='b'), )
        sorted_edges = tuple(sorted(edges))
        self.assertEqual(sorted_edges, (edges[1], edges[2], edges[0]))

    def test_sorting_edges_complex(self):
        edges = (AttributedEdge(from_node='btc', to_node='timeSeries'), 
                 AttributedEdge(from_node='BTC', to_node='timeSeries'), 
                 AttributedEdge(from_node='btc', to_node='timeSeries.test'),
                 AttributedEdge(from_node='BTC', to_node='timeSeries.API'),)
        sorted_edges = tuple(sorted(edges))
        self.assertEqual(sorted_edges, (edges[1], edges[3], edges[0], edges[2]))
                
        
class MultiGraphTest(unittest.TestCase):
    source = "source"
    target = "target"
    colors = (Colors.BLUE, Colors.RED)

    def setUp(self):
        self.graphs = (AttributeGraphHelper.construct_graph(self.source, self.target, self.colors[0]),
                       AttributeGraphHelper.construct_graph(self.source, self.target, self.colors[1]),
                       )
        self.multigraph = MultiGraph(self.graphs) 

    def tearDown(self):
        pass


    def test_edge_count(self):
        edges = self.multigraph.edges()
        self.assertEquals(len(edges), 2)

    def test_default_edge_attributes(self):
        edges = self.multigraph.get_edges(self.source, self.target)
        self.assertEquals(len(edges), 2)
        colors = set([edge.get_attr(EdgeAttributes.COLOR) for edge in edges])
        self.assertEquals(colors, set(self.colors))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    