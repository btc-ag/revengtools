# -*- coding: UTF-8 -*-
'''
Created on 18.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_if import ModuleGrouper
from base.modules_if import ModuleListSupply
from commons.core_util import PrefixMapper, CollectionTools
from commons.graph.output_base import BaseNodeGroupingConfiguration
from epm.cabstyle.dependency_output import (CABStyleTopLevelModuleGrouperBase, 
    CABStyleFinestLevelModuleGrouperInternal)
from epm.cpp.mapper import CppPhysicalModuleDescriber
from epm.dependency_output import (EPMDependencyFilterConfiguration, 
    EPMInterfaceOnlyDependencyFilterConfiguration, 
    EPMWrapperOnlyDependencyFilterConfiguration, 
    EPMTestOnlyDependencyFilterConfiguration)
from epm.epm_physical_if import PhysicalModuleTypes
import itertools

config_module_list_supply = ModuleListSupply()

class CppCABPhysicalModuleDescriber(CppPhysicalModuleDescriber):
    physical_type_exceptions = \
        dict({'BTC.CAB.Commons.Core': (PhysicalModuleTypes.Framework,),
              'BTC.CAB.Commons.TypeTraits': (PhysicalModuleTypes.Framework,),
              'BTC.CAB.Commons.CoreExtras': (PhysicalModuleTypes.InterfaceUtility,),
              'BTC.CAB.Commons.Dom': (PhysicalModuleTypes.Framework,), # TODO: unsauber
              'BTC.CAB.Commons.Sax': (PhysicalModuleTypes.InterfaceUtility,),
              'BTC.CAB.Commons.RegEx': (PhysicalModuleTypes.Framework,),
              'BTC.CAB.Commons.Values': (PhysicalModuleTypes.Framework,),
              'BTC.CAB.RTB.DemoAppIEC61850': (PhysicalModuleTypes.Configurator,),
              'BtcDemoClient': (PhysicalModuleTypes.Configurator,),
              'BtcEMSCmdClient': (PhysicalModuleTypes.Configurator,),
              'BtcEEAInterface': (PhysicalModuleTypes.Interface,),
              'BTC.CAB.TimeSeries.EMSClient': (PhysicalModuleTypes.Configurator,),
              'BtcCimServiceModelProvider': (PhysicalModuleTypes.ImplementationWrapper, ),
              'BtcUnitTester': (PhysicalModuleTypes.Configurator, PhysicalModuleTypes.Implementation, ),
              'BTC.CAB.Database.SqlMinus': (PhysicalModuleTypes.Configurator, PhysicalModuleTypes.Implementation, ),
              'BTC.CAB.Depends.EXE': (PhysicalModuleTypes.Configurator, PhysicalModuleTypes.Implementation, ),                              
              'BTC.CAB.Encoding.SML.Dumper': (PhysicalModuleTypes.Configurator, PhysicalModuleTypes.Implementation,),
              'BTC.CAB.Controller.UnitTests': (PhysicalModuleTypes.ImplementationTest,),                              
              'BTC.CAB.Controller.UnitTestsInterface': (PhysicalModuleTypes.InterfaceTest,),
              'BTC.CAB.EMSServices.KomStub': (PhysicalModuleTypes.Implementation,),                              
              'BTC.CAB.EMSServices.KomDispatcher': (PhysicalModuleTypes.Implementation,),                              
              'ALL_BUILD': (),
              'ZERO_CHECK': (),
              'Z_BtcUtCommons': (),
              })

class CABDependencyOutputterConfiguration(EPMDependencyFilterConfiguration):
    
    #skip_module_types_as_source = \
    #    EPMDependencyFilterConfiguration.skip_module_types_as_source + \
    #        [PhysicalModuleTypes.Implementation]

    ########################################################
    # Parameters
    hide_modules_completely = ['ZERO_CHECK', 'ALL_BUILD',
                               # TODO why hide BTC.CAB.Commons.Crypto.Impl.External?
                               'BTC.CAB.Commons.Crypto.Impl.External',
                               'BTC.CAB.Commons.Core',
                               # the following are c# modules... 
                               'System', 'System.Core', 'System.Data', 'System.Xml', 'System.Xml.Linq'
                               ]
    #focus_on_node_groups = ['BtcRTB']
    ########################################################

    def skip_module(self, module):
        return module in self.hide_modules_completely \
            or module.startswith("_") \
            or module.startswith("Z_")
            # there are empty modules that may not be ignored, e.g. BTC.CAB.CIM.V12.Full.API
            # or (hasattr(config_module_list_supply, "is_module_empty") and config_module_list_supply.is_module_empty(module)) # MSVC-specific!

    #focus_on_node_groups = ['ProcessVariable', 'ProcessVariableEventTracer']

    def skip_module_as_target(self, target):
        return target == 'Logging' \
            or EPMDependencyFilterConfiguration.skip_module_as_target(self, target)
            
class CABTopLevelDependencyOutputterConfiguration(CABDependencyOutputterConfiguration):
    hide_modules_completely = ['ZERO_CHECK', 'ALL_BUILD']

    
    def get_skip_module_types_as_source(self):
        return []
                
      
# TODO Diese folgenden mehrfachvererbenden Klassen sollten nicht nötig sein...
class CABInterfaceOnlyDependencyOutputterConfiguration(EPMInterfaceOnlyDependencyFilterConfiguration, CABDependencyOutputterConfiguration):
    """
    >>> PhysicalModuleTypes.names(CABInterfaceOnlyDependencyOutputterConfiguration().get_skip_module_types_as_source())
    ...
    """
    pass      

class CABWrapperOnlyDependencyOutputterConfiguration(EPMWrapperOnlyDependencyFilterConfiguration, CABDependencyOutputterConfiguration):
    """
    >>> PhysicalModuleTypes.names(CABWrapperOnlyDependencyOutputterConfiguration().get_skip_module_types_as_source())
    ...
    """
    pass      

class CABTestOnlyDependencyOutputterConfiguration(EPMTestOnlyDependencyFilterConfiguration, CABDependencyOutputterConfiguration):
    """
    >>> PhysicalModuleTypes.names(CABTestOnlyDependencyOutputterConfiguration().get_skip_module_types_as_source())
    ...
    """
    pass


class CABFinestLevelModuleGrouper(ModuleGrouper):
    ########################################################
    # Parameters
    additional_module_group_prefixes = [
                                    # the following are external .NET modules
                                    "DevExpress",
                                    'OSIsoft',
                                    'Spring',
                                    'nunit',
                                    'System',
                                    'Common',
                                    'Microsoft',
                                    'Presentation',
                                    ]
    module_group_exceptions = \
        dict({'BTC.CAB.RTB.Driver.Base': 'BTC.CAB.RTB',
              'BTC.CAB.RTB.Driver.Mock': 'BTC.CAB.RTB',
              })
    ########################################################
    
    def __init__(self, modules, *args, **kwargs):
        self.__decoratee = CABStyleFinestLevelModuleGrouperInternal(modules=None, *args, **kwargs)
        self.__prefix_mapper = PrefixMapper(CollectionTools.identity_dict(self.additional_module_group_prefixes))
        if modules:
            self.configure_nodes(modules)
        
    @staticmethod
    def split_iter(iterator, pred):
        # TODO this is not optimal
        iter1, iter2 = itertools.tee(iterator, 2)
        return (itertools.ifilter(pred, iter1), itertools.ifilterfalse(pred, iter2))

    def configure_nodes(self, nodes):
        if nodes:
            additional_nodes, regular_nodes = self.split_iter(nodes, lambda node: node.startswith(tuple(self.additional_module_group_prefixes)))
            self.__decoratee.configure_nodes(regular_nodes)
            self.__active_prefixes = set(itertools.imap(self.__prefix_mapper.get_value, additional_nodes))
        else:
            self.__active_prefixes = ()
            self.__decoratee.configure_nodes(None)


    def get_node_group_prefix(self, module):
        result = self.__prefix_mapper.get_value(module)
        if not result:
            result = self.__decoratee.get_node_group_prefix(module)
        return result


    def node_group_prefixes(self):
        return itertools.chain(self.__decoratee.node_group_prefixes(), self.__active_prefixes)

        

class CABFinestLevelModuleGrouperService(CABFinestLevelModuleGrouper):
    def __init__(self, modules=None):
        CABFinestLevelModuleGrouper.__init__(self, 
                                             modules=modules,
                                             internal_modules=config_module_list_supply.get_module_list(),
                                             min_parts=3)    
    
class CABTopLevelModuleGrouper(CABStyleTopLevelModuleGrouperBase):
    OWN_PREFIX="BTC.CAB."
    ADDITIONAL_PREFIXES=()

class CABTopLevelModuleGrouperService(CABTopLevelModuleGrouper):
    def __init__(self, modules=None):
        CABTopLevelModuleGrouper.__init__(self, 
                                          modules=modules,
                                          internal_modules=config_module_list_supply.get_module_list())    


class CABModuleGroupingConfiguration(BaseNodeGroupingConfiguration):
    collapse_all_module_groups = True
    collapse_module_group_prefixes = [
                                      ]

    def __init__(self, module_grouper, *args, **kwargs):
        #if module_grouper == None:
        #    module_grouper = config_module_grouper()
        BaseNodeGroupingConfiguration.__init__(self, node_grouper=module_grouper, *args, **kwargs)


    def collapse_node_group(self, module_group_prefix):
        return self.collapse_all_module_groups or \
            module_group_prefix in self.collapse_module_group_prefixes
        #return module_group_prefix != None and module_group_prefix != ''

if __name__ == "__main__":
    import doctest
    doctest.testmod()
