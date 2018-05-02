'''
An interface for a resource abstraction, which may be implemented for local files, and remote 
resources addressable via an URL or virtual named resources. 

Created on 26.05.2011

@author: SIGIESEC
'''

class IllegalResourceIdentifierError(ValueError):
    pass

class ResourceUnresolvable(ValueError):
    def __init__(self, candidates=()):
        self.__candidates = candidates

    def get_candidates(self):
        return iter(self.__candidates)
    
    def __str__(self):
        return "ResourceUnresolvable(candidates=%s)" % self.__candidates
    
class ResourceAccessError(ValueError):
    pass

class Resource(object):
    """
    An abstraction of a resource that can be opened as a stream and has an absolute name and possible a 
    relative base resource.
    
    Implementations of this interface must also implement __hash__ and __eq__.
    """
    
    def open(self, mode="r"):
        """
        @param mode: mode string as accepted by the builtin C{open}
        @raise ResourceAccessError: if the resource could not be opened with the specified mode
        @rtype: A file-like object
        """
        raise NotImplementedError(self.__class__)
        
    def stat(self):
        raise NotImplementedError(self.__class__)

    def name(self):
        raise NotImplementedError(self.__class__)
    
    def get_resolution_root(self):
        """
        @return: Return the resolution root if this resource was resolved relatively, or None 
        @rtype: Resource or NoneType
        """        
        raise NotImplementedError(self.__class__)
    
class ResourceMetricProcessor(object):
    """
    @deprecated: This is flawed ... It should not be necessary to provide 
        different implementations for different kinds of resources. It
        appears to be currently unused. 
    @todo: It should be possible to query multiple metrics.
    """
    
    def get_metric(self):
        """
        @rtype: L{ContentMetric}
        """
        raise NotImplementedError(self.__class__)        
    
    def apply_metric_to_resource(self, resource):
        """
        Returns the number of apply_metric_to_resource contained in a resource.
        
        @param resource: the resource
        @type resource: a subtype of Resource
        
        TODO @raise ...: if the supplied resource is not supported  
        """
        raise NotImplementedError(self.__class__)

class GenerationStrategy(object):
    """
    An abstraction of a resource transformation strategy.
    """
    
    def process(self, input_resource, generator_func):
        """
        Transform an input resource to an output resource using a given transformation function.
        Guarantees that the input resource is unmodified on return, if the transformation function fails.
        
        @param input_resource: The input resource.
        @type input_resource: Resource (implementations might accept only specific subtypes of Resource)
        @param generator_func: A transformation function which reads from a given resource and writes to a given resource.
        @type generator_func: (Resource, Resource) -> [x]
        @return: The result of generator_func
        @rtype: [x]
        
        @raise ValueError: If the input_resource is not acceptable by the implementation.
        
        @todo: Should be renamed to a more specific method name.
        @todo: The generator_func could operate on open files (streams) rather than the resources, but
          then the generator function could not use the name of the resource.
        @todo: Should not raise ValueError on a generation strategy failure. 
        @todo: There should be a way for a caller to know which output_resource is generated for a given 
          input resource, either as a result of process or by a different method. 
        """
        raise NotImplementedError(self.__class__)    
