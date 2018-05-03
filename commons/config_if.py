#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Marker interfaces that can be used by targets of the IoC mechanism.    

Created on 05.09.2010

@author: SIGIESEC
'''

# TODO These marker interfaces should be non-mandatory,
# it should be possible to specify the use of other 
# or no such marker interfaces to make the IoC mechanism completely non-intrusive.

class AutoConfigurable(object):
    """
    A marker interface for auto-configurable interface.
    """
    pass

class FactoryRequired(object):
    """
    A marker interface for implementations of an AutoConfigurable interface, whose instance methods 
    are implemented, but the constructor requires additional dependencies to be injected, which
    require the definition of a factory wrapper class.
    """
    pass

class ConfigDependent(object):
    """
    A marker interface for classes that use configurator-injected configuration variables, i.e.
    which can only be instantiated after the configuration variables have been initialized by the
    Configurator or manually.
    
    Architectural rule: ConfigDependent classes should only be contained in wrapper modules (*_wrap). 
    """
    pass

class Decorator(object):
    """
    A marker interface for decorator classes, whose constructor's first parameter is named decoratee 
    and accepts an instance with the same interface.
    """
    pass

class ObjectFactory(object):
    # TODO consider changing the signature of create_factory and create_instance such that they do not use the
    # *args/**kwargs transformation, but use an explicit list of positional and dictionary of named arguments.
    # This would also avoid the possible name clash and the xxclsxx parameter could be safely renamed to cls.
    # Probably, more parameters will be added in the future, e.g. a name of the object to create.
    
    def create_factory(self, xxclsxx, **kwargs):
        """
        Creates a factory function for a type that performs autowiring of any parameters when called 
        unless they are overridden by kwargs.
        
        @param xxclsxx: The type to be instantiated. If it is an interface, an implementation of the interface is selected. 
        @type xxclsxx: TypeType
        @rtype: xxclsxx
        """
        raise NotImplementedError
    
    def create_instance(self, *args, **kwargs):
        """
        Creates an instance of a class and autowires any parameters unless they are overridden by kwargs.
        
        @param xxclsxx: A keyword-only parameter denoting the class to be instantiated.        
        @type xxclsxx: TypeType
        @rtype: xxclsxx
        """
        raise NotImplementedError
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()
