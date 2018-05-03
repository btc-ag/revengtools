# -*- coding: UTF-8 -*-
'''
Created on 26.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import ModuleGrouper
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    DependencyFilterOutputterTools)
from base.dependency.dependency_util import GraphDescriptionImpl
from base.dependency.generation_log_if import GenerationLogGenerator
from commons.config_if import ConfigDependent
from commons.graph.output_base import DecoratingTextGraphOutputter,\
    DecoratingTextGraphOutputterFactory
from commons.graph.output_default import DefaultNodeGroupingConfiguration
from commons.graph.output_if import DecoratorSet, NodeGroupingConfiguration
from cpp.cpp_if import FileToModuleMapSupply
from cpp.incl_deps.file_include_deps import (FileIncludeDepsProcessor, 
    ModuleIncludeLinkDetailsDecorator, FileModuleIncludeDepsSupply)
from textwrap import TextWrapper

class ConsistencyCheckerOutputConstants(object):
    DESCRIPTION_STRING = "module-level include-/link-deps"
    
class DocumentFormatter(object):
    # TODO Das ist nur eine Übergangslösung, komplizierter sollte die nicht werden.
    # Falls etwas komplexeres nötig ist, XSL-FO bzw. Docbook verwenden.
    
    def format_paragraph(self, paragraph):
        raise NotImplementedError(self.__class__)
    
    def format_enumeration(self, enumerated_paragraphs):
        raise NotImplementedError(self.__class__)
    
class HTMLDocumentFormatter(DocumentFormatter):
    pass

class TextDocumentFormatter(DocumentFormatter):
    def __init__(self, width=80):
        self.__wrapper = TextWrapper(width=width)

    def format_paragraph(self, paragraph):
        return self.__wrapper.fill(paragraph)

    def format_enumeration(self, enumerated_paragraphs):
        filled_text = ""
        self.__wrapper.subsequent_indent = "     "
        for (itemno, text) in enumerate(enumerated_paragraphs, 1):
            self.__wrapper.initial_indent = "  %d) " % (itemno, )
            filled_text += self.__wrapper.fill(text) + "\n"
            
        self.__wrapper.subsequent_indent = ""
        self.__wrapper.initial_indent = ""
        return filled_text

class ConsistencyCheckerReportOutputter(ConfigDependent):
    def __init__(self, file_to_module_map_supply, module_grouper, report_filename,
                 generation_log = GenerationLogGenerator(),
                 dependency_filter_outputter = DependencyFilterOutputter,
                 text_graph_outputter_factory=DecoratingTextGraphOutputterFactory(),
                ):
        self.__file_include_deps_printer = FileIncludeDepsProcessor(file_to_module_map_supply=file_to_module_map_supply)
        self.__module_grouper = module_grouper
        self.__report_file = open(report_filename, "wt")
        self.__report_filename = report_filename
        self.__formatter = TextDocumentFormatter()
        self.__dependency_filter_outputter = dependency_filter_outputter
        self.__text_graph_outputter_factory = text_graph_outputter_factory
        self.__generation_log = generation_log

    def _print_missing_link_deps_explanation(self):
        print >>self.__report_file, self.__formatter.format_paragraph("Missing link dependencies [module A includes header from module B but does not link with module B]:")
        print >>self.__report_file, self.__formatter.format_paragraph("Note: The build may be successful in spite of that for several reasons, including")
        
        enumerated_paragraphs = ["No definitions from the header are used at all -> Remove the include statement", 
            "No symbols that require link binding are used -> Add the link dependency to B for consistency", 
            "A symbol that requires link binding is reexported by a module C that A links with "
            "-> Add the link dependency to B, and check whether the link binding to C can be "
            "removed (see list below)", 
            "A is a static library that does not specify implied link dependencies for its users"]
        print >>self.__report_file, self.__formatter.format_enumeration(enumerated_paragraphs)

    def __print_missing_link_deps(self, missing_link_deps_graph):
        self._print_missing_link_deps_explanation()
        decorator_config = DecoratorSet(edge_label_decorators=[ModuleIncludeLinkDetailsDecorator(self.__file_include_deps_printer)])
        filter_outputter = self.__dependency_filter_outputter(decorator_config)
        filter_outputter.output_graph(graph=missing_link_deps_graph,
                                node_group_conf=DefaultNodeGroupingConfiguration(self.__module_grouper),
                                outfile=self.__report_file,
                                graph_outputter_factory=self.__text_graph_outputter_factory)

    def _print_irregular_link_deps_explanation(self):
        print >>self.__report_file, self.__formatter.format_paragraph("Irregular link dependencies [module A links with module B but does not use any header from module B]:")
        print >>self.__report_file, self.__formatter.format_paragraph("Note: These may be required for a successful build for several reasons, including")

        enumerated_paragraphs = ["A uses a static library which depends on B -> avoid using static libraries in the debug build",
                                 "A relies on template specializations that are instantiated in B -> OK, but B should not contain anything else"]
        print >>self.__report_file, self.__formatter.format_enumeration(enumerated_paragraphs)

    def __print_irregular_link_deps(self, irregular_link_deps_graph):
        self._print_irregular_link_deps_explanation()
        filter_outputter = self.__dependency_filter_outputter()
        filter_outputter.output_graph(graph=irregular_link_deps_graph,
                                node_group_conf=DefaultNodeGroupingConfiguration(self.__module_grouper),
                                outfile=self.__report_file,
                                graph_outputter_factory=self.__text_graph_outputter_factory)

    def print_all(self, missing_link_deps_graph, irregular_link_deps_graph):
        self.__print_missing_link_deps(missing_link_deps_graph)
        print >>self.__report_file, ""
        self.__print_irregular_link_deps(irregular_link_deps_graph)
        description = GraphDescriptionImpl(description=ConsistencyCheckerOutputConstants.DESCRIPTION_STRING,
                                       category="report")
        self.__generation_log.add_generated_file(description=description,
                                                 filename=self.__report_filename)


class ConsistencyCheckerGraphOutputter(ConfigDependent):

    def __init__(self, file_to_module_map_supply, module_grouper,
                 node_group_conf = NodeGroupingConfiguration,
                 dependency_filter_outputter = DependencyFilterOutputter,
                 ):
        assert isinstance(file_to_module_map_supply, FileToModuleMapSupply)
        assert isinstance(module_grouper, ModuleGrouper)
        #self.__file_to_module_map_supply = file_to_module_map_supply
        self.__file_include_deps_printer = FileIncludeDepsProcessor(file_to_module_map_supply=file_to_module_map_supply)
        self.__module_grouper = module_grouper
        self.__dependency_filter_outputter = dependency_filter_outputter
        self.__node_group_conf = node_group_conf


    def output_combined_graph(self, show_combined_graph, multigraph, overview_multigraph):
        output_basename = FileModuleIncludeDepsSupply().get_module_include_deps_basename() \
            + "-consistency"
        decorator_config = DecoratorSet(edge_tooltip_decorators=[ModuleIncludeLinkDetailsDecorator(self.__file_include_deps_printer)])

        description = GraphDescriptionImpl(description=ConsistencyCheckerOutputConstants.DESCRIPTION_STRING,
                                       basename=output_basename,
                                       legend="red=missing, blue=irregular link deps")
        DependencyFilterOutputterTools.output_detail_and_overview_graph \
                (graph=multigraph,
                 overview_graph=overview_multigraph,
                 module_group_conf=self.__node_group_conf(self.__module_grouper),
                 outputter=self.__dependency_filter_outputter(decorator_config),
                 description=description)

#        config_graphical_graph_outputter.render_file(description=description,
#                                                     show=show_combined_graph
#                                                     )
