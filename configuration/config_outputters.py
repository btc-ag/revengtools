'''
Created on 04.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_output_html import (
    HTMLDocumentTextGraphOutputter, HTMLDocumentTextGraphOutputterFactory)
from base.dependency.dependency_output_util import OutputterConfiguration
from commons.config_if import ObjectFactory, ConfigDependent
from commons.graph.output_base import (TextGraphOutputter, 
    TextGraphOutputterFactory)
from commons.graph.output_if import (GraphicalGraphOutputter, 
    GraphicalGraphOutputterFactory)
from infrastructure.graph_layout.graphviz.graphviz import (
    GraphvizRenderingGraphOutputter, GraphvizGraphOutputter, 
    GraphvizGraphOutputterFactory, GraphvizRenderingGraphOutputterFactory)
from infrastructure.graph_layout.graphviz.graphviz_config import (
    GraphvizConfiguration)
import os

config_graphical_outputter_factory = GraphicalGraphOutputterFactory()
config_graphviz = GraphvizConfiguration()

class CurrentOutputterConfiguration(OutputterConfiguration, ConfigDependent):
    def __init__(self, object_factory=ObjectFactory()):
        self.__object_factory = object_factory     
    
    def outputters(self):
        # TODO this is not too nice... a warning should be given if graphviz is not found
        if os.name == 'nt':
            EXECUTABLE_EXTENSION = '.exe'
        else:
            EXECUTABLE_EXTENSION = ''
        if os.path.exists(os.path.join(config_graphviz.get_graphviz_bin_dir(), "dot" + EXECUTABLE_EXTENSION)):
            outputters = (self.__object_factory.create_instance(xxclsxx=GraphvizRenderingGraphOutputterFactory), 
                          self.__object_factory.create_instance(xxclsxx=TextGraphOutputterFactory), 
                          self.__object_factory.create_instance(xxclsxx=HTMLDocumentTextGraphOutputterFactory)
                          )
        else: 
            outputters = (self.__object_factory.create_instance(xxclsxx=GraphvizGraphOutputterFactory), 
                          self.__object_factory.create_instance(xxclsxx=TextGraphOutputterFactory), 
                          self.__object_factory.create_instance(xxclsxx=HTMLDocumentTextGraphOutputterFactory)
                          )
        return outputters
        
class DefaultOutputterConfiguration(OutputterConfiguration):    
    def __init__(self, object_factory=ObjectFactory()):
        self.__object_factory = object_factory 

    def outputters(self):
        outputters = (config_graphical_outputter_factory, 
                      self.__object_factory.create_instance(xxclsxx=TextGraphOutputterFactory), 
                      self.__object_factory.create_instance(xxclsxx=HTMLDocumentTextGraphOutputterFactory),
                      )
        return outputters
