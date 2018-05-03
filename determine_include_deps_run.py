#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 22.09.2010

@author: SIGIESEC
'''
from commons.configurator import Configurator
from cpp.incl_deps.include_deps_if import IncludeDependencyGenerator
import logging
import sys
#import pydevd

config_include_deps_generator = IncludeDependencyGenerator

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.INFO)
    #pydevd.settrace()
    Configurator().default()

    config_include_deps_generator().generate()

if __name__ == "__main__":
    main()
