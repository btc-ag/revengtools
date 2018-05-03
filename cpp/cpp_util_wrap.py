'''
Created on 25.02.2012

@author: SIGIESEC
'''
from cpp.cpp_util import IncludePathMappingFactory
from base.basic_config_if import BasicConfig

config_basic = BasicConfig()

def get_default_include_path_mapping():
    return IncludePathMappingFactory(basic_config=config_basic).create()
