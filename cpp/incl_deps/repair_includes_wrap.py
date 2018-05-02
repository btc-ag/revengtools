#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 20.12.2011

@author: SIGIESEC
'''
from commons.config_if import ConfigDependent
from cpp.incl_deps.repair_includes_base import (
    TwoPhaseRequiredIncludeFilesCalculator)
from cpp.incl_deps.repair_includes_if import (HeaderLister, UsedSymbolsLister, 
    RequiredIncludeFilesCalculator)

config_header_lister_class = HeaderLister
config_used_symbols_lister_class = UsedSymbolsLister

class TwoPhaseRequiredIncludeFilesCalculatorWrapper(ConfigDependent, RequiredIncludeFilesCalculator):
    def __init__(self, *args, **kwargs):
        self.__wrappee = TwoPhaseRequiredIncludeFilesCalculator(*args,                                                                                  
            used_symbols_lister=config_used_symbols_lister_class(), 
            header_lister=config_header_lister_class(), **kwargs)

    def calculate_required_include_files(self, *args, **kwargs):
        return self.__wrappee.calculate_required_include_files(*args, **kwargs)

