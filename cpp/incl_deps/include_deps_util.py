'''
Created on 18.03.2011

@author: SIGIESEC
'''
from base.dependency.dependency_util import (AggregateMapper, 
    AggregateMapperGraphTools)
from commons.graph.graph_util import GraphAlgorithms
from cpp.incl_deps.file_include_deps import FileIncludeDepsProcessor
from itertools import chain

class FileLevelPseudoModuleDependencyGenerator(object):
    
    # TODO This class should be generalised such that it does not depend on CPP, include dependencies, 
    # or file-level. It just should aggregate dependencies according to some aggregation function.
    
    def __init__(self, file_to_module_map):
        self.__individual_to_input_aggregate_map = file_to_module_map    

    def get_file_level_pseudomodule_graph(self, modulenames, mapper, ignore_external=True, exceptions=set()):
        """
        @param mapper: 
        @type mapper: cpp.cpp_util.FileNameMapper
        """
        assert(isinstance(mapper, AggregateMapper))
        fidp = FileIncludeDepsProcessor(file_to_module_map=self.__individual_to_input_aggregate_map, 
                                        include_internal_links=True)
        file_graph = fidp.graph_for_from_module(modulenames)
        
        pseudomodule_graph = AggregateMapperGraphTools.aggregate_graph(mapper, 
                                                  ignore_external, 
                                                  exceptions, 
                                                  file_graph)
        return pseudomodule_graph
    
class FileIncludeDepsListerFacade(object):
    def __init__(self, include_deps_supply, closure, sort):
        """
        
        @param include_deps_supply: 
        @type include_deps_supply: FileIncludeDepsSupply
        @param closure: if True, consider transitive closure of dependencies, otherwise only direct dependencies
        @type closure: Boolean
        @param sort: if True, return output sorted by filenames
        @type sort: Boolean
        """
        self.__include_deps_supply = include_deps_supply        
        if closure:
            self.__transform_pre = GraphAlgorithms.transitive_closure
        else:
            self.__transform_pre = lambda x: x
        if sort:
            self.__transform_post = sorted
        else:
            self.__transform_post = lambda x: x
            
    def required_files(self, args):
        """
        Returns all files required by some base files.
        
        @param args: base file names (relative to project root)
        @type args: iterator of strings        
        @rtype: iterator of strings 
        """
        args_set = set(args)
        edge_list = self.__transform_pre(self.__include_deps_supply.get_file_include_deps())
        targets = chain((target for (source, target) in edge_list if source in args_set), args_set)
        return self.__transform_post(targets)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    