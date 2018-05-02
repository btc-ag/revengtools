# -*- coding: UTF-8 -*-
'''
Created on 29.10.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.dependency.dependency_table import DecoratedGraphTableModel
from commons.config_if import ObjectFactory
from commons.document.renderers.html import HTMLTableWriter, HTMLHelper
from commons.graph.output_base import BaseGraphOutputter
from commons.graph.output_if import (TextualGraphOutputter, GraphOutputter, 
    TextualGraphOutputterFactory)
from commons.os_util import PathTools
from commons.scm_default import FallbackVersionDescriber
from commons.scm_if import VersionDescriber
from commons.v26compat_util import compatrelpath
from datetime import datetime
import os

config_basic = BasicConfig()
config_version_describer = VersionDescriber()

class HTMLTableTextGraphOutputter(GraphOutputter):
    def __init__(self, output_groups, graph, outfile,
                 node_grouper,
                 decorator_config,
                 description=None,
                 table_model_class=DecoratedGraphTableModel,
                 *args, **kwargs):
        self.__description = description
        self.__outfile = outfile
        self.__graph = graph
        self.__decorator_config = decorator_config
        self.__table_model_class = table_model_class

    @staticmethod
    def usual_extension():
        return None

    def description(self):
        return self.__description.get_full_description()

    def output_all(self):
        table_model = self.__table_model_class(graph=self.__graph,
                                               decorator_config=self.__decorator_config)
        HTMLTableWriter(output_file=self.__outfile,
                        table_model=table_model,
                        sep=HTMLTableWriter.VERTICAL_SEP).write_table(sortable=True)

class HTMLDocumentTextGraphOutputterFactory(TextualGraphOutputterFactory):
    def __init__(self, object_factory=ObjectFactory()):
        self.__object_factory = object_factory 

    def usual_extension(self):
        return HTMLDocumentTextGraphOutputter.usual_extension()

    def get_name(self):
        return HTMLDocumentTextGraphOutputter.__name__

    def create_instance(self, *args, **kwargs):
        return self.__object_factory.create_instance(xxclsxx=HTMLDocumentTextGraphOutputter, *args, **kwargs)

class HTMLDocumentTextGraphOutputter(BaseGraphOutputter, TextualGraphOutputter):
    def __init__(self, graph, outfile,
                decorator_config,
                 description=None,
                 *args, **kwargs):
        BaseGraphOutputter.__init__(self,
                                    graph=graph,
                                    outfile=outfile,
                                    decorator_config=decorator_config,
                                    description=description,
                                    *args, **kwargs)
        self.__table_output = HTMLTableTextGraphOutputter(graph=graph,
                                                          outfile=outfile,
                                                          decorator_config=decorator_config,
                                                          description=description,
                                                          *args, **kwargs)

    @staticmethod
    def usual_extension():
        return '.html'

    def output_all(self):
        stylesheet_path = PathTools.native_to_posix(
                                        os.path.join(compatrelpath(config_basic.get_results_directory(),
                                                                     os.path.dirname(self.file().name)),
                                       'styles.css'))
        print >>self.file(), HTMLHelper.get_html_head(title=self.description(),
                                 charset='iso-8859-1',
                                 stylesheet=stylesheet_path,
                                 )
        print >>self.file(), HTMLHelper.get_preamble()
        print >>self.file(), """
        <h1>BTC RevEngTools Results: %s</h1>
        <h2>System: %s, Version: %s, Repository revision: %s</h2>
        <h2>Analysis time: %s</h2>
        
        """ % (self.description(),
               # TODO hierfür sollten die Graph Decorator verwendet werden
               config_basic.get_system(), config_basic.get_version(),
               FallbackVersionDescriber(config_version_describer).describe_local_version(config_basic.get_local_source_base_dir(), False)[2],
               datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.__table_output.output_all()
        print >>self.file(), HTMLHelper.get_postamble()
        print >>self.file(), HTMLHelper.get_html_tail()
