# -*- coding: UTF-8 -*-

'''
Basic interfaces and supporting framework classes to realize other interfaces.

Created on 07.10.2010

@author: SIGIESEC
'''

class ContentMetric(object):
    # TODO this should be moved to another, more specific interface module
    
    def apply_metric(self, lines):
        raise NotImplementedError(self.__class__)        

class Adaptable(object):
    # TODO currently unused
    
    def get_adaptees(self):    
        raise NotImplementedError(self.__class__)
    
    def adapt_to(self, class_object_or_objects):
        """
        Returns an adapter to a class or the first of several classes. 
        
        @param class_object_or_objects: an instance or iterable of instances of types.TypeType
        @return: an adapter, or None if none can be created
        @rtype: one of class_object_or_objects, or NoneType 
        """
        raise NotImplementedError(self.__class__)    
    
class EnumerationItem(object):
    __last_id = dict()
    
    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self
    
    def __register(self):
        if self.__class__ == EnumerationItem:
            raise TypeError("Only subclasses of EnumerationItem may be instantiated")
        if self.__class__ not in EnumerationItem.__last_id:
            EnumerationItem.__last_id[self.__class__] = 0
        EnumerationItem.__last_id[self.__class__] += 1
        return EnumerationItem.__last_id[self.__class__] - 1

    def __init__(self):
        self.__id = self.__register()
        
    def id(self):
        return self.__id

# TODO change Enumeration to something based on a special metaclass, such as the approach in http://www.python.org/doc/essays/metaclasses/Enum.py
class Enumeration(object):
    _type = None
    
    @classmethod
    def __type_set(cls):
        if cls._type == None:
            raise RuntimeError("No type set on Enumeration type %s" % cls)

    @classmethod
    def name(cls, value):
        cls.__type_set()
        if not isinstance(value, cls._type):
            raise TypeError("value = %s %s" % (str(value), type(value)))  
        for (name, var) in cls.__dict__.iteritems():
            if var == value:
                return name
            
        raise ValueError("value = %s" % (str(value)))  

    @classmethod
    def names(cls, values):
        return map(cls.name, values) 

    @classmethod
    def values(cls):
        cls.__type_set()
        if not hasattr(cls, "values__"):
            cls. values__ = [var for (_name, var) in cls.__dict__.iteritems() if isinstance(var, cls._type)]
        return cls.values__
      
    @classmethod
    def is_mapping_complete(cls, dictionary):
        return set(cls.values()) == set(dictionary.keys())
    
    @classmethod
    def missing_values(cls, dictionary):
        return set(cls.values()) - set(dictionary.keys())

    @classmethod
    def enum_item_name(cls, value):
        try:
            return cls.name(value)
        except:
            return "non-item %s" % str(value)

    @classmethod 
    def map(cls, dictionary, key):
        assert len(cls.missing_values(dictionary)) == 0, \
            "dictionary for Enumeration %s incomplete, missing values %s" % \
                (cls, ",".join(map(cls.enum_item_name, cls.missing_values(dictionary)))) 
        return dictionary[key]
    
