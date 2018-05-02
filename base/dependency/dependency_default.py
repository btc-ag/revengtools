# -*- coding: UTF-8 -*-

'''
Created on 30.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_base import BaseDependencyFilterConfiguration
from base.dependency.dependency_generator_if import (
    DependencyGraphGeneratorFactory)
from base.dependency.dependency_if import (DependencyFilter, 
    DependencyFilterConfiguration)
from commons.graph.attrgraph_if import EdgeAttributes, NodeAttributes
from commons.graph.attrgraph_util import MutableAttributeGraph
import logging
import warnings

# TODO Dies sollte alles unabhängig von "Modul" sein. "Node" statt "Modul"

class DefaultDependencyFilter(DependencyFilter):
    """
    This class is not intended to be subclassed.
    """
    
    _supports_grouping = True

    def __init__(self,
                 config,
                 module_list,
                 default_edge_attrs=dict(),
                 *args, **kwargs):
        assert isinstance(config, DependencyFilterConfiguration)
        self.__initial_config = config
        self.__full_graph = MutableAttributeGraph(default_edge_attrs=dict({EdgeAttributes.COLOR: "red"}))
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__module_list = module_list
        self.__graph = None

    def __get_module_list(self):
        return self.__module_list

    def _edges(self):
        warnings.warn("use _graph().edges()", DeprecationWarning)
        return self.__graph.edges()

#    def _config(self):
#        return self.__initial_config

#    def _graph(self):
#        return self.__graph

#    def set_node_size(self, node, height, width):
#        self.__graph.set_node_attrs(node, {NodeAttributes.HEIGHT: height,
#                                            NodeAttributes.WIDTH: width}, create=True)

#    def set_node_shape(self, node, shape):
#        self.__graph.set_node_attrs(node, {NodeAttributes.SHAPE: shape}, create=True)

    def dependency(self, source, target):
        self.__full_graph.add_edge_and_nodes(source, target)

    @staticmethod
    def filter_graph(full_graph, dependency_filter_config, internal_modules):
        """
        
        @param full_graph:
        @param dependency_filter_config:
        @param internal_modules: All internal modules are added to the graph even if they are not 
            connected to any other module. If the graph is focused on a particular module group, 
            this applies only if they belong to this module group.
        """
        graph = MutableAttributeGraph()
        for module in internal_modules:
            if not dependency_filter_config.skip_module(module) and not dependency_filter_config.skip_module_as_source(module):
                graph.add_node(module)
        for edge in full_graph.edges():
            source = str(edge.get_from_node())
            target = str(edge.get_to_node())
            if not (dependency_filter_config.skip_module(source) \
                    or dependency_filter_config.skip_module(target) \
                    or dependency_filter_config.skip_module_as_source(source) \
                    or dependency_filter_config.skip_module_as_target(target) \
                    or dependency_filter_config.skip_edge(source, target)):
                graph.add_edge_and_nodes(source, target)
            else:
                if dependency_filter_config.skip_module_as_source(source) or dependency_filter_config.skip_edge(source, target):
                    #self.__logger.debug("recording skipped edge source %s->%s", source, target)
                    graph.set_node_attrs(source, {NodeAttributes.SKIPPED_FROM_EDGE: True}, True)
                if dependency_filter_config.skip_module_as_target(target) or dependency_filter_config.skip_edge(source, target):
                    #self.__logger.debug("recording skipped edge target %s->%s", source, target)
                    graph.set_node_attrs(target, {NodeAttributes.SKIPPED_TO_EDGE: True}, True)

        if dependency_filter_config.focus_on_node_groups:
            node_grouper = dependency_filter_config.get_module_grouper()
            exception_func = lambda node: node_grouper.get_node_group_prefix(node) in dependency_filter_config.focus_on_node_groups
        else:
            exception_func = lambda node: False
        graph.delete_unconnected_nodes(exception_func)
        return graph

    def __color_nodes(self):
        warnings.warn("use a node decorator instead", DeprecationWarning)
        for node in self.__full_graph.node_names_iter():
            color = self.__initial_config.get_node_color(str(node))
            self.__graph.set_node_attrs(node, {NodeAttributes.FILL_COLOR: color})

    def __color_edges(self):
        # TODO besser in einem Decorator. Wird das überhaupt noch benutzt?
        for edge in self.__full_graph.edges():
            edge.set_attrs({EdgeAttributes.COLOR:
                            self.__initial_config.get_edge_color(str(edge.get_from_node()),
                                                         str(edge.get_to_node())
                                                         )})

    def postamble(self):
        #self.__color_nodes()
        self.__color_edges()
        graph = self.filter_graph(full_graph=self.__full_graph, 
                                  dependency_filter_config=self.__initial_config,
                                  internal_modules=self.__get_module_list())
        self.__graph = graph.immutable()

    def graph(self):
        #return self.__graph.immutable()
        return MutableAttributeGraph(graph=self.__graph)

class NullDependencyGraphGeneratorFactory(DependencyGraphGeneratorFactory):

    def get_dependency_graph_generators(self, specification, exact_match=False, max_count=None):
        return ()

class NullDependencyFilterConfiguration(BaseDependencyFilterConfiguration):
    def __init__(self, modules=()):
        # TODO we need to make various assumptions about BaseDependencyFilterConfiguration to make it legal 
        # to pass an empty module list.
        BaseDependencyFilterConfiguration.__init__(self, modules=modules)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
