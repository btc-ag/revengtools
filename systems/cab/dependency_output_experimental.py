# -*- coding: UTF-8 -*-
'''
Created on 18.10.2010

@author: SIGIESEC
'''
from base.dependency.dependency_base import BaseSuffixModuleGrouper
from base.dependency.dependency_output_util import (DependencyFilterOutputter,
    FileRevisionNodeAndGraphDecorator, ScalingTypes, ModuleColorNodeDecorator,
    TerminalNodeDecorator)
from base.dependency.module.graph_util import (ModuleSizeLabelDecorator,
    ModuleWeightedDepsScalingDecorator)
from commons.graph.output_base import BaseNodeGroupingConfiguration
from commons.graph.output_if import DecoratorSet
from epm.cpp.mapper import CppPhysicalModuleDescriber
from epm.dependency_output import (EPMDependencyFilterConfiguration,
    EPMInterfaceOnlyDependencyFilterConfiguration, EPMNodeColorer,
    EPMWrapperOnlyDependencyFilterConfiguration)
from epm.epm_physical_if import PhysicalModuleTypes

class CABModuleDependencyFilterOutputter(DependencyFilterOutputter):

    def __init__(self, decorator_config=None, base_graph=None, *args, **kwargs):
        if decorator_config == None:
            decorator_config = DecoratorSet()
        decorator_config.add_graph_decorators([FileRevisionNodeAndGraphDecorator()])
        decorator_config.add_node_label_decorators \
            ([ModuleSizeLabelDecorator(),
              #ModuleSizeScalingDecorator(3, 8, ScalingTypes.RADICAL, is_prins_classic),
              ModuleWeightedDepsScalingDecorator(min_render_size=2,
                 max_render_size=12,
                 scale_type=ScalingTypes.RADICAL,
                 base_graph=base_graph),
              ModuleColorNodeDecorator(EPMNodeColorer()),
              TerminalNodeDecorator(),
              ])
        DependencyFilterOutputter.__init__(self,
                                           decorator_config=decorator_config,
                                           base_graph=base_graph,
                                           *args, **kwargs)

