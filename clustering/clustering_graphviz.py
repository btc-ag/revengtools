#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.serverpath_if import ServerPath
from commons.os_util import PrinterDecorator
from commons.graph.graph_util import PartitionGraph
from infrastructure.graph_layout.graphviz.graphviz import GraphvizFormatter
import logging
import pprint
import sys

config_pathtools = ServerPath

# TODO Das ist Käse... einerseits sollte das den GraphOutputter verwenden und nicht Graphviz-spezifisch sein. 
# Andererseits: wieso leitet das von PartitionGraph ab?

class AbstractClusteringGraphvizOutput(PartitionGraph):
    split_rest = None
    max_node_size = 5.0
    min_node_size = 3.0

    def __init__(self, out_file = sys.stdout):
        self.__outputter = PrinterDecorator(GraphvizFormatter(), out_file)
        
    def outputter(self):
        return self.__outputter

    def simple_node_name(self, files):
        """
        >>> x = AbstractClusteringGraphvizOutput() 
        >>> x.simple_node_name('a') # doctest:+ELLIPSIS    
        '...'
        
        >>> x.simple_node_name(('a')) == x.simple_node_name(('a'))
        True

        >>> x.simple_node_name(frozenset(['a','b'])) == x.simple_node_name(frozenset(['b','a']))
        True
        """
        return str(files.__hash__())

    def cluster_node_name(self, cluster):
        """
        >>> x = AbstractClusteringGraphvizOutput()
        >>> x.cluster_node_name('a') # doctest:+ELLIPSIS
        '...'

        >>> x.cluster_node_name(('a')) # doctest:+ELLIPSIS
        '...'
        """
        #return "cluster_" + self.simple_node_name(cluster)
        return self.simple_node_name(cluster)

    def find_dependencies(self, moduleDependenciesClustered, cluster, elem, _nodeNameFun):
        found = 0
        for key in moduleDependenciesClustered.keys():
            if elem in moduleDependenciesClustered[key]:
                self.add_node((self.simple_node_name(cluster), cluster))
                self.add_node((self.simple_node_name(moduleDependenciesClustered[key]), moduleDependenciesClustered[key]))

                self.add_edge((self.simple_node_name(cluster), self.simple_node_name(moduleDependenciesClustered[key])))
#                print graphviz.dot_edge(nodeNameFun(cluster), 
#                    nodeNameFun(moduleDependenciesClustered[key]))
                found += 1
        return found


    def find_remaining(self, _moduleDependenciesClustered, clusterKey):
        return list(clusterKey)

    def sizeable_nodes(self):
        return set(self.__nodes.keys())

    def format_label(self, label):
        """
        TODO Use default implementation instead of CASTPathTools 
        
        >>> from cast.castutils import CASTPathTools 
        >>> sys.modules['__main__'].config_pathtools = CASTPathTools
        >>> x = AbstractClusteringGraphvizOutput()
        >>> x.format_label('abc')
        'abc'

        >>> x.format_label(('abc', 'bcd'))
        'abc\\\\nbcd'
        """
