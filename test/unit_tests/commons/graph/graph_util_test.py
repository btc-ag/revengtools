'''
Created on 09.06.2012

@author: SIGIESEC
'''
from commons.graph.graph_util import GraphAlgorithms, GraphConversions
import unittest

class GraphAlgorithmsTest(unittest.TestCase):
    INPUT_EDGES_1 = [(1,2), (2,3), (3, 4), (2, 4), (2, 5), (4, 5)]
    
    def test_cut_branches_1_1(self):
        result = GraphAlgorithms.cut_branches(cut_obj_ids=[], edges=self.INPUT_EDGES_1)
        self.assertEquals(set(self.INPUT_EDGES_1), set(result))

    def test_cut_branches_1_2(self):
        result = GraphAlgorithms.cut_branches(cut_obj_ids=[3], edges=self.INPUT_EDGES_1)
        self.assertEquals(set([(1,2), (2,3), (2, 4), (2, 5), (4, 5)]), set(result))

    def test_cut_branches_1_3(self):
        result = GraphAlgorithms.cut_branches(cut_obj_ids=[4], edges=self.INPUT_EDGES_1)
        self.assertEquals(set([(1,2), (2,3), (3,4), (2, 4), (2, 5)]), set(result))

    def test_remove_branches_1_2(self):
        result = GraphAlgorithms.remove_branches(cut_nodes=[3], edges=self.INPUT_EDGES_1, target_nodes=[5])
        self.assertEquals(set([(1,2), (2, 4), (2, 5), (4, 5)]), set(result))

    def test_remove_branches_1_4(self):
        result = GraphAlgorithms.remove_branches(cut_nodes=[1], edges=self.INPUT_EDGES_1, target_nodes=[5])
        self.assertEquals(set([(4, 5), (3, 4), (2, 5), (2, 3), (2, 4)]), set(result))
        
    def test_dependent_nodes_1_5(self):
        result = GraphAlgorithms.dependent_nodes(GraphConversions.edge_list_to_pygraph(edge_list=self.INPUT_EDGES_1), start_nodes=[5])
        self.assertEquals(set([1,2,3,4,5]), result)

    def test_dependent_nodes_1_4(self):
        result = GraphAlgorithms.dependent_nodes(GraphConversions.edge_list_to_pygraph(edge_list=self.INPUT_EDGES_1), start_nodes=[4])
        self.assertEquals(set([1,2,3,4]), result)

    def test_dependent_nodes_1_1(self):
        result = GraphAlgorithms.dependent_nodes(GraphConversions.edge_list_to_pygraph(edge_list=self.INPUT_EDGES_1), start_nodes=[1])
        self.assertEquals(set([1]), result)
        