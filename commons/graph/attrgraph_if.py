# -*- coding: UTF-8 -*-
'''
Interfaces for attributed graph data structures.

Created on 01.10.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.core_if import EnumerationItem, Enumeration

class NodeGrouper(AutoConfigurable):
# TODO rename parameters with "modules" to "node"
    
    def __init__(self, modules=None):
        pass
    
    def configure_nodes(self, nodes):
        raise NotImplementedError(self.__class__)
    
    def get_node_group_prefix(self, module):
        """
        Returns the module group prefix for the given module. Returns None if 
        it is not contained in any known module group. Never returns the 
        empty string.
        
        @rtype: string or None
        """
        raise NotImplementedError(self.__class__)
    
    def node_group_prefixes(self):
        raise NotImplementedError(self.__class__)

class _GraphShape(EnumerationItem):
    pass

class GraphShapes(Enumeration):
    """
    >>> GraphShapes.name(GraphShapes.PACKAGE)
    'PACKAGE'

    >>> GraphShapes.name(2) #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: value = 2 <type 'int'>
    
    >>> sorted(map(GraphShapes.name, GraphShapes.values()))
    ['BOT', 'ELLIPSIS', 'PACKAGE', 'RECTANGLE', 'TOP', 'TOPBOT']
    """
    _type = _GraphShape
    PACKAGE = _GraphShape()
    RECTANGLE = _GraphShape()
    ELLIPSIS = _GraphShape()
    BOT = _GraphShape()
    TOP = _GraphShape()
    TOPBOT = _GraphShape()
    
class _Color(EnumerationItem):
    pass

class Colors(Enumeration):
    _type = _Color
    RED = _Color()
    BLUE = _Color()
    BLACK = _Color()
    WHITE = _Color()
    PURPLE = _Color()
    DARKPURPLE = _Color()
    GREEN = _Color()
    DARKGREEN = _Color()
    GREENYELLOW = _Color()
    SALMON = _Color()
    YELLOW = _Color()

class GraphAttribute(EnumerationItem):
    def __init__(self, name):
        EnumerationItem.__init__(self)
        self.__name = name
        
    def get_name(self):
        return self.__name
    
    def __repr__(self):
        return "GraphAttribute(%s)" % repr(self.__name)
    
class GraphAttributes(Enumeration):
    _type = GraphAttribute
    
class NodeAttributes(GraphAttributes):
    GROUPED_NODES = GraphAttribute("nodes")
    SHAPE = GraphAttribute("shape")
    HEIGHT = GraphAttribute("height")
    WIDTH = GraphAttribute("width")
    FILL_COLOR = GraphAttribute("fillcolor")
    LINE_COLOR = GraphAttribute("linecolor")
    LABEL = GraphAttribute("label")
    LINK = GraphAttribute("link")
    SKIPPED_FROM_EDGE = GraphAttribute("skipped_from_edge")
    SKIPPED_TO_EDGE = GraphAttribute("skipped_to_edge")

class EdgeAttributes(GraphAttributes):
    WEIGHT = GraphAttribute("weight")
    COLOR = GraphAttribute("color")
    STYLE = GraphAttribute("style")
    GROUPED_EDGES = GraphAttribute("edges")
    LINK = GraphAttribute("link")
    LABEL = GraphAttribute("label")

class _EdgeStyle(EnumerationItem):
    pass

class EdgeStyles(Enumeration):
    _type = _EdgeStyle
    SOLID = _EdgeStyle()
    DASHED = _EdgeStyle()
    DOTTED = _EdgeStyle()

# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()

