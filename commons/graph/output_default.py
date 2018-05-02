# -*- coding: UTF-8 -*-
'''
Created on 12.10.2010

@author: SIGIESEC
'''
from commons.graph.attrgraph_base import NullNodeGrouper
from commons.graph.output_base import BaseNodeGroupingConfiguration

class DefaultNodeGroupingConfiguration(BaseNodeGroupingConfiguration):
    """
    Collapses all or no nodes.
    """
    
    def __init__(self, collapse_all=False, node_grouper=NullNodeGrouper(), *args, **kwargs):
        BaseNodeGroupingConfiguration.__init__(self, node_grouper, *args, **kwargs)
        self.__collapse_all = collapse_all
    
    def collapse_node_group(self, _module_group_prefix):
        return self.__collapse_all
    
    

