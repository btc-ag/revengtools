#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@summary: Dependency parser for Microsoft Visual C++ 9 Solution Files 
    implementing base.dependency.dependency_if_deprecated.DependencyParser.
'''

from base.dependency.dependency_if_deprecated import DependencyParser
from cpp.cpp_if import CppPaths
from cpp.msvc.parse_sln_internal import InternalSolutionFileParser

config_cpp_paths = CppPaths

# TODO die SLN-Dependencies ergänzen um die #pragma-Link-Dependencies

class LinkDependencyParser(DependencyParser):
    def __init__(self, cpp_paths = None):
        if cpp_paths == None:
            cpp_paths = config_cpp_paths()
        self.__cpp_paths = cpp_paths
        self.__internal = None
        
    def process(self):
        self.__internal = InternalSolutionFileParser(open(self.__cpp_paths.get_solution_file(), "r"))

    def output(self, outputter):
        #project_name_to_id = dict([(project_name,project_id) 
        #                    for (project_id,project_name) in self.__project_ids_to_name.iteritems()])
        for (source, target) in self.__internal.get_dependencies_iter():
            outputter.dependency(source, target)
        outputter.postamble()
        
    def vcprojs(self):
        return self.__internal.vcprojs()
        
    
# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
