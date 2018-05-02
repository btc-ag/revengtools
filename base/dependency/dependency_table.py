# -*- coding: UTF-8 -*-
'''
Created on 26.10.2010

@author: SIGIESEC
'''
from commons.document.basic_if import Link
from commons.document.table_if import TableModel
from commons.graph.attrgraph_if import EdgeAttributes
from commons.graph.attrgraph_util import AttributedEdge
from commons.graph.graph_if import BasicGraph
from itertools import repeat, izip, chain, ifilter

class SimpleGraphTableModel(TableModel):
    def __init__(self, graph, *args, **kwargs):
        TableModel.__init__(self, *args, **kwargs)
        assert isinstance(graph, BasicGraph)
        self.__graph = graph

    def get_cell_content(self, cell_content):
        return (str(cell_content),)

    def get_data_columns(self, row_entries):
        assert isinstance(row_entries, AttributedEdge), "row_entries = %s, expected AttributedEdge" % row_entries
        return [row_entries.get_from_node(), row_entries.get_to_node()]

    def get_column_headers(self):
        return ["Dependency Source", "Dependency Target"]

    def get_rows(self):
        return izip(repeat(None), sorted(self.__graph.edges()))

    def has_row_headers(self):
        return False

class DecoratedGraphTableModel(TableModel):
    def __init__(self, graph, decorator_config, decoratee=None, *args, **kwargs):
        TableModel.__init__(self, *args, **kwargs)
        self.__graph = graph
        self.__decorated_nodes = dict()
        self.__decorator_config = decorator_config
        self.__decorator_config.attach_graph(graph)
        if not decoratee:
            decoratee = SimpleGraphTableModel(graph)
        else:
            assert isinstance(decoratee, TableModel)
        self.__decoratee = decoratee

    def get_row_header_text(self, keyval):
        return self.__decoratee.get_row_header_text(keyval)


    def __del__(self):
        self.__decorator_config.detach_graph()

    def has_row_headers(self):
        return self.__decoratee.has_row_headers()

    def __get_decorated_edge(self, edge):
        assert isinstance(edge, AttributedEdge)
        decorated_edge = chain.from_iterable(ifilter(None, (d.decorate(edge)
                               for d in chain(self.__decorator_config.get_edge_label_decorators(),
                                              self.__decorator_config.get_edge_tooltip_decorators()))))


        if EdgeAttributes.LINK in edge.get_attr_names():
            return Link(decorated_edge, edge.get_attr(EdgeAttributes.LINK))
        else:
            return decorated_edge

    def __get_decorated_node(self, node):
        if node not in self.__decorated_nodes:
            plain_node = self.__decoratee.get_cell_content(node)
            # TODO decorate node
            decorated_node = plain_node
            self.__decorated_nodes[node] = decorated_node
        return self.__decorated_nodes[node]

    def get_cell_content(self, cell_content):
        if isinstance(cell_content, AttributedEdge):
            return self.__get_decorated_edge(cell_content)
        else:
            return self.__get_decorated_node(cell_content)

    def get_data_columns(self, row_entries):
        return chain(self.__decoratee.get_data_columns(row_entries),
                     [row_entries])

    def get_column_headers(self):
        return chain(self.__decoratee.get_column_headers(),
                     ["Dependency Info"])

    def get_rows(self):
        return self.__decoratee.get_rows()
