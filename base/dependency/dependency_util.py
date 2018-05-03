#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 24.09.2010

@author: SIGIESEC
'''

from base.basic_config_if import BasicConfig
from base.dependency.dependency_default import (DefaultDependencyFilter, 
    NullDependencyFilterConfiguration)
from base.dependency.dependency_generator_if import (
    DependencyGraphGeneratorFactory, DependencyGraphSpecification, 
    DependencyGraphGenerator)
from base.dependency.dependency_if import (GraphDescription, DependencyFilter, 
    DependencyFilterConfiguration)
from base.dependency.dependency_if_deprecated import DependencyParser
from base.modules_if import ModuleListSupply
from commons.config_if import ConfigDependent
from commons.core_util import IterTools, StringTools, SetValuedDictTools
from commons.graph.graph_if import BasicGraph
from commons.graph.graph_util import GraphAlgorithms
from commons.v26compat_util import compatnext
from itertools import ifilter, islice, imap
import math
import os.path
from commons.graph.attrgraph_util import MutableAttributeGraph
from commons.graph.attrgraph_if import NodeAttributes

class DependencyParserHelper(object):
    @staticmethod
    def get_full_graph(dependency_parser, internal_modules):
        assert isinstance(dependency_parser, DependencyParser)
        dependency_filter = DefaultDependencyFilter(config=NullDependencyFilterConfiguration(), 
                                                    module_list=internal_modules)
        dependency_parser.output(dependency_filter)
        return dependency_filter.graph()

class AggregateMapper(object):
    """
    This class considers three levels of elements: input aggregate, output aggregate and individual.
    It provides means for mapping individual elements between an input aggregate level and an output 
    aggregate level, which is finer than the input aggregate level.
    A typical example (for C++, see also cpp.cpp_util.FileNameMapper) is:
    input aggregate=module, 
    individual=file, 
    output aggregate=set of related header & implementation files.
    
    >>> func = lambda filename: os.path.splitext(os.path.basename(filename))[0]
    >>> mapper = AggregateMapper({"A/a.cpp": "A", "B/a.cpp": "B", "B/b.cpp": "B"}, ("A", "B"), optimiseNodeNames=True, local_output_aggregate_for_individual_func=func)
    >>> mapper.get_input_aggregate_for_individual("A/a.cpp")
    'A'
    >>> mapper.get_output_aggregate_for_individual("A/a.cpp")
    'A:a'
    >>> mapper.get_output_aggregate_for_individual("B/b.cpp")
    'b'
    >>> sorted(mapper.get_individuals_for_output_aggregate('A:a'))
    ['A/a.cpp']
    >>> sorted(mapper.get_individuals_for_output_aggregate('b'))
    ['B/b.cpp']
    >>> mapper = AggregateMapper({"A/a.cpp": "XA", "B/a.cpp": "XB", "B/b.cpp": "XB"}, ("XA", "XB"), optimiseNodeNames=True, local_output_aggregate_for_individual_func=func)
    >>> sorted(mapper.get_individuals_for_output_aggregate('A:a'))
    ['A/a.cpp']
    """
    
    def __local_output_aggregate_to_input_aggregate_iteritems(self):
        individuals = ifilter(self.is_file_in_input_aggregates, self.__individual_to_input_aggregate_map)
        selected = ((individual, self.__filtered_input_aggregate_for_individual(individual)) 
                    for individual in individuals 
                    if self.__filtered_input_aggregate_for_individual(individual) in self.__selected_input_aggregates)        
        second_of = lambda element: compatnext(islice(element, 1, 2))
        key_func = lambda (individual, input_aggregate): self.__local_output_aggregate_for_individual_func(individual)
        return ((output_aggregate, set(imap(second_of, elements))) 
                for output_aggregate, elements in IterTools.sort_and_group(key_func, selected))
#     original non-functional version:
#        local_output_aggregate_to_input_aggregate_map = dict()
#        for individual in ifilter(self.is_file_in_input_aggregates, self.__individual_to_input_aggregate_map):
#            input_aggregate = self.__filtered_input_aggregate_for_individual(individual)
#            if input_aggregate in self.__selected_input_aggregates:
#                local_output_aggregate = self.__local_output_aggregate_for_individual_func(individual)
#                SetValuedDictTools.add_or_create(local_output_aggregate_to_input_aggregate_map, 
#                                                 local_output_aggregate, 
#                                                 input_aggregate)        
#        return local_output_aggregate_to_input_aggregate_map

    def __init__(self, file_to_module_map, modules, local_output_aggregate_for_individual_func, optimiseNodeNames=False, optimiseModuleNames=True, get_raw_modulename=lambda x: x):
        self.__selected_input_aggregates = modules
        self.__individual_to_input_aggregate_map = file_to_module_map
        self.__local_output_aggregate_to_input_aggregate_map = None
        self.__filter_input_aggregate_func = get_raw_modulename
        self.__local_output_aggregate_for_individual_func = local_output_aggregate_for_individual_func
        if optimiseNodeNames and len(self.__selected_input_aggregates) > 1:
            self.__local_output_aggregate_to_input_aggregate_map = \
                dict(self.__local_output_aggregate_to_input_aggregate_iteritems())
        if optimiseModuleNames:
            self.__selected_input_aggregates_common_prefix, self.__optimised_input_aggregates = \
                StringTools.prefix_optimise(self.__selected_input_aggregates)
        else:
            self.__optimised_input_aggregates = dict()
            self.__selected_input_aggregates_common_prefix = ""

    def __filtered_input_aggregate_for_individual(self, individual):
        return self.__filter_input_aggregate_func(self.__individual_to_input_aggregate_map[individual])

    def is_file_in_input_aggregates(self, individual):
        return self.__filtered_input_aggregate_for_individual(individual) in self.__selected_input_aggregates
    
    def get_pseudomodule_name(self, individual):
        if self.is_file_in_input_aggregates(individual):
            return self.get_output_aggregate_for_individual(individual)
        else:
            return individual
        
    def get_full_input_aggregate(self, input_aggregate):
        return "".join((self.__selected_input_aggregates_common_prefix, input_aggregate))

    def is_individual_in_input_aggregate(self, input_aggregate, individual):
        return self.__filtered_input_aggregate_for_individual(individual) == self.get_full_input_aggregate(input_aggregate)

    def get_individuals_for_output_aggregate(self, global_output_aggregate):
        if ':' in global_output_aggregate:
            (input_aggregate, _local_output_aggregate) = global_output_aggregate.split(':')
        else:
            input_aggregate = None            
            #_local_output_aggregate = global_output_aggregate
        result = []
        # TODO suboptimal
        for individual in self.__individual_to_input_aggregate_map.iterkeys():
            if not input_aggregate or self.is_individual_in_input_aggregate(input_aggregate, individual):
                if self.get_output_aggregate_for_individual(individual) == global_output_aggregate:
                    result.append(individual)
        return result

    def get_input_aggregate_for_individual(self, individual):
        filtered_input_aggregate = self.__filtered_input_aggregate_for_individual(individual)
        return self.__optimised_input_aggregates.get(filtered_input_aggregate, filtered_input_aggregate)

    def get_output_aggregate_for_individual(self, individual):
        local_output_aggregate = self.__local_output_aggregate_for_individual_func(individual)
        if (not self.__local_output_aggregate_to_input_aggregate_map or len(self.__local_output_aggregate_to_input_aggregate_map[local_output_aggregate]) > 1) and len(self.__selected_input_aggregates) > 1:
            return self.get_input_aggregate_for_individual(individual) + ":" + local_output_aggregate
        else:
            return local_output_aggregate
        
class AggregateMapperGraphTools(object):
    @staticmethod
    def aggregate_graph(mapper, ignore_external, exceptions, file_graph):
        assert(isinstance(mapper, AggregateMapper))
        pseudomodule_graph = MutableAttributeGraph()
        for edge in file_graph.edges():
            from_node = mapper.get_output_aggregate_for_individual(edge.get_from_node())
            if mapper.is_file_in_input_aggregates(edge.get_to_node()):
                to_node = mapper.get_output_aggregate_for_individual(edge.get_to_node())
                if not (from_node == to_node or (from_node, to_node) in exceptions):
                    pseudomodule_graph.add_edge_and_nodes(from_node, to_node)
                else:
                    pseudomodule_graph.add_node(from_node)
                    pseudomodule_graph.add_node(to_node)
            elif not ignore_external:
                to_node = edge.get_to_node()
                pseudomodule_graph.add_edge_and_nodes(from_node, to_node)
            else:
                pseudomodule_graph.add_node(from_node)
                
        # TODO warum wird das gemacht?
        for node in pseudomodule_graph.nodes_raw():
            pseudomodule_graph.set_node_attrs(node, {NodeAttributes.LABEL: ""})             
        
        return pseudomodule_graph
    

class ReferencingModules(object):
    """
    >>> rm = ReferencingModules([('a', 'b'), ('b', 'c')], [('a', 'X'), ('b', 'Y'), ('c', 'Z')])
    >>> rm.get_referencing_module_count('a')
    0
    >>> rm.get_referencing_module_count('c')
    2
    >>> sorted(rm.get_referencing_modules_iter('c'))
    ['X', 'Y']
    >>> rm = ReferencingModules([('a', 'b'), ('b', 'c')], [('a', 'X'), ('b', 'Y'), ('c', 'Z')], use_transitive_closure=False)
    >>> rm.get_referencing_module_count('a')
    0
    >>> sorted(rm.get_referencing_modules_iter('c'))
    ['Y']
    >>> rm.get_referencing_module_count('d')
    0
    """
    def __init__(self, 
                 file_dependencies,
                 file_to_module_map,
                 use_transitive_closure=True,
                 module_name_filter=lambda module: module
                 ):
        if use_transitive_closure:
            unique_file_dependencies = set((src, dst) for (src, dst) in file_dependencies)
            self.__reverse_file_dependencies = SetValuedDictTools.convert_from_itemiterator((target, source) 
                                                               for (source, target) in GraphAlgorithms.transitive_closure(unique_file_dependencies))
        else:            
            self.__reverse_file_dependencies = SetValuedDictTools.convert_from_itemiterator((target,source) for (source,target) in file_dependencies)
        self.__target_files_to_referencing_modules_map = dict()        
        self.__files_to_modules_raw = dict(file_to_module_map)
        self.__module_name_filter = module_name_filter
    
    def __get_referencing_files_iter(self, target_file): #functional
        return iter(self.__reverse_file_dependencies.get(target_file, []))

    def __get_referencing_modules(self, target_file): #functional
        if target_file not in self.__target_files_to_referencing_modules_map:
            self.__target_files_to_referencing_modules_map[target_file] = frozenset(ifilter(lambda module: len(module) != 0 and module != self.__module_name_filter(self.__files_to_modules_raw[target_file]), 
                                                               (self.__module_name_filter(self.__files_to_modules_raw.get(filename, "")) 
                                                                for filename in self.__get_referencing_files_iter(target_file))))
        return self.__target_files_to_referencing_modules_map[target_file]

    def get_referencing_modules_iter(self, target_file): #functional
        return iter(self.__get_referencing_modules(target_file))

    def get_referencing_module_count(self, target_file): #functional
        return len(self.__get_referencing_modules(target_file))

class ComponentDependencyMetric(object):
    def __init__(self, graph=None, accessibility_matrix=None, weight_function=None):
        assert len(filter(None, (graph, accessibility_matrix)))==1, "Either graph or accessiblity_matrix must be set"
        if accessibility_matrix:
            self.__accessibility_matrix = accessibility_matrix
        else:
            self.__accessibility_matrix = GraphAlgorithms.accessibility_matrix_from_graph(graph)        
        self.__weight_function = weight_function
        assert weight_function == None, "TODO using a weight function support is not yet implemented"

    def calculate_ccd(self):
        # TODO auch gewichtete ACD berechnen (gewichten nach beliebiger Metrik, z.B. LOC)
        return float(sum(len(accessibles) - 1 for accessibles in self.__accessibility_matrix.values()))

    def calculate_acd(self):
        """
        Calculates the average component dependency (ACD) for the object's system.
        """
        nodes = len(self.__accessibility_matrix)
        if nodes > 0:
            return self.calculate_ccd() / (nodes * (nodes - 1))
        else:
            return float("nan")

    @staticmethod
    def calculate_ccd_balanced_binary_tree(nodes):
        return (nodes + 1) * math.log(nodes + 1, 2) - nodes

    def calculate_nccd(self):
        """
        Calculates the normalized CCD for the graph, i.e. the ratio of the CCD and the optimal CCD 
        of a system with the same number of elements.
        """
        nodes = len(self.__accessibility_matrix)
        if nodes > 0:
            return self.calculate_ccd() / self.calculate_ccd_balanced_binary_tree(nodes)
        else:
            return float("nan")

config_dependency_graph_factory = DependencyGraphGeneratorFactory()

class DependencyGraphGeneratorTools(object):
    @staticmethod
    def retrieve_dependency_graph(specification, exact_match=False, factory=None):
        """
        Gets the best matching generator from a dependency graph generator factory
        and retrieve the dependency from it.
        
        @param specification: A specification 
        @param exact_match: the parameter is passed to the factory.
        @param factory: The dependency graph factory to be used. If None, the dependency graph 
            factory is retrieved from the configuration.
        @type factory: DependencyGraphGeneratorFactory or NoneType
        """
        if factory == None:
            factory = config_dependency_graph_factory
        assert isinstance(factory, DependencyGraphGeneratorFactory)
        assert isinstance(specification, DependencyGraphSpecification)
        generator = IterTools.first(factory.get_dependency_graph_generators(specification, max_count=1))
        if generator:
            assert isinstance(generator, DependencyGraphGenerator)
            return generator.retrieve_graph()
        else:
            return None

config_basic = BasicConfig()

class GraphDescriptionImpl(GraphDescription):
    def __init__(self, description, basename=None, section=None, category=None, extra=None, legend=None):
        self.__section = section
        self.__category = category
        self.__description = description
        self.__basename = basename
        self.__extra = extra
        self.__legend = legend

    def get_legend(self):
        return self.__legend


    def set_legend(self, value):
        self.__legend = value


    def get_extra(self):
        return self.__extra if self.__extra else ""

    def get_description(self):
        return self.__description if self.__description else ""

    def set_extra(self, value):
        self.__extra = value

    def get_section(self):
        return config_basic.get_section_prefix() + (self.__section if self.__section else "")

    def get_category(self):
        return self.__category if self.__category else ""
    
    def __str__(self, *args, **kwargs):
        return "GraphDescriptionImpl(%s)" % (self.get_full_description(), )

    def get_full_description(self):
        return self.__description + \
                (" %s" % self.__extra if self.__extra else "") + \
                (" (%s)" % self.__category if self.__category else "") + \
                (" (%s)" % self.__legend if self.__legend else "")

    def set_section(self, value):
        self.__section = value

    def set_category(self, value):
        self.__category = value

    def set_description(self, value):
        self.__description = value

    def set_basename(self, value):
        self.__basename = value

    def get_filename(self):
        if self.__basename:
            (dirname, filename) = os.path.split(self.__basename)
            return os.path.join(dirname, "-".join(ifilter(None, (self.get_section(), filename, self.get_category()))))
        else:
            return None

    section = property(get_section, set_section, None, None)
    category = property(get_category, set_category, None, None)
    description = property(get_description, set_description, None, None)
    basename = property(None, set_basename, None, None)
    extra = property(get_extra, set_extra, None, None)
    legend = property(get_legend, set_legend, None, None)

config_dependency_filter_class = DependencyFilter
config_module_list = ModuleListSupply()

class DependencyFilterHelper(ConfigDependent):
    @staticmethod
    def filter_graph(graph, dependency_filter_configuration=None, dependency_filter=None):
        assert isinstance(graph, BasicGraph)
        if dependency_filter == None:
            assert isinstance(dependency_filter_configuration, DependencyFilterConfiguration)
            dependency_filter = config_dependency_filter_class(config=dependency_filter_configuration, 
                                                               module_list=config_module_list.get_module_list())
        for edge in graph.edges():
            dependency_filter.dependency(edge.get_from_node(), edge.get_to_node())
        dependency_filter.postamble()
        return dependency_filter.graph()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
