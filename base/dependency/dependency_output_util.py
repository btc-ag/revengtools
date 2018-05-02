# -*- coding: UTF-8 -*-
'''
Created on 26.10.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.dependency.dependency_if import (OutputterConfiguration, ModuleGrouper, 
    DependencyFilter, NodeColorer, GraphDescription)
from base.dependency.dependency_util import (GraphDescriptionImpl, 
    DependencyFilterHelper)
from base.dependency.generation_log_if import GenerationLogGenerator
from commons.config_if import AutoConfigurable, ConfigDependent
from commons.core_if import EnumerationItem, Enumeration
from commons.core_util import HierarchicalDecomposer
from commons.graph.attrgraph_if import (NodeAttributes, GraphShapes, 
    EdgeAttributes, Colors)
from commons.graph.attrgraph_util import MultiGraph, AttributedEdge, NodeGroup
from commons.graph.graph_if import BasicGraph
from commons.graph.graph_util import GraphAlgorithms, SCCHelper
from commons.graph.output_base import BaseNodeDecorator, BaseEdgeDecorator
from commons.graph.output_if import (NodeGroupingConfiguration, DecoratorSet, 
    GraphicalGraphOutputter, GraphDecorator)
from commons.graph.output_util import (GraphCollapser, EdgeGroupDecorator, 
    NodeGroupDecorator)
from commons.os_util import PathTools
from commons.scm_default import FallbackVersionDescriber
from commons.scm_if import VersionDescriber
from itertools import ifilter
import logging
import math
import os.path
import posixpath
import types
import warnings

config_outputter_configuration = OutputterConfiguration()
config_basic = BasicConfig()
config_module_group_conf = NodeGroupingConfiguration
config_module_grouper = ModuleGrouper
config_version_describer = VersionDescriber()


class NodeGroupNodeGrouperDecorator(ModuleGrouper):
    def __init__(self, decoratee):
        self.__decoratee = decoratee
        self.__node_groups = None

    def configure_nodes(self, nodes):
        node_set = set(nodes)
        self.__node_groups = set(node for node in node_set if isinstance(node, NodeGroup))
        self.__decoratee.configure_nodes(node for node in node_set if not isinstance(node, NodeGroup))

    def get_node_group_prefix(self, module):
        if self.__node_groups == None:
            raise RuntimeError("Instance has not yet been configured")
        if module in self.__node_groups:
            return module.name()
        else:
            return self.__decoratee.get_node_group_prefix(module)

    def __my_node_group_prefixes(self):
        if self.__node_groups == None:
            raise RuntimeError("Instance has not yet been configured")
        return set(node.name() for node in self.__node_groups)    
    
    def node_group_prefixes(self):        
        return set(self.__decoratee.node_group_prefixes()) | self.__my_node_group_prefixes()



class NodeGroupingConfigurationDecorator(NodeGroupingConfiguration):
    
    def __init__(self, node_grouping_configuration, node_grouper_decorator):
        self.__decoratee = node_grouping_configuration
        self.__node_grouper = node_grouper_decorator(decoratee=node_grouping_configuration.get_node_grouper())

    def collapse_node_group(self, module_group_prefix):
        return self.__decoratee.collapse_node_group(module_group_prefix)

    def get_node_grouper(self):
        return self.__node_grouper

config_generation_log=GenerationLogGenerator()

# TODO This class should not be subclassed. Construction of the decorator set should be done 
# by a separate class. 
class DependencyFilterOutputter(AutoConfigurable, ConfigDependent):

    def __init__(self, decorator_config, base_graph=None, *args, **kwargs):
        AutoConfigurable.__init__(self, *args, **kwargs)
        self.outputters = config_outputter_configuration.outputters()
        assert isinstance(decorator_config, DecoratorSet)
        self.__decorator_config = decorator_config
        self.__logger = logging.getLogger(self.__class__.__module__)

    def add_decorators(self, decorator_config):
        self.__decorator_config.add_decorator_set(decorator_config)

    def get_decorator_config(self, filename):
        return self.__decorator_config

    def output_graph(self,
                     output_filename=None, # @deprecated: use description instead
                     outfile=None,
                     graph_outputter_factory=None,
                     graph=None,
                     node_group_conf=None,
                     collapse=True,
                     description=None,
                     generation_log=None,
                     add_graph_outputter_options=dict()):
        if not generation_log:
            warnings.warn("a generation log should be passed to output_graph")
            generation_log = config_generation_log
        if description != None:
            if isinstance(description, basestring):
                warnings.warn("passing string as description is deprecated, pass GraphDescription object instead", DeprecationWarning)
                description = GraphDescriptionImpl(description=description, basename=output_filename)
            else:
                if output_filename != None:
                    raise ValueError("do not set output_filename if description==GraphDescriptionImpl(...)")
        if outfile == None:
            output_filename = description.get_filename()
            if output_filename != None:
                # TODO replace graph_outputter_class by a proper abstract factory
                outfile = open(output_filename + graph_outputter_factory.usual_extension(), "w")
            else:
                pass
                #raise ValueError("Must specify either outfile or output_filename")
                # TODO this depends on the graph_outputter_class... this is true only if it outputs to a file

        # Assume a MultiGraph is already collapsed
        if collapse and not isinstance(graph, MultiGraph):
            assert node_group_conf != None and isinstance(node_group_conf, NodeGroupingConfiguration)
            graph = GraphCollapser.get_collapsed_graph(graph, node_group_conf)

        node_grouper = None
        if node_group_conf != None:
            node_grouper = node_group_conf.get_node_grouper()

        self.__logger.info("Writing graph %s to %s using outputter %s and grouping config %s" % (graph, outfile, graph_outputter_factory.get_name(), node_group_conf))

        graph_outputter = \
            graph_outputter_factory.create_instance(output_groups=True,
                                  graph=graph,
                                  outfile=outfile,
                                  node_grouper=node_grouper,
                                  decorator_config=self.get_decorator_config(output_filename),
                                  description=description,
                                  generation_log=generation_log,
                                  **add_graph_outputter_options)
        graph_outputter.output_all()
        # TODO die ganze Fallunterscheidung sollte hier entfernt werden.
#        if isinstance(graph_outputter, GraphicalGraphOutputter) and output_filename != None:
#            outfile.close()
#            graph_outputter.render_file(filename=output_filename, description=description)
#        else:
        graph_outputter.register_log()
        return graph_outputter


    def output(self,
               basename=None, # @deprecated:  
               suffix=None, # @deprecated: 
               filter=None,
               graph=None,
               module_group_conf=None,
               collapse=True,
               description=None):
        if description != None:
            if isinstance(description, GraphDescription):
                assert basename == None and suffix == None
            else:
                warnings.warn("deprecated, use description=GraphDescriptionImpl(...)", DeprecationWarning)
                description = GraphDescriptionImpl(description=description,
                                               basename=basename + suffix)
        if module_group_conf == None:
            warnings.warn("module_group_conf should be set", DeprecationWarning)
                
        if filter != None:
            assert isinstance(filter, DependencyFilter)
            if graph == None:
                graph = filter.graph()
        else:
            assert isinstance(graph, BasicGraph)
        if module_group_conf != None:
            # TODO !!! 20120129 This does not work if working on a collapsed graph. The 
            # nodes are NodeGroup instances then, but this cannot be determined when their names are passed.
            module_group_conf = NodeGroupingConfigurationDecorator(node_grouping_configuration=module_group_conf,
                                                                   node_grouper_decorator=NodeGroupNodeGrouperDecorator)
            module_group_conf.get_node_grouper().configure_nodes(graph.nodes_raw())

        # Assume a MultiGraph is already collapsed
        if collapse and not isinstance(graph, MultiGraph):
            assert module_group_conf != None
            graph = GraphCollapser.get_collapsed_graph(graph, module_group_conf)

        for graph_outputter_factory in self.outputters:
            if graph_outputter_factory.is_graphical() or not isinstance(graph, MultiGraph):
                self.output_graph(graph=graph,
                                  node_group_conf=module_group_conf,
                                  graph_outputter_factory=graph_outputter_factory,
                                  collapse=False,
                                  description=description)

config_dependency_filter_outputter = DependencyFilterOutputter

class DependencyFilterOutputterTools(ConfigDependent):
    @staticmethod
    def output_detail_and_overview_graph(graph,
                                         basename=None,
                                         outputter=None,
                                         decorator_config=None,
                                         node_grouper=None,
                                         module_group_conf=None,
                                         description=None,
                                         overview_graph=None,
                                         ):
        if description == None:
            warnings.warn("Missing description is now deprecated", DeprecationWarning)
            description = GraphDescriptionImpl(basename, "unknown graph")
        else:
            if isinstance(description, basestring):
                warnings.warn("use a GraphDescription as description", DeprecationWarning)
                description = GraphDescriptionImpl(basename=basename, description=description)
        if module_group_conf == None:
            if node_grouper == None:
                node_grouper = config_module_grouper()
            module_group_conf = config_module_group_conf(node_grouper)
        if outputter == None:
            outputter = config_dependency_filter_outputter(decorator_config=decorator_config)
        else:
            warnings.warn("Passing an outputter is deprecated, just pass decorator_config", DeprecationWarning)

        basenames = list()
        basenames.append(description.get_filename())
        group_decorator_set = DecoratorSet(edge_tooltip_decorators=[EdgeGroupDecorator()])
        outputter.add_decorators(group_decorator_set)
        outputter.output(graph=graph,
                         module_group_conf=module_group_conf,
                         collapse=False,
                         description=description)
        group_decorator_set = DecoratorSet(node_tooltip_decorators=[NodeGroupDecorator()])
        outputter.add_decorators(group_decorator_set)
        description.set_category(description.get_category() + "overview")
        basenames.append(description.get_filename())
        if overview_graph:
            outputter.output(graph=overview_graph,
                             module_group_conf=module_group_conf,
                             collapse=False,
                             description=description)
        else:
            outputter.output(graph=graph,
                             module_group_conf=module_group_conf,
                             collapse=True,
                             description=description)
        return basenames

class NodeSizeDecorator(BaseNodeDecorator):
    def __init__(self, size_func, *args, **kwargs):
        BaseNodeDecorator.__init__(self, *args, **kwargs)
        self.__size_func = size_func

    def _get_node_size(self, node):
        modules = self.node_tuple(node)
        sizes = map(self.__size_func, modules)
        return (sum(filter(None, sizes)), any(size == None for size in sizes))

class NodeSizeLabelDecorator(NodeSizeDecorator):
    def decorate(self, node):
        try:
            (size, missing) = self._get_node_size(node)
        except ValueError:
            return "(?)"
        if size != None:
            return "(%i%s)" % (size, "+?" if missing else "")
        else:
            return None

class _ScalingType(EnumerationItem):
    def __init__(self, map_func, *args, **kwargs):
        EnumerationItem.__init__(self, *args, **kwargs)
        self.__map_func = map_func

    def map(self, value):
        return self.__map_func(value)

class ScalingTypes(Enumeration):
    LINEAR = _ScalingType(lambda x: x)
    RADICAL = _ScalingType(math.sqrt)
    LOGARITHMIC = _ScalingType(math.log)

class NodeSizeScalingDecorator(NodeSizeDecorator):
    def __init__(self,
                 min_render_size,
                 max_render_size,
                 scale_type=ScalingTypes.RADICAL,
                 ignore=lambda x: False, *args, **kwargs):
        NodeSizeDecorator.__init__(self, *args, **kwargs)
        self.__min_render_size = min_render_size
        self.__max_render_size = max_render_size
        self.__scaling_type = scale_type
        self.__ignore = ignore
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__min_size = None
        self.__max_size = None

    def attach_graph(self, graph):
        assert isinstance(graph, BasicGraph)
        NodeSizeDecorator.attach_graph(self, graph)
        nodes = graph.nodes_raw()
        not_ignored_nodes = (node for node in nodes if not self.__ignore(str(node)))
        sizes = filter(None, (self._get_node_size(node)[0] for node in not_ignored_nodes))
        if len(sizes) > 0:
            self.__max_size = max(sizes)
            self.__min_size = min(sizes)
            self.__logger.debug("maximum node size: %f, minimum node size: %f",
                                self.__max_size, self.__min_size)
        else:
            self.__logger.debug("no matching nodes")
            self.__max_size = 1
            self.__min_size = 1

    def _adjusted_size(self, size):
        if size == None:
            return None

        assert isinstance(self.__min_size, (types.IntType, types.FloatType)), "min_size=%s" % self.__min_size
        assert size >= self.__min_size and size <= self.__max_size, \
            "size = %d, min_size = %d, max_size = %d" % (size, self.__min_size, self.__max_size)

        return_value = self.__min_render_size + \
            (self.__max_render_size - self.__min_render_size) * \
                self.__scaling_type.map(size - self.__min_size) / \
                    self.__scaling_type.map(self.__max_size)
        assert self.__min_render_size <= return_value and return_value <= self.__max_render_size, "adjusted_size = %f" % (return_value,)

        return return_value

    def decorate(self, node):
        try:
            if self.__ignore(str(node)):
                return None
            (size, _missing) = self._get_node_size(node)
            if size == 0:
                return None
            adjusted_size = self._adjusted_size(size)
            #adjusted_size = math.sqrt(size) / 20.0
            #adjusted_size = size / 4000.0
            #adjusted_size = math.log(size / 10.0)  
            if adjusted_size != None:
                self._graph().set_node_attrs(node, {NodeAttributes.WIDTH: adjusted_size,
                                            NodeAttributes.HEIGHT: adjusted_size})
        except ValueError:
            pass
        return None

class NodeWeightedDepsScalingDecorator(NodeSizeScalingDecorator):
    def __init__(self,
                 elementary_node_size_func,
                 base_graph=None,
                 *args, **kwargs):
        NodeSizeScalingDecorator.__init__(self, *args, **kwargs)
        self.__get_elementary_node_size = elementary_node_size_func
        self.__accessibility_matrix = None
        self.__has_base_graph = base_graph != None
        if self.__has_base_graph: 
            self._create_accessibility_matrix(base_graph)
        self.__logger = logging.getLogger(self.__class__.__module__)

    def _create_accessibility_matrix(self, graph):
        self.__accessibility_matrix = GraphAlgorithms.accessibility_matrix_from_graph(graph, 
                                                                                      inverse=False)

    def attach_graph(self, graph):
        if not self.__has_base_graph:
            self._create_accessibility_matrix(graph)
            #self.__logger.warning("accessibility matrix is %s" % pprint.pformat(self.__accessibility_matrix))
        NodeSizeScalingDecorator.attach_graph(self, graph)

    def detach_graph(self):
        if not self.__has_base_graph:
            self.__accessibility_matrix = None
        NodeSizeScalingDecorator.detach_graph(self)

    def get_weighted_module_deps(self, module):
        sizes = list()
        own_size = self.__get_elementary_node_size(module)
        if own_size:
            sizes.append(own_size)
        if module in self.__accessibility_matrix:
            sizes.extend(ifilter(None, (self.__get_elementary_node_size(reachable_node)
                                  for reachable_node in self.__accessibility_matrix[module])))
        if len(sizes) == 0:
            size = 0
        else:
            size = math.sqrt(sum(math.pow(size, 2) for size in sizes))

        self.__logger.debug("weight of %s is %s" % (module, size))
        return size


class TerminalNodeDecorator(BaseNodeDecorator):
    def __init__(self, *args, **kwargs):
        """
        
        @type config: DependencyFilterConfiguration
        """
        BaseNodeDecorator.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)

    def decorate(self, node):
        skipped_from = NodeAttributes.SKIPPED_FROM_EDGE in self._graph().node_attr_names(node)
        skipped_to = NodeAttributes.SKIPPED_TO_EDGE in self._graph().node_attr_names(node)
        if skipped_from and skipped_to:
            self._graph().set_node_attrs(node, {NodeAttributes.SHAPE: GraphShapes.TOPBOT})
        elif skipped_from:
            self._graph().set_node_attrs(node, {NodeAttributes.SHAPE: GraphShapes.BOT})
        elif skipped_to:
            self._graph().set_node_attrs(node, {NodeAttributes.SHAPE: GraphShapes.TOP})

class ModuleColorNodeDecorator(BaseNodeDecorator):
    def __init__(self, config, *args, **kwargs):
        BaseNodeDecorator.__init__(self, *args, **kwargs)
        assert isinstance(config, NodeColorer)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__config = config

    def decorate(self, node):
        #self.__logger.warning("Color decorating node %s" % (node,))
        #for node in self._graph().node_names_iter():
        color = self.__config.get_node_color(str(node))
        self._graph().set_node_attrs(node, {NodeAttributes.FILL_COLOR: color})

class FilenameURLNodeDecorator(BaseNodeDecorator, ConfigDependent):

    def __init__(self, *args, **kwargs):
        BaseNodeDecorator.__init__(self, *args, **kwargs)
        self.__basedir = config_basic.get_local_source_base_dir()

    def _get_abspath_for_node(self, node):
        if os.path.isabs(node):
            return node
        else:
            return posixpath.join(self.__basedir, node)

    def __get_url_for_node(self, node):
        abspath = self._get_abspath_for_node(node)
        return PathTools.get_url_for_local_path(abspath)

    def decorate(self, node):
        self._graph().set_node_attrs(node,
                                     {NodeAttributes.LINK:
                                      self.__get_url_for_node(node)})
        return None        

class SCCEdgeDecorator(BaseEdgeDecorator):
    """
    An edge decorator that highlights the strongly connected components in the graph. The strongly connected 
    components are assignednumbers which are added as labels to the edges within the SCCs and they are 
    coloured in red.
    """
    
    def __init__(self, *args, **kwargs):
        BaseEdgeDecorator.__init__(self, *args, **kwargs)
        self.__scc = None
        self.__logger = logging.getLogger(self.__class__.__module__)

    def attach_graph(self, graph):
        assert isinstance(graph, BasicGraph)
        BaseEdgeDecorator.attach_graph(self, graph)
        self.__scc = SCCHelper(graph)

    def detach_graph(self):
        BaseEdgeDecorator.detach_graph(self)
        self.__scc = None

    def decorate(self, edge):
        assert isinstance(edge, AttributedEdge)
        if edge.get_from_node() != edge.get_to_node():
            scc_edge_number = self.__scc.get_scc_number_of_edge(edge)
            if scc_edge_number != None:
                edge.set_attr(EdgeAttributes.COLOR, Colors.RED)
                return ("SCC %i" % scc_edge_number,)

class FileRevisionNodeAndGraphDecorator(BaseNodeDecorator, GraphDecorator, ConfigDependent):
    def __init__(self):
        BaseNodeDecorator.__init__(self)
        GraphDecorator.__init__(self)
        self.__version_describer = FallbackVersionDescriber(config_version_describer)
        self.__basedir = config_basic.get_local_source_base_dir()

    def decorate_graph(self, graph):
        return self.__version_describer.describe_local_version(self.__basedir, False)[2]

    def decorate(self, graph_element):
        return self.__version_describer.describe_local_version(self.__basedir + graph_element, False)[2]

class GenericGraphOutputter(ConfigDependent):
    @classmethod
    def output_graph(cls,
                     graph,
                     base_description,
                     more_description,
                     section,
                     module_group_conf,
                     base_name,
                     suffix):
        graph.delete_unconnected_nodes()
        #logger = logging.getLogger(cls.__class__.__module__)
        #if deleted_nodes:
        #    logger.info("deleted nodes: " + str(list(deleted_nodes)))
        description = GraphDescriptionImpl(description=base_description + more_description,
                                       basename=base_name + suffix,
                                       section=section)
        DependencyFilterOutputterTools.output_detail_and_overview_graph(graph=graph,
                                                                        module_group_conf=module_group_conf,
                                                                        outputter=config_dependency_filter_outputter(),
                                                                        description=description)


    @classmethod
    def graphs_for_dep_filter_configs(cls, full_graph, config_iter):
        """
        
        @param cls:
        @param full_graph:
        @param config_iter: an iterator over (GraphDescription, DependencyFilterConfiguration) tuples
        """
        graph_generation_function = lambda dep_filter_config: \
            DependencyFilterHelper.filter_graph(dependency_filter_configuration=dep_filter_config, graph=full_graph)
        for (description, dep_filter_config) in config_iter:
            yield (description, graph_generation_function(dep_filter_config))
        
    @classmethod
    def output_list_of_graphs(cls, module_grouper, full_graph, generated_graphs_iter):
        for description, graph in generated_graphs_iter:
            if graph.node_count() > 0:
                decorator_config = DecoratorSet(edge_label_decorators=[SCCEdgeDecorator()])
                outputter = config_dependency_filter_outputter(decorator_config, base_graph=full_graph)
                try:
                    DependencyFilterOutputterTools.output_detail_and_overview_graph(graph=graph, 
                                                                                    module_group_conf=config_module_group_conf(module_grouper), 
                                                                                    outputter=outputter, 
                                                                                    description=description, 
                                                                                    decorator_config=decorator_config)
                except Exception, exc:                    
                    logging.getLogger(cls.__module__).error("Exception during outputting of graph %s using %s" % (description,outputter,), exc_info=exc)
            else:
                logging.getLogger(cls.__module__).info("Graph '%s' is empty", description.get_full_description())

class PerGroupOutputter(object):
    @classmethod
    def graphs_focused_on_each_group(cls, 
                                     module_grouper, 
                                     dependency_filter_config_class,
                                     base_description,
                                     base_name,
                                     full_graph):
#        config_iter = ((GraphDescriptionImpl(description=base_description + " focused on " + node_group_prefix,
#                                             basename=base_name + "_" + node_group_prefix,
#                                             section="focused"), 
#                        dependency_filter_config_class(focus_on=[node_group_prefix], modules=full_graph.node_names_iter())) 
#                       for node_group_prefix in module_grouper.node_group_prefixes())   
        config_iter = ((GraphDescriptionImpl(description=base_description + " focused on " + node_group_prefix + (" (and below)" if level else ""),
                                             basename=base_name + "_" + node_group_prefix + (str(level) if level else ""),
                                             section="focused"), 
                        dependency_filter_config_class(focus_on=node_group_prefixes, modules=full_graph.node_names_iter())) 
                       for ((node_group_prefix, level), node_group_prefixes) in HierarchicalDecomposer(delimiter='.').cluster_all_levels(module_grouper.node_group_prefixes()))
        
        # TODO in general, it cannot be assumed the the delimiter '.' is used   
        return GenericGraphOutputter.graphs_for_dep_filter_configs(full_graph, config_iter)     

    @classmethod
    def output_focus_on_each_group(cls,
                                   module_grouper,
                                   base_name,
                                   base_description,
                                   dependency_filter_config_class,
                                   full_graph,
                                   ):
        """
        
        @param module_grouper: The module grouper that defines the node groups and the mapping of nodes to 
            node groups.
        @param graph_generation_function: A function that generates a graph using a given dep_filter_config, 
            as in
            lambda dep_filter_config: None
        @param base_name: The basic output filename, a fragment describing each focus is appended.
        @param base_description: The basic description, a description of each focus is appended.
        """
        
        # TODO man könnte bereits vor der Generierung prüfen, ob überhaupt Knoten innerhalb der Knotengruppe sind
        generated_graphs_iter = cls.graphs_focused_on_each_group(
            module_grouper, 
            dependency_filter_config_class, 
            base_description, 
            base_name, 
            full_graph=full_graph)
        GenericGraphOutputter.output_list_of_graphs(module_grouper, full_graph, generated_graphs_iter)

#doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
