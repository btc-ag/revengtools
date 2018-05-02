'''
Created on 13.10.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.core_if import EnumerationItem, Enumeration

class DependencyTime(EnumerationItem):
    pass
    
class DependencyTimes(Enumeration):
    # DESIGN_TIME = DependencyTime()
    COMPILE_TIME = DependencyTime()
    LINK_TIME = DependencyTime()
    DEPLOY_TIME = DependencyTime()
    RUN_TIME = DependencyTime()
    
class DependencyLevel(EnumerationItem):
    pass

class DependencyLevels(Enumeration):
    # SUBSYSTEM_LEVEL = DependencyLevel()
    MODULE_LEVEL = DependencyLevel()
    PHYSICAL_UNIT_LEVEL = DependencyLevel() # e.g. files
    LOGICAL_UNIT_LEVEL = DependencyLevel() # e.g. classes
    CALLABLE_LEVEL = DependencyLevel() # e.g. functions, methods 
    FINEST_LEVEL = DependencyLevel() # e.g. complete AST
    
class DependencyGraphSpecification(object):
    def __init__(self, 
                 name=None, 
                 time=None, 
                 level=None, 
                 granularity=None,
                 regenerate=False, 
                 *args, **kwargs):
        self.__name = name
        self.__time = time
        self.__level = level
        self.__granularity = granularity
        self.__regenerate = regenerate
        self.__additional = kwargs

class DependencyGraphGenerator(AutoConfigurable):
    def specification(self):
        """
        @rtype: DependencyGraphSpecification
        """
        raise NotImplementedError(self.__class__)
    
    def retrieve_graph(self):
        """
        @rtype: BasicGraph
        """
        raise NotImplementedError(self.__class__)
    
class DependencyGraphGeneratorFactory(AutoConfigurable):
    def get_dependency_graph_generators(self, specification, exact_match=False, max_count=None):
        """
        
        @param specification: A specification of the desired dependency graph generators.
        @type specification: DependencyGraphSpecification 
        @param exact_match: if exact_match is true, any graph generator returned must exactly 
            match the specification.
        @param max_count: None or a positive integer. If None, returns an arbitrary number of 
            generators, otherwise a maximum number of max_count. The DependencyGraphFactory may 
            choose to return more generators if max_count is set to a number than are returned
            if max_count is set to 0.        
        @rtype: a list of DependencyGraphGenerator objects, sorted in descending order of matching
            the specification.
        """
        raise NotImplementedError(self.__class__)
        