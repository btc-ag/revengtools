# -*- coding: UTF-8 -*-
'''
Created on 12.10.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.graph.graph_if import BasicGraph
from itertools import chain, imap

class NodeGroupingConfiguration(AutoConfigurable):
    def collapse_node_group(self, module_group_prefix):
        """
        Determines whether the node group should be collapsed in the resulting graph,
        i.e. all nodes within the node group are replaced by one node representing the
        node group as a whole, and all edges to/from the nodes within the node group 
        are redirected to the node group representative.
        
        @rtype: C{BooleanType}
        """
        raise NotImplementedError
    
    def get_node_grouper(self):
        """
        Returns a node grouper according to the configuration represented by this object.
        
        @rtype: C{NodeGrouper}
        """
        raise NotImplementedError

class DecoratorSet(object):
    def __init__(self, node_label_decorators=(), edge_label_decorators=(),
                 node_tooltip_decorators=(), edge_tooltip_decorators=(), graph_decorators=()):
        assert all(imap(lambda decorator: isinstance(decorator, GraphDecorator), graph_decorators))
        assert all(imap(lambda decorator: isinstance(decorator, GraphElementDecorator), node_label_decorators))
        assert all(imap(lambda decorator: isinstance(decorator, GraphElementDecorator), edge_label_decorators))
        assert all(imap(lambda decorator: isinstance(decorator, GraphElementDecorator), node_tooltip_decorators))
        assert all(imap(lambda decorator: isinstance(decorator, GraphElementDecorator), edge_tooltip_decorators))
        self.__node_label_decorators = list(node_label_decorators)
        self.__edge_label_decorators = list(edge_label_decorators)
        self.__node_tooltip_decorators = list(node_tooltip_decorators)
        self.__edge_tooltip_decorators = list(edge_tooltip_decorators)
        self.__graph_decorators = list(graph_decorators)
        
    def get_all_decorators(self):
        return chain(self.__graph_decorators, 
                     self.__node_label_decorators, self.__node_tooltip_decorators,
                     self.__edge_label_decorators, self.__edge_tooltip_decorators)

    def get_graph_decorators(self):
        return self.__graph_decorators

    def get_node_label_decorators(self):
        return self.__node_label_decorators

    def get_edge_label_decorators(self):
        return self.__edge_label_decorators

    def get_node_tooltip_decorators(self):
        return self.__node_tooltip_decorators

    def get_edge_tooltip_decorators(self):
        return self.__edge_tooltip_decorators
    
    @staticmethod
    def unique_extend(decorator_list, additions):
        for add_decorator in additions:
            if all(imap(lambda decorator: add_decorator.__class__ != decorator.__class__, decorator_list)):
                decorator_list.append(add_decorator)
    
    def add_graph_decorators(self, additions):
        self.unique_extend(self.__graph_decorators, additions)
        return self

    def add_node_label_decorators(self, additions):
        self.unique_extend(self.__node_label_decorators, additions)
        return self

    def add_edge_label_decorators(self, additions):
        self.unique_extend(self.__edge_label_decorators, additions)
        return self

    def add_node_tooltip_decorators(self, additions):
        self.unique_extend(self.__node_tooltip_decorators, additions)
        return self

    def add_edge_tooltip_decorators(self, additions):
        self.unique_extend(self.__edge_tooltip_decorators, additions)
        return self
        
    def add_decorator_set(self, additions):
        self.add_graph_decorators(additions.get_graph_decorators())
        self.add_edge_label_decorators(additions.get_edge_label_decorators())
        self.add_node_label_decorators(additions.get_node_label_decorators())
        self.add_edge_tooltip_decorators(additions.get_edge_tooltip_decorators())
        self.add_node_tooltip_decorators(additions.get_node_tooltip_decorators())
        return self
    
    def attach_graph(self, graph):
        for decorator in self.get_all_decorators(): 
            decorator.attach_graph(graph)
        
    def detach_graph(self):
        for decorator in self.get_all_decorators(): 
            decorator.detach_graph()


class GraphOutputter(AutoConfigurable):
    def __init__(self, *args, **kwargs):
        pass
    
    @staticmethod
    def usual_extension():
        raise NotImplementedError
    
    def description(self):        
        raise NotImplementedError
    
    def output_all(self):
        raise NotImplementedError
    
    def register_log(self):
        raise NotImplementedError
    
class GraphOutputterFactory(AutoConfigurable):
    def __init__(self, *args, **kwargs):
        pass
    
    def is_graphical(self):
        raise NotImplementedError
    
    def usual_extension(self):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError

    def create_instance(self, *args, **kwargs):
        raise NotImplementedError

class TextualGraphOutputterFactory(GraphOutputterFactory, AutoConfigurable):
    def is_graphical(self):
        return False
    
class GraphicalGraphOutputterFactory(GraphOutputterFactory, AutoConfigurable):
    def is_graphical(self):
        return True

class TextualGraphOutputter(GraphOutputter, AutoConfigurable):
    pass

class GraphicalGraphOutputter(GraphOutputter, AutoConfigurable):
    pass
#    @staticmethod
#    def render_file(filename=None, description=None, show=False, *args, **kwargs):
#        """
#        Renders a file with the underlying layout engine.
#        
#        TODO also allow to process a stream or an internal representation.
#        
#        @param filename: the name of the input file
#        @param show: if True, also show the resulting file
#        @return: the name of the rendered file
#        """
#        raise NotImplementedError

class GraphDecorator(object):
    def decorate_graph(self, graph):
        raise NotImplementedError
    
class GraphElementDecorator(object):
    def description(self):
        raise NotImplementedError

    def attach_graph(self, graph):
        assert isinstance(graph, BasicGraph)
        raise NotImplementedError
        
    def detach_graph(self):
        raise NotImplementedError

    def decorate(self, graph_element):
        raise NotImplementedError

class RenderExecutor(object):
    def __init__(self, configuration):
        pass

    def _configuration(self):
        raise NotImplementedError(self.__class__)

    def create_renderer(self, output_file, on_success=None):
        raise NotImplementedError(self.__class__)

