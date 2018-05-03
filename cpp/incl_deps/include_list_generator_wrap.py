'''
Created on 17.02.2012

@author: SIGIESEC
'''
from base.serverpath_if import ServerPath
from commons.config_if import ConfigDependent
from commons.os_util import PathTools
from cpp.incl_deps.include_list_generator import (HeaderExceptionMapper, 
    HeaderCanonicalSorter, HeaderPathMapper, IncludeListGeneratorInternal)
from cpp.incl_deps.include_rule_checker_if import IncludeRuleChecker

config_header_exception_mapper = HeaderExceptionMapper()
config_header_canonical_sorter = HeaderCanonicalSorter()
config_include_rule_checker = IncludeRuleChecker()
config_header_path_mapper = HeaderPathMapper()

class IncludeListGenerator(ConfigDependent):
    def __init__(self, include_guard_normalizer, config):
        self.__decoratee = IncludeListGeneratorInternal(include_guard_normalizer=include_guard_normalizer, 
                                                        config=config,
                                                        include_rule_checker = config_include_rule_checker,
                                                        header_canonical_sorter=config_header_canonical_sorter,
                                                        header_exception_mapper=config_header_exception_mapper,
                                                        header_path_mapper=config_header_path_mapper,
                                                        )
        
    def generate_include_directives(self, repair_path, include_paths):
        return self.__decoratee.generate_include_directives(repair_path, include_paths)

# shorter/more efficient: 
#def IncludeListGenerator(include_guard_normalizer, config):
#    return IncludeListGeneratorInternal(include_guard_normalizer=include_guard_normalizer, 
#                                        config=config,
#                                        include_rule_checker = config_include_rule_checker,
#                                        header_canonical_sorter=config_header_canonical_sorter,
#                                        header_exception_mapper=config_header_exception_mapper,
#                                        header_path_mapper=config_header_path_mapper,
#                                        )

config_path_tools = ServerPath

class DefaultHeaderPathMapper(HeaderPathMapper, ConfigDependent):
    def __init__(self):
        HeaderPathMapper.__init__(self)

    def server_to_rel_to_root_path(self, server_path):
        return PathTools.unix_normpath(config_path_tools.server_to_relative_path(server_path))
