#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 20.09.2010
@author: SIGIESEC
'''
from commons.configurator import Configurator
from cpp.msvc.parse_link_dependencies import LinkDependencyParser
import logging
import sys

class ParseVcprojList(object):

    def process(self):
        self._parser = LinkDependencyParser()
        self._parser.process()        
        
        #vcproj_list_file = open(FileMSVCDataSupply().get_vcproj_list_filename(), "w")
        for vcproj in self._parser.vcprojs():
            print(vcproj)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr,level=logging.INFO)
    #logging.getLogger("commons.configurator").setLevel(logging.DEBUG)
    Configurator().default()
    ParseVcprojList().process()
