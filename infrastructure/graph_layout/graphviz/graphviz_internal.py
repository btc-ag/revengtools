#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 15.12.2010

@author: SIGIESEC
'''
from infrastructure.graph_layout.graphviz.graphviz_config import (
    GraphvizConfiguration)
from itertools import imap, chain
import collections
import string
import warnings

config_graphviz = GraphvizConfiguration()

class GraphvizFormatterHelper(object):
    @staticmethod
    def sanitize_node_name(insaneName):
        """
        Converts insaneName into a string and replaces characters that are illegal 
        in GraphViz node names by underscores.
        
        >>> GraphvizFormatterHelper().sanitize_node_name(-1000)
        '_1000'
        
        >>> GraphvizFormatterHelper().sanitize_node_name('A.CPP')
        'A_CPP'
        """
        # TODO There are probably more illegal characters 
        return str(insaneName).translate(string.maketrans("#-.+<>/[]: ", "___________"))

    @staticmethod
    def to_dot_label(elements):
        """
        If elements is a literal, convert it to a string.
        If elements is a container, concatenate its elements separated by newline 
        characters.
        
        >>> GraphvizFormatterHelper().to_dot_label(['a', 'b'])
        'a\\\\nb'
    
        >>> GraphvizFormatterHelper().to_dot_label('a')
        'a'
        
        >>> GraphvizFormatterHelper().to_dot_label(5)
        '5'
        """
        if isinstance(elements, collections.Container):
            return "\\n".join(imap(str, elements))
        else:
            return str(elements)

class GraphvizFormatter(object):
    # TODO dies könnte auch eine statische Klasse sein

    def __init__(self):
        self.__helper = GraphvizFormatterHelper()

    def head(self, rankdir='RL', strict=False):
        """
        Prints the head of a graphviz DOT file.
        """
        if strict:
            strict_str = "strict "
        else:
            strict_str = ""
        return """
        %sdigraph G {
            rankdir = %s;
            node [fontname=\"%s\", fontsize=%d, style=\"filled\"];
            edge [fontname=\"%s\", fontsize=%d, arrowsize=%d];
            fontname=\"%s\";
            fontsize=%d;
        """ % (strict_str,
               rankdir,
               config_graphviz.get_font(), 30 * config_graphviz.get_font_scale(),
               config_graphviz.get_font(), 20 * config_graphviz.get_font_scale(), config_graphviz.get_arrowhead_factor(),
               config_graphviz.get_font(),
               30 * config_graphviz.get_font_scale(),
               )

    def tail(self):
        """
        Prints the tail of a graphviz DOT file. 
        """
        return """
        }
        """

    def dot_node_dict(self, name, inAttrDict):
        """
        >>> GraphvizFormatter().dot_node_dict('a', {"fillcolor": None, "label": "test"})
        'a [ label="test" ];'
        
        >>> GraphvizFormatter().dot_node_dict('a', {"size": 2})
        'a [ height="2", width="2" ];'
        """
        attrDict = dict(inAttrDict)
        if "size" in attrDict:
            attrDict.update({"width": attrDict["size"], "height": attrDict["size"]})
            del attrDict["size"]
        return "%s [ %s ];" % (self.__helper.sanitize_node_name(name),
            ", ".join(sorted(["%s=\"%s\"" % (key, value)
                              for key, value in attrDict.iteritems()
                              if value != None])))

    def dot_node(self, name, label, size, color="white"):
        """
        @deprecated: Use dot_node_dict instead.
        
        >>> GraphvizFormatter().dot_node('a', 'b', 3)
        'a [ fillcolor="white", height="3", label="b", width="3" ];'
        """
        warnings.warn("use dot_node_dict instead", DeprecationWarning)
        return self.dot_node_dict(name,
                             {"label": label, "size": size, "fillcolor": color})

    def dot_edge_dict(self, from_node, to_node, inAttrDict=dict()):
        """
        >>> GraphvizFormatter().dot_edge_dict('a', 'b', {"color": "red", "label": None})
        'a -> b [ color="red" ];'
        >>> GraphvizFormatter().dot_edge_dict('a', 'b')
        'a -> b;'
        """
        return "%s -> %s%s;" % (self.__helper.sanitize_node_name(from_node),
                                self.__helper.sanitize_node_name(to_node),
            (
             (" [ %s ]" % ", ".join(sorted(["%s=\"%s\"" % (key, value)
                              for key, value in inAttrDict.iteritems()
                              if value != None])) 
            if len(inAttrDict)
            else ""
            )
            ))

    def dot_edge(self, from_node, to_node, color=None):
        """
        >>> GraphvizFormatter().dot_edge('a', 'b')
        'a -> b;'
        """
        warnings.warn("use dot_edge_dict instead", DeprecationWarning)
        if color != None:
            color_string = ' [ color = \"%s\" ]' % (color,)
        else:
            color_string = ''
        return "%s -> %s%s;" % (self.__helper.sanitize_node_name(from_node),
                                self.__helper.sanitize_node_name(to_node),
                                color_string)

class GraphvizFormatterWrapper(object):
    def __init__(self):
        self.__formatter = GraphvizFormatter()
        
    def format(self, edges):
        """
        >>> GraphvizFormatterWrapper().format( (('a-', 'b-'),) )
        'graph {\\nb_ [ label="b-" ];\\na_ [ label="a-" ];\\na_ -> b_;\\n}'
        """
        nodes = set()
        nodes.update( (x for (x,_y) in edges) )
        nodes.update( (y for (_x,y) in edges) )
        return "\n".join(chain(
                          ("graph {",),
                          (self.__formatter.dot_node_dict(node, {'label': node}) for node in nodes),
                          (self.__formatter.dot_edge_dict(x,y, dict()) for (x,y) in edges),
                          ("}",) ) )
        
    def formatCZCH(self, edgesCZCH):
        return self.format( (x.node1.id, x.node2.id) for x in edgesCZCH)

# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