class CABPhysicalModuleDescriber(CppPhysicalModuleDescriber):
    physical_type_exceptions = \
        dict({'BtcCommonsCore': (PhysicalModuleTypes.InterfaceUtility,),
              'BtcCommonsCoreExtras': (PhysicalModuleTypes.InterfaceUtility,),
              'BtcCommonsDom': (PhysicalModuleTypes.InterfaceUtility,),
              'BtcCommonsSax': (PhysicalModuleTypes.InterfaceUtility,),
              'BTC.CAB.RTB.DemoAppIEC61850': (PhysicalModuleTypes.Configurator,),
              'BtcDemoClient': (PhysicalModuleTypes.Configurator,),
              'BtcEMSCmdClient': (PhysicalModuleTypes.Configurator,),
              'BtcEEAInterface': (PhysicalModuleTypes.Interface,),
              'BtcTimeSeriesEMSClient': (PhysicalModuleTypes.Configurator,),
              'BtcFieldBusModbusClient': (PhysicalModuleTypes.Configurator,),
              'BtcCimServiceModelProvider': (PhysicalModuleTypes.ImplementationWrapper, ),              
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
                               'BtcCommonsCore',
                               'BtcTestCppUnitTestRunner', 'BtcTestCppUnitStatic', 'BtcTestCppUnitShared',
                               'BTC.CAB.Commons.Crypto.Impl.External',
                               ]
    #focus_on_node_groups = ['BtcRTB']
    ########################################################

    def skip_module(self, module):
        return module in self.hide_modules_completely \
            or module.startswith("_") \
            or module.startswith("Z_")


    #focus_on_node_groups = ['ProcessVariable', 'ProcessVariableEventTracer']

    def skip_module_as_target(self, target):
        return target == 'Logging' \
            or EPMDependencyFilterConfiguration.skip_module_as_target(self, target)

class CABInterfaceOnlyDependencyOutputterConfiguration(EPMInterfaceOnlyDependencyFilterConfiguration, CABDependencyOutputterConfiguration):
    """
    >>> PhysicalModuleTypes.names(CABInterfaceOnlyDependencyOutputterConfiguration.skip_module_types_as_source)
    ...
    """
    pass

class CABWrapperOnlyDependencyOutputterConfiguration(EPMWrapperOnlyDependencyFilterConfiguration, CABDependencyOutputterConfiguration):
    """
    >>> PhysicalModuleTypes.names(CABInterfaceOnlyDependencyOutputterConfiguration.skip_module_types_as_source)
    ...
    """
    pass      


class CABModuleGrouper(BaseSuffixModuleGrouper):
    ########################################################
    # Parameters
    defined_module_group_prefixes = [
                                    'BtcCommons',
                                    'BtcCim',
                                    'BtcTimeSeries',
                                    'BtcModeling',
                                    'BtcEMS',
                                    'BtcController',
                                    'BTC.CAB.FieldBus',
                                    'BtcGraphics',
                                    'BtcMessaging',
                                    'BtcTimer',
                                    'BtcTest',
                                    'BtcYacl',
                                    'BtcSandbox',
                                    'BtcGui',
                                    'BtcDatabase',
                                    'BtcDataset',
                                    'BTC.CAB.AsyncCommunication',
                                    'BtcHTTP',
                                    'BtcUnitTest',
                                    'BtcEsb',
                                    'BtcYaclTimeService', # Ausnahme
                                    'BtcGid',
                                    'BtcCimController',
                                    'BtcEEA',
                                    'BtcCommonsCoreYacl',
                                    'BTC.CAB.RTB',
                                    'BTC.CAB.RTB.Driver',
                                    'BTC.CAB.Encoding',
                                    'BTC.CAB.RTB.Domains',
                                    'BTC.CAB.Commons.Crypto',
                                    'BTC.CAB.FieldBus.MMS',
                                    'BTC.CAB.FieldBus.IEC61850',                                                                        
                                    ]
    module_group_exceptions = \
        dict({'BtcUtCommons': 'BtcUnitTest',
              #'BtcMemoryDataset': 'BtcDataset',
              'BtcControllerCimAdapter': 'BtcCimController',
              'BtcEMSCmdClient': None,
              'BtcDispatcherFW': 'BtcEMS',
              'BTC.CAB.RTB.Driver.Base': 'BTC.CAB.RTB',
              'BTC.CAB.RTB.Driver.Mock': 'BTC.CAB.RTB',
              })
    ########################################################

    def get_node_group_prefix(self, module):
        if module in self.module_group_exceptions:
            return self.module_group_exceptions[module]
        else:
            return BaseSuffixModuleGrouper.get_node_group_prefix(self, module)

    def _determine_node_group_prefixes(self, nodes):
        #EPMDependencyFilterConfiguration.node_group_prefixes(self, modules)
        # TODO currently ignores nodes parameter...
        return sorted(self.defined_module_group_prefixes, key=lambda x:-len(x))

class CABModuleGroupingConfiguration(BaseNodeGroupingConfiguration):
    collapse_all_module_groups = True
    collapse_module_group_prefixes = [
                                      ]

    def __init__(self, module_grouper, *args, **kwargs):
        #if module_grouper == None:
        #    module_grouper = config_module_grouper()
        BaseNodeGroupingConfiguration.__init__(self, node_grouper=module_grouper, *args, **kwargs)

    def __str__(self):
        if self.collapse_all_module_groups:
            collapse_info = "collapse all"
        else:
            collapse_info = "collapse %s" % (self.collapse_module_group_prefixes,)
        return "<%s(%s)>" % (self.__class__.__name__, collapse_info)

    def collapse_node_group(self, module_group_prefix):
        return self.collapse_all_module_groups or \
            module_group_prefix in self.collapse_module_group_prefixes
        #return module_group_prefix != None and module_group_prefix != ''

if __name__ == "__main__":
    import doctest
    doctest.testmod()
