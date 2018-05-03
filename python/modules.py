# -*- coding: UTF-8 -*-

'''
Contains implementation of base.modules_if for Python repositories.

Created on 28.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.basic_config_base import BasicConfigBase
from base.dependency.dependency_base import BaseSuffixModuleGrouper
from base.modules_base import BaseModuleListSupply
from commons.os_util import FixedBaseDirPathResolver
from python.python_util import PythonTools
import os.path
import warnings

config_basic = BasicConfig()
#config_module_list_supply = ModuleListSupply()

class __MockBasicConfig(BasicConfigBase):
    def get_local_source_base_dir(self):
        return os.path.abspath(os.path.dirname(__file__))

class PythonModuleGrouper(BaseSuffixModuleGrouper):


    def is_external_module(self, module):
        """
        The modules returned by is_external_module will be clustered into one single node group.
        
        This does not affect dependency gathering for these modules currently. If these modules depend
        on other modules, these dependencies will be shown in the output graph.
        See python.depgraph2dot for modifying dependency gathering. 
        """
        # TODO so geht das nicht, wenn man Ausnahmen verwendet 
        #return config_module_list_supply.is_external_module(module)
        return module in ('csv', 'pymssql', 'datetime', 'imp', 'modulefinder',
                          # 'urllib2', 'mimetools', 'urlparse', 'thread', 'urllib', 'optparse', 'textwrap',
                          )

    def get_node_group_prefix(self, module):
        if self.is_external_module(module):
            return "<PYTHON>"
        else:
            return BaseSuffixModuleGrouper.get_node_group_prefix(self, module)
    
    def _determine_node_group_prefixes(self, nodes):
        prefixes = set()
        for module in nodes:
            package_name = PythonTools.get_package_name(module)
            if package_name != '':
                prefixes.add(package_name + ".")
        return prefixes

class PythonModuleListSupplyBase(BaseModuleListSupply):
    """
    >>> import sys
    >>> sys.modules["__main__"].config_basic = __MockBasicConfig
    >>> sys.modules["base.modules_base"].config_basic = __MockBasicConfig
    
    # TODO convert this into a real unit test, this needs an implementation of get_module_list
    #>>> PythonModuleListSupplyBase().get_module_size('python.modules') > 0
    #True

    >>> tuple(map(lambda str: str.replace('/', '\\\\'), PythonModuleListSupplyBase().get_files_for_module('python.modules')))
    ('python\\\\modules.py',)
    """

    def get_files_for_module(self, module):
        return (PythonTools.get_filename_for_module(module),)


class FromFilePythonModuleListSupply(PythonModuleListSupplyBase):
    def __init__(self, results_resolver=None, *args, **kwargs):
        PythonModuleListSupplyBase.__init__(self, *args, **kwargs)
        self.__module_list = None
        if not results_resolver:
            warnings.warn(DeprecationWarning, "results_path_resolver should be set")
            self.__results_resolver = FixedBaseDirPathResolver(config_basic.get_results_directory())
        else:
            self.__results_resolver = results_resolver

    def get_module_list(self):
        if self.__module_list == None:
            module_list_file = self.__results_resolver.resolve("python-modules").open(mode="r")
            self.__module_list = [PythonTools.get_module_for_filename(filename.strip()) 
                                  for filename in module_list_file]
        return self.__module_list
    
class OnTheFlyPythonModuleListSupply(PythonModuleListSupplyBase):
    def __init__(self, source_resolver=None, *args, **kwargs):
        PythonModuleListSupplyBase.__init__(self, *args, **kwargs)
        self.__module_list = None
        if not source_resolver:
            warnings.warn("results_path_resolver should be set", DeprecationWarning)
            self.__source_resolver = FixedBaseDirPathResolver(config_basic.get_local_source_base_dir())
        else:
            self.__source_resolver = source_resolver
        

    def get_module_list(self):
        if self.__module_list == None:
            olddir = os.getcwd()
            result = list()
            try:
                os.chdir(config_basic.get_local_source_base_dir())
                walk_res = os.walk('.')
                for (dirpath, _dirnames, filenames) in walk_res:
                    result.extend(PythonTools.get_module_for_filename(os.path.join(dirpath, filename)) 
                                   for filename in filenames 
                                   if filename.endswith('.py'))
            finally:
                os.chdir(olddir)
            self.__module_list = result
        return self.__module_list
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
