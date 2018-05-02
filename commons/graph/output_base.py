# -*- coding: UTF-8 -*-
'''
Created on 12.10.2010

@author: SIGIESEC
'''
from base.dependency.generation_log_if import GenerationLogGenerator
from commons.config_if import ConfigDependent, ObjectFactory
from commons.core_util import CollectionTools
from commons.graph.attrgraph_base import NullNodeGrouper
from commons.graph.attrgraph_if import NodeGrouper, NodeAttributes
from commons.graph.attrgraph_util import MutableAttributeGraph, NodeGroup
from commons.graph.graph_if import BasicGraph, Edge
from commons.graph.output_if import (GraphOutputter, GraphElementDecorator, 
    NodeGroupingConfiguration, RenderExecutor, GraphicalGraphOutputter, 
    TextualGraphOutputter, TextualGraphOutputterFactory)
from commons.thread_util import Tee
from copy import copy
from itertools import ifilter, imap
import logging
import os.path
import warnings

class BaseGraphOutputter(GraphOutputter):
    _supports_grouping = True
    
    def __init__(self, output_groups, graph, outfile,
                 node_grouper,
                 decorator_config,
                 generation_log, 
                 description = None,
                 *args, **kwargs):
        GraphOutputter.__init__(self, output_groups, graph, outfile, node_grouper, *args, **kwargs) 
        assert isinstance(graph, BasicGraph)
        if node_grouper != None:
            assert isinstance(node_grouper, NodeGrouper)
        else:
            node_grouper = NullNodeGrouper() 
        
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__do_output_groups = output_groups
        self.__graph = MutableAttributeGraph(graph=graph)
        self.__outfile = outfile
        self.__node_grouper = node_grouper
        self.__decorator_config = decorator_config
        self.__description = description
        self.__generation_log = generation_log
        
    def _decorator_config(self):
        return self.__decorator_config
        
    def _node_label_decorators(self):
        return self.__decorator_config.get_node_label_decorators()

    def _edge_label_decorators(self):
        return self.__decorator_config.get_edge_label_decorators()

    def _node_tooltip_decorators(self):
        return self.__decorator_config.get_node_tooltip_decorators()

    def _edge_tooltip_decorators(self):
        return self.__decorator_config.get_edge_tooltip_decorators()

    def _node_grouper(self):
        return self.__node_grouper
        
    def file(self):
        return self.__outfile 
    
    def description(self):
        return self.__description.get_full_description()
    
    def _graph(self):
        return self.__graph

    def _render_edge(self, edge):
        raise NotImplementedError

    def _edge_decorations(self, edge):
        return CollectionTools.flatten(d.decorate(edge) 
                                       for d in self._edge_label_decorators())

    def _write_rendered_edge(self, rendered_edge):
        if len(rendered_edge):
            print >>self.file(), rendered_edge

    def _write_rendered_node(self, rendered_node):
        if len(rendered_node):
            print >>self.file(), rendered_node
            
    def _attach_decorators(self):
        self.__decorator_config.attach_graph(self._graph())
        
    def _detach_decorators(self):
        self.__decorator_config.detach_graph()
        
    def _output_edges(self):
        for edge in sorted(self._graph().edges()):
            rendered_edge = self._render_edge(edge)
            self._write_rendered_edge(rendered_edge)
            
    def _output_group(self, group_name, processed_nodes):
        warnings.warn("Not implemented")
            
    def _output_groups(self):
        if self.__do_output_groups and self._supports_grouping:
            self.__logger.debug("Outputting groups: YES")
            remaining_nodes = set(node for node in self._graph().nodes_raw() if not isinstance(node, NodeGroup))
            for group_prefix in self._node_grouper().node_group_prefixes():
                processed_nodes = set(node for node in remaining_nodes 
                                      if self._node_grouper().get_node_group_prefix(str(node)) == group_prefix)
                self.__logger.debug("Outputting group %s = (%s)" % (group_prefix, ",".join(imap(str, processed_nodes))))
                self._output_group(group_prefix, processed_nodes)
                remaining_nodes -= processed_nodes
        else:
            self.__logger.debug("Outputting groups: NO")
            
    def _render_node(self, node):
        raise NotImplementedError

    def _output_nodes(self):
        for node in self._graph().nodes_raw():
            if node != None:
                rendered_node = self._render_node(node)
                self._write_rendered_node(rendered_node)
            else:
                self.__logger.debug("node == None in _output_nodes")

    def _output_head(self):
        pass

    def _output_tail(self):
        pass


    def edges_before_nodes(self):
        return True
    
    
    def output_all(self):
        self.register_log()
        self.__logger.debug("Outputting graph %s using node grouper %s" % (self.__graph,
                                                                           self.__node_grouper))
        self._output_head()
        self._output_groups()
        self._attach_decorators()
        try:
            if self.edges_before_nodes():
                self._output_edges()
                self._output_nodes()
            else:
                self._output_nodes()
                self._output_edges()
        finally:
            self._detach_decorators()
        self._output_tail()
        
    def register_log(self):
        self.__generation_log.add_generated_file(description=self.__description, 
                                                 filename=self.file().name)
        
