'''
Implementation of C{base.dependency.module.linkdeps_if.ModuleLinkDepsSupply} which
uses a previously created CSV file containing the link dependencies.

Created on 27.09.2010

@author: SIGIESEC
'''
from base.dependency.module.linkdeps_if import ModuleLinkDepsSupply
from base.generic_files_util import GenericFilesTools
from commons.config_if import ConfigDependent
from commons.graph.attrgraph_util import AttributedEdge, AttributeGraph
from commons.os_util import FileTools
import logging

class FileModuleLinkDepsSupply(ModuleLinkDepsSupply, ConfigDependent):
    def __init__(self, generic_files_tools=GenericFilesTools):
        self.__module_link_deps_graph = None
        self.__generic_files_tools = generic_files_tools()
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def __get_module_link_deps(self):
        # TODO warn if the file is outdated, i.e. if there is a module whose
        # module specification file is newer than the link deps file
        filename = self.__generic_files_tools.get_module_link_deps_csv_filename()
        return FileTools.create_csv_reader(filename=filename,
                                           what="module link deps", 
                                           delimiter=',')

    def get_module_link_deps_graph(self):
        if self.__module_link_deps_graph == None:
            self.__module_link_deps_graph = AttributeGraph(
                                       edges=[AttributedEdge(from_node=f, to_node=t) 
                                              for (f,t) in self.__get_module_link_deps()])
        return self.__module_link_deps_graph.immutable()
    