#        logging.debug("format_label(%s (type %s))" % (label, type(label)))
        if isinstance(label, basestring):
            if config_pathtools.is_server_path(label):
                return config_pathtools.server_path_to_basename(label)
            else:
                return label
        elif isinstance(label, tuple):
            return "\\n".join([self.format_label(x) for x in label])
        else:
            raise TypeError("Unsupported type: %s" % type(label))

    def construct_node(self, nodeNameFun, files):
        """
        >>> x = AbstractClusteringGraphvizOutput()
        >>> x.construct_node(x.cluster_node_name, ('C:\\X.C', 'C:\\Y.C')) # doctest:+ELLIPSIS
        ('...', ('C:\\\\X.C', 'C:\\\\Y.C'))
        """
        return (nodeNameFun(files), files)

    def output_edges(self):
        for (fromNode, toNode) in self.__edges:
            self.outputter().dot_edge(fromNode,
                toNode)

    def node_color(self, node):
        return "white"

    def output_nodes(self):
        sizeableNodes = self.sizeable_nodes()
        logging.debug("sizeableNodes = %s", sizeableNodes)
        maxSize = max([self.size_node(self.__nodes[node]) for node in sizeableNodes])
        minSize = min([self.size_node(self.__nodes[node]) for node in sizeableNodes])
        logging.debug("maxSize = %i, minSize = %i", maxSize, minSize)
        if maxSize == minSize:
            maxSize = 1
            minSize = 0
        for    node, nodelabel in self.__nodes.iteritems():
            params = {"label": self.format_label(nodelabel),
					"fillcolor": self.node_color(node)}
            if node in sizeableNodes:
                params.update({"size": self.min_node_size
							+ self.size_node(nodelabel) / (maxSize - minSize)
							* (self.max_node_size - self.min_node_size)})
            else:
                params.update({"size": self.max_node_size, "fillcolor": "red"})
            self.outputter().dot_node_dict(node, params)

    def process_remaining(self, remaining, cluster):
        """
        >>> x = AbstractClusteringGraphvizOutput()
        """
        node = self.construct_node(self.simple_node_name, remaining)
        #logging.debug(pprint.pformat(node))
        overlaps = self.find_overlapping_nodes(node)
        if len(overlaps) == 0:
            self.add_node(node)
            self.add_edge((node[0],
                self.cluster_node_name(cluster)))
        else:
            logging.debug("Overlapping node exists: new = %s:%s, old = %s:%s",
                          node[0], node[1], overlaps,
                          [self.__nodes[x] for x in overlaps])
            rest = set(node[1])
            for overlap in overlaps:
                if (node[0] == overlap and len(overlaps) == 1) or \
                        set(self.__nodes[overlap]).issubset(node[1]):
                    self.add_edge((overlap, self.cluster_node_name(cluster)))
                else:
                    logging.debug("Overlapping node %s should be split, new node = %s",
                                  pprint.pformat(self.__nodes[overlap]), pprint.pformat(node[1]))
                    self.add_edge((overlap, self.cluster_node_name(cluster)))
                rest.difference_update(self.__nodes[overlap])
            if len(rest) > 0:
                self.process_remaining(tuple(rest), cluster)

        return node

    def process(self, moduleDependenciesClustered):
        for clusterKey, cluster in moduleDependenciesClustered.iteritems():
            self.add_node(self.construct_node(self.cluster_node_name, cluster))
            for elem in clusterKey:
                if self.find_dependencies(moduleDependenciesClustered, cluster,
										elem, self.cluster_node_name) == 0:
                    logging.debug("Missing %s in (%s: %s)", elem, clusterKey,
								cluster)
                    rest = self.find_remaining(moduleDependenciesClustered,
											clusterKey)
                    if self.split_rest:
                        for module in rest:
                            self.process_remaining(tuple([module]), cluster)
                    else:
                        if len(rest) > 0:
                            self.process_remaining(rest, cluster)

        #logging.debug("Missing nodes: %s" % pprint.pformat(self.missing_nodes()))
        #logging.debug("All nodes: %s" % pprint.pformat(self.nodes))

    def output_graphviz(self):
        self.outputter().head()
        self.output_nodes()
        self.output_edges()
        self.outputter().tail()

    def size_node(self, node):
        """
    	
        @deprecated: use size_node_key instead
        """
        return self.size_node_key(node[0])

    def size_node_key(self, nodeKey):
        return len(self.__nodes[nodeKey])

    def pick_top(self, count, targetNodeLabel = 'REST',
				cmpFun = lambda nodes: lambda x, y: cmp(len(nodes[y]), len(nodes[x]))):
        """
        Restricts the result to the first <count> nodes according to the sort order induced by <cmpFun>. All other nodes are joined 
        into one node, the label of which becomes <targetNodeLabel>, if <targetNodeLabel> is not None, otherwise it will be the union 
        of the labels of all joined nodes.
        """
        keysSorted = sorted(self.__nodes.keys(), cmpFun(self.__nodes))

        self.add_node((str(id(self)), tuple()))
        for i in range(count + 1, len(keysSorted)):
#            self.del_node(keysSorted[i])
            self.join_nodes(str(id(self)), keysSorted[i])
        if targetNodeLabel != None:
            self.change_node((str(id(self)), (targetNodeLabel,)))


# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
