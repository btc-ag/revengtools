# -*- coding: UTF-8 -*-

'''
Created on 01.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import ModuleGrouper
from base.dependency.dependency_output_util import (DependencyFilterOutputter, 
    ModuleColorNodeDecorator, ScalingTypes, TerminalNodeDecorator)
from base.dependency.module.graph_util import (ModuleSizeLabelDecorator, 
    ModuleSizeScalingDecorator)
from commons.graph.output_base import BaseNodeGroupingConfiguration
from commons.graph.output_if import DecoratorSet
from epm.dependency_output import (EPMDependencyFilterConfiguration, 
    EPMNodeColorer, EPMInterfaceOnlyDependencyFilterConfiguration)
from python.modules import PythonModuleGrouper
from base.modules_if import ModuleListSupply

config_module_grouper = ModuleGrouper
config_module_list_supply = ModuleListSupply()

class RevEngToolsEPMDependencyOutputterConfiguration(EPMDependencyFilterConfiguration):
    #skip_module_types_as_source = \
    #    EPMDependencyFilterConfiguration.skip_module_types_as_source + \
    #        [PhysicalModuleTypes.Implementation]
    #focus_on_node_groups = ['epm']
    
    def _create_module_grouper(self, modules):
        return config_module_grouper(modules)
    
    def skip_module(self, module):
        return (module.endswith("__init__") and config_module_list_supply.get_module_size(module) == 0) or \
                module.startswith("site-packages") or \
            EPMDependencyFilterConfiguration.skip_module(self, module)

    def skip_module_as_source(self, source):
        return source.startswith("ClusterF") or \
            source.startswith("List") or \
            EPMDependencyFilterConfiguration.skip_module_as_source(self, source)
            
    def skip_module_as_target(self, target):
        return target.endswith("__init__") or \
            EPMDependencyFilterConfiguration.skip_module_as_target(self, target)
            
class RevEngToolsIfOnlyEPMDependencyOutputterConfiguration(EPMInterfaceOnlyDependencyFilterConfiguration, 
                                                           RevEngToolsEPMDependencyOutputterConfiguration):
    pass


# TODO automatische Trennung von Interface und Nicht-Interface
# TODO wieso kann ich kein "+" im ModulNamen verwenden??
class RevEngToolsCategoryModuleGrouper(PythonModuleGrouper):
    ########################################################
    # Parameters
    defined_module_group_prefixes = ['base',
                                     'commons',
                                     'systems',
                                     'technologies',
                                     'epm',
                                     'epm.technologies',
                                     'backends',
                                     'backends.technologies',
                                     'infrastructure.graph_layout',
                                     'infrastructure.databases',
                                     'infrastructure.scms',
                                     '<PYTHON>'
                                    ]
    
    replace_at_start = dict({'cpp.idep.': 'backends.technologies.cpp-idep.', 
                             'cpp.': 'technologies.cpp.', 
                             'python.': 'technologies.python.', 
                             'epm.python.': 'epm.technologies.python.',
                             'epm.cpp.': 'epm.technologies.cpp.',
                             'clustering.': 'base.clustering.'})
    
    ########################################################

    def get_node_group_prefix(self, module):
        """
        >>> RevEngToolsCategoryModuleGrouper(None).get_node_group_prefix("cpp.bla")
        'technologies'
        >>> RevEngToolsCategoryModuleGrouper(None).get_node_group_prefix("base.dependencies")
        'base'
        """
        for (prefix, new_prefix) in self.replace_at_start.iteritems():
            if module.startswith(prefix):
                # TODO achtung, eigentlich nur am Anfang ersetzen
                module = module.replace(prefix, new_prefix)
                break
        #if module in self.module_group_exceptions:
        #    return self.module_group_exceptions[module]
        #else:
        return PythonModuleGrouper.get_node_group_prefix(self, module)

    def _determine_node_group_prefixes(self, nodes):
        #EPMDependencyFilterConfiguration.module_group_prefixes(self, modules)
        return sorted(self.defined_module_group_prefixes, key=lambda x: -len(x))

    # TODO auch hide_module_group

class RevEngToolsModuleGrouper(PythonModuleGrouper):
    pass

class RevEngToolsModuleGroupingConfiguration(BaseNodeGroupingConfiguration):

    def __init__(self, module_grouper=None, *args, **kwargs):
        if module_grouper == None:
            module_grouper = config_module_grouper()
        BaseNodeGroupingConfiguration.__init__(self, node_grouper=module_grouper, *args, **kwargs)

    collapse_all_module_groups = True
    collapse_module_groups = []

#    collapse_module_groups = ['clustering',
#                              #'commons', 
#                              'python',
#                              'cpp',
#                              'cpp.msvc',
#                              #'base',
#                              ]
    
    def collapse_node_group(self, module_group_prefix):
        return self.collapse_all_module_groups or \
            module_group_prefix  in self.collapse_module_groups
        #return module_group_prefix != None and module_group_prefix != ''

class ModuleDependencyFilterOutputter(DependencyFilterOutputter):
    def __init__(self, decorator_config=None, *args, **kwargs):
        if decorator_config == None:
            decorator_config = DecoratorSet()
        decorator_config.add_node_label_decorators \
            ([
              ModuleSizeLabelDecorator(), 
              ModuleSizeScalingDecorator(2, 7, ScalingTypes.RADICAL),
              ModuleColorNodeDecorator(EPMNodeColorer()),
              TerminalNodeDecorator(),
              ])
        DependencyFilterOutputter.__init__(self,
                                           decorator_config=decorator_config, 
                                           *args, **kwargs)
        


if __name__ == "__main__":
    import doctest
    doctest.testmod()