config_generation_log = GenerationLogGenerator()

class TextGraphOutputterFactory(TextualGraphOutputterFactory):
    def __init__(self, object_factory=ObjectFactory()):
        self.__object_factory = object_factory 

    def usual_extension(self):
        return TextGraphOutputter.usual_extension()

    def get_name(self):
        return TextGraphOutputter.__name__

    def create_instance(self, *args, **kwargs):
        return self.__object_factory.create_instance(xxclsxx=TextGraphOutputter, *args, **kwargs)

# TODO rename to CSVGraphOutputter?
class TextGraphOutputter(BaseGraphOutputter, TextualGraphOutputter, ConfigDependent):
    _supports_grouping = False
    sep = ','
    
    # TODO output node labels to avoid numeric ids to be the only content
    
    def __init__(self, generation_log=config_generation_log, *args, **kwargs):
        BaseGraphOutputter.__init__(self, generation_log=generation_log, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        if len(self._node_label_decorators()) > 0:
            self.__logger.debug("%s ignores node label decoraters = %s" % 
                            (self.__class__, self._node_label_decorators()))
        if len(self._edge_label_decorators()) > 0:
            self.__logger.debug("%s ignores edge label decoraters = %s" % 
                            (self.__class__, self._edge_label_decorators()))

    @staticmethod
    def usual_extension():
        return '.csv'
    
    def _render_node(self, node):
        return ""

    def _render_edge(self, edge):
        return "%s%s%s" % (edge.get_from_node(), self.sep, edge.get_to_node())
    

class DecoratingTextGraphOutputterFactory(TextualGraphOutputterFactory, ConfigDependent):
    def __init__(self, object_factory=ObjectFactory()):
        self.__object_factory = object_factory 

    def usual_extension(self):
        return DecoratingTextGraphOutputter.usual_extension()

    def get_name(self):
        return DecoratingTextGraphOutputter.__name__

    def create_instance(self, *args, **kwargs):
        return self.__object_factory.create_instance(xxclsxx=DecoratingTextGraphOutputter, *args, **kwargs)


class DecoratingTextGraphOutputter(BaseGraphOutputter, TextualGraphOutputter):
    _supports_grouping = False
    long_decorations = True
    sep = ' -> '

    def __init__(self, generation_log=config_generation_log, *args, **kwargs):
        BaseGraphOutputter.__init__(self, generation_log=generation_log, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        if len(self._node_label_decorators()) > 0:
            self.__logger.debug("%s ignores node label decoraters = %s" % 
                            (self.__class__, self._node_label_decorators()))
    
    @staticmethod
    def usual_extension():
        return '.txt'
    
    def _render_node(self, node):
        return ""

    def _render_edge(self, edge):
        result = "%s%s%s" % (edge.get_from_node(), self.sep, edge.get_to_node())
        edge_decorations = list(self._edge_decorations(edge))
        edge_decorations_str = ""
        if len(edge_decorations) > 0:
            if self.long_decorations:
                edge_decorations_str = "\n" + "\n".join(edge_decorations) + "\n"
            else:
                edge_decorations_str = " [" + ", ".join(edge_decorations) + "]"
        return result + edge_decorations_str


        
class BaseGraphElementDecorator(GraphElementDecorator):
    def __init__(self):
        self.__graph = None
        
    def _graph(self):
        return self.__graph
    
    def attach_graph(self, graph):
        assert isinstance(graph, BasicGraph)
        assert self.__graph == None, "Decorator %s has already an attached graph" % self
        self.__graph = graph
        
    def detach_graph(self):
        self.__graph = None

    def description(self):
        return self.__class__.__name__

    def decorate(self, graph_element):
        raise NotImplementedError

    @staticmethod
    def decorations(decorators, graph_element):
        """
        Returns an iterator over the decorations of the graph_element with each decorator.
        """
        return ifilter(None, (d.decorate(graph_element) for d in decorators))
        
class BaseNodeDecorator(BaseGraphElementDecorator):
    def node_tuple(self, node):
        if NodeAttributes.GROUPED_NODES in self._graph().node_attr_names(node):
            modules = self._graph().node_attr(node, NodeAttributes.GROUPED_NODES)
        else:
            modules = node, 
        return modules

    def decorate(self, graph_element):
        raise NotImplementedError

class BaseEdgeDecorator(BaseGraphElementDecorator):
    def decorate(self, graph_element):
        assert isinstance(graph_element, Edge)
        raise NotImplementedError

class BaseNodeGroupingConfiguration(NodeGroupingConfiguration):
    def __init__(self, node_grouper):
        assert isinstance(node_grouper, NodeGrouper)
        self.__node_grouper = node_grouper

    def get_node_grouper(self):
        return self.__node_grouper

class NullRenderExecutor(RenderExecutor):
    def __init__(self, configuration, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)

    def create_renderer(self, output_file, on_success=None):
        if on_success != None:
            self.__logger.warning("%s does not support success hook, executing regardless of success",
                                  self.__class__)
            on_success()
        return output_file

class GenericRenderingGraphOutputter(GraphicalGraphOutputter):    
    def __init__(self, description, outfile, graph, *args, **kwargs):
        GraphicalGraphOutputter.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__module__)
        self.__description = description
        self.__dot_outfile = outfile
        self.__graph = graph
        self.__render_executors = list()
        self.__args = args
        self.__kwargs = kwargs

    def register_log(self):
        # do nothing here, log registering is done on completion of each rendering job
        pass

    def description(self):
        return self.__description
    
    def _dot_outfile(self):
        return self.__dot_outfile

    @classmethod
    def usual_extension(cls):
        return cls._get_renderer_input_generator_graph_outputter().usual_extension()

    def __create_render_executor(self, rendering_configuration):
        output_filename = os.path.normpath(self.__description.get_filename() +  rendering_configuration.get_file_extension())
        render_executor_class = self._get_executor_class_and_outfile(rendering_configuration)
        if render_executor_class == NullRenderExecutor:
            # TODO das ist nicht schön... Hier sollte nicht der Typ abgefragt werden.
            outfile = self.__dot_outfile
        else:
            outfile = open(output_filename, "wb")

        self.__logger.info("rendering %s using %s", output_filename, render_executor_class.__name__)

        render_executor = render_executor_class(configuration=rendering_configuration)

        if self.__description == None:
            self.__logger.warning("No description set")
            add_log_func = None
        else:
            description = copy(self.__description)
            add_log_func = lambda: config_generation_log.add_generated_file(filename=output_filename,
                                                     description=description)

        pipe = render_executor.create_renderer(outfile,
                                           on_success=add_log_func)
        return (render_executor, pipe)

        #TODO introduce class parameter for configuring showing
        #if show:
        #    os.system("start %s" % (output_filename, ))

    def __create_renderers(self, rendering_configurations):
        pipes = list()
        for rendering_configuration in rendering_configurations:
            try:
                render_executor, pipe = self.__create_render_executor(rendering_configuration)
                self.__render_executors.append(render_executor)
                pipes.append(pipe)
            except:
                self.__logger.error("Creating renderer failed for rendering_configuration = %s" % (rendering_configuration, ), exc_info=True)
        
        return pipes

    def _generate_renderer_input_file(self, output_pipe):
        dot_outputter = self._get_renderer_input_generator_graph_outputter()(description=self.__description, outfile=output_pipe, 
            graph=self.__graph, *self.__args, **self.__kwargs)
        dot_outputter.output_all()

    def output_all(self):
#        rendering_configurations = (RenderingConfiguration(aspect_ratio=config_graphviz.get_aspect_ratio(),
#                                                           output_format=config_graphviz.get_output_format(),
#                                                         ), )
        pipes = self.__create_renderers(self._rendering_configurations())
            
        tee = Tee(out_files=pipes)
        try:
            self._generate_renderer_input_file(output_pipe=tee.stdin())
        finally:
            tee.close()

    def _rendering_configurations(self):
        raise NotImplementedError(self.__class__)

    @classmethod
    def _get_renderer_input_generator_graph_outputter(cls):
        raise NotImplementedError(cls)

    def _get_executor_class_and_outfile(self, rendering_configuration):
        raise NotImplementedError(self.__class__)
    
    def _graph(self):
        return self.__graph
    
    