# -*- coding: UTF-8 -*-
'''
Created on 01.10.2010

@author: SIGIESEC
'''
from commons.graph.attrgraph_if import NodeGrouper

class NullNodeGrouper(NodeGrouper):
    def __init__(self, modules=None):
        NodeGrouper.__init__(self, modules)
        
    def configure_nodes(self, nodes):
        pass
    
    def get_node_group_prefix(self, module):
        return None
    
    def node_group_prefixes(self):
        return []
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
