"""
Integration test tool to test whether a simple graph can be output with 
a given configuration (CONFIG variable).
If this fails, then more complex operations such as process_hudson.sh 
will most certainly also fail.

Created on 21.08.2012

@author: SIGIESEC
"""
from base.dependency.dependency_base import NullModuleGrouper
from base.dependency.dependency_if import ModuleGrouper
from base.dependency.dependency_output_util import (
    DependencyFilterOutputterTools, DependencyFilterOutputter)
from base.dependency.dependency_util import GraphDescriptionImpl
from commons.configurator import Configurator
from commons.graph.attrgraph_util import MutableAttributeGraph
from commons.graph.output_if import NodeGroupingConfiguration
import logging
import sys
from base.basic_config_if import BasicConfig

config_dependency_filter_outputter = DependencyFilterOutputter
config_module_group_conf = NodeGroupingConfiguration
config_module_grouper = ModuleGrouper
config_basic_config = BasicConfig()

class GraphGenerationProbe(object):
    
    def __init__(self, *args,**kwargs):
        self.__logger  = logging.getLogger(self.__class__.__module__)

    def __test(self):
        description = GraphDescriptionImpl(description="Test",
                                       basename="test",
                                       section="test")
        graph = MutableAttributeGraph()
        graph.add_edge_and_nodes("a", "b")
        module_group_conf = config_module_group_conf(module_grouper=config_module_grouper())
        DependencyFilterOutputterTools.output_detail_and_overview_graph(graph=graph,
                                                                        module_group_conf=module_group_conf,
                                                                        outputter=config_dependency_filter_outputter(),
                                                                        description=description)    
    
    def do_test(self):
        print "Trying to generate a graph using configuration for system %s ... " % (config_basic_config.get_system(), )
        try:
            self.__test()
            print "OK"
            return 0
        except:
            self.__logger.error("Graph generation failed", exc_info=1)
            print "FAILED"        
            return 1

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Configurator().default()
    sys.exit(GraphGenerationProbe().do_test())
    
