#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 25.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.configurator import Configurator
from commons.core_util import CollectionTools, SetValuedDictTools
from cpp.cpp_if import CppPaths
from cpp.msvc.msvc_supply_if import MSVCDataSupply
import logging
import os.path
import sys

config_basic = BasicConfig()
config_msvc_data_supply = MSVCDataSupply
config_cpp_paths = CppPaths()

class VcprojToModuleNameMapper(object): 
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__vcproj_to_module_map = CollectionTools.transpose_items_as_dict(config_msvc_data_supply().get_module_to_vcproj_map())
    
    def get_module_name(self, vcproj):
        if vcproj not in self.__vcproj_to_module_map:
            if vcproj.endswith(".csproj"):
                self.__logger.info("C# project %s currently not supported" % (vcproj, ))
            else:
                self.__logger.warning("Unknown vcproj %s" % (vcproj, ))
            return None
        else: 
            return self.__vcproj_to_module_map[vcproj]

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.INFO)
    Configurator().default()

    vcproj_lines = config_msvc_data_supply().get_vcproj_list()    
    dirs_to_vcprojs_map = SetValuedDictTools.convert_from_itemiterator((os.path.dirname(line[0]), line[0]) for line in vcproj_lines)
    os.chdir(config_cpp_paths.get_module_spec_basedir())
    mapper = VcprojToModuleNameMapper()
    for (dirname, vcprojs) in sorted(dirs_to_vcprojs_map.iteritems()):
        if dirname == '':
            # this is an entry containing solution folders, not projects # TODO this should be filtered somewhere else 
            continue
        if len(vcprojs) == 1:
            top_vcproj = vcprojs.pop()
        else:
            top_vcproj = max(vcprojs, key=lambda name: os.stat(name).st_size)
            
        # TODO this has not the correct case... better: extract module name from vcproj file
        # das ist doch schon gefixed, oder nicht??
        if len(dirname):
            print "%s:%s" % (dirname, mapper.get_module_name(top_vcproj))

if __name__ == "__main__":
    main()
