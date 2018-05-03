#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from commons.configurator import Configurator
from cpp.cpp_if import VirtualModuleTypes
from cpp.header_linker_if import BaseOutput, HeaderLinker
from cpp.incl_deps.file_include_deps import IncludeLinksHeaderListSupply
import logging
import sys
    
class ProcessableOutput(BaseOutput):
    def __init__(self, separate_inc):
        self.__separate_inc = separate_inc

    def add_module_map(self, module, header):
        if module != None:
            # TODO ensure that header is posixpath. alt: "inc" in PathTools.splitall(header)
            if header.find('/inc/') != -1 and self.__separate_inc:
                print("%s%s,%s" % (module, VirtualModuleTypes.HeaderModule.suffix(), header))
            else:
                print("%s%s,%s" % (module, VirtualModuleTypes.DeclarationModule.suffix(), header))
                
    def write(self):
        pass
                
class ReadableOutput(BaseOutput):
    def __init__(self):
        self.__module_map = dict()

    def add_module_map(self, module, header):
        if module in self.__module_map:
            self.__module_map[module].add(header)
        else:
            self.__module_map[module] = set([header])
        
    def write(self):
        for module in sorted(self.__module_map.iterkeys()):
            print("module %s" % module)
            print("\n".join(sorted(self.__module_map[module])))
            print("")

config_header_linker = HeaderLinker

def main():        
    logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
    Configurator().default()
        
    header_list = IncludeLinksHeaderListSupply().get_header_list()
    config_header_linker(outputter = ProcessableOutput(separate_inc=0)).link_all_headers(header_list)
    #logging.basicConfig(stream=sys.stdout,level=logging.DEBUG)    
    #config_header_linker(outputter = ReadableOutput()).link_all_headers()

if __name__ == "__main__":
    main()
