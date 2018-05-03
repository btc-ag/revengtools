#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.dependency.dependency_if import ModuleGrouper
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    SCCEdgeDecorator)
from base.dependency.dependency_util import GraphDescriptionImpl
from commons.config_if import ConfigDependent
from commons.configurator import Configurator
from commons.graph.output_if import NodeGroupingConfiguration, DecoratorSet
from commons.graph.output_util import NodeGroupDecorator
from cpp.cpp_if import FileToModuleMapSupply
from cpp.incl_deps.file_include_deps import (FileModuleIncludeDepsSupply, 
    FileIncludeDepsProcessor, ModuleIncludeLinkTargetDetailsDecorator)
from cpp.incl_deps.include_deps_if import FileIncludeDepsSupply
from cpp.incl_deps.include_link_lifter_if import IncludeLinkLifter
from cpp.incl_deps.include_link_lifter_output import ModuleLinksOutputter
import logging
import sys

config_include_link_lifter = IncludeLinkLifter
config_dependency_filter_outputter = DependencyFilterOutputter
config_file_include_deps_supply = FileIncludeDepsSupply()
config_file_to_module_map_supply = FileToModuleMapSupply()
config_module_grouper = ModuleGrouper
config_module_group_conf = NodeGroupingConfiguration

class LiftIncludeLinksRunner(ConfigDependent):
    def process(self, node_restriction_in):
        file_include_deps = config_file_include_deps_supply.get_file_include_deps()
            
        lifter = config_include_link_lifter(file_include_deps_supply=config_file_include_deps_supply,
                                            file_to_module_map_supply=config_file_to_module_map_supply,
                                            node_restriction_in=node_restriction_in)
        
        lifter.process(use_mapping_exceptions=True)
        fidp = FileIncludeDepsProcessor(file_include_deps=file_include_deps)
        decorator_config = DecoratorSet(edge_tooltip_decorators=(ModuleIncludeLinkTargetDetailsDecorator(fidp), ),
                                        node_tooltip_decorators=(NodeGroupDecorator(),),
                                        edge_label_decorators=(SCCEdgeDecorator(),),
                                        )
        description = GraphDescriptionImpl(description="module-level include dependencies", 
                                       basename=FileModuleIncludeDepsSupply().get_module_include_deps_basename() + "-impl-except", 
                                       extra="with external dependencies")
        ModuleLinksOutputter.output(module_links=lifter.get_module_links(),
                                    decorator_config=decorator_config,
                                    module_group_conf=config_module_group_conf(config_module_grouper()),
                                    description=description)    
        

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    Configurator().default()
    if len(sys.argv) < 2:
        node_restriction_in = None
    else:
        node_restriction_in = set(sys.argv[1].split(","))
    
    LiftIncludeLinksRunner().process(node_restriction_in)
    
if __name__ == "__main__":
    main()
