"""
Contains interfaces used to provide extensions to the IoC mechanism.

Created on 15.08.2012

@author: SIGIESEC
"""

class Configuration(object):
    """
    Interface to provide external configuration data to an IoC context. 
    
    This interface may be implemented to provide other configuration contexts to the IoC mechanism. 
    """
    
    # TODO this is not really necessary, the dict interface could be used instead
    
    def get(self, key, default=None):
        if default != None:
            return default
        else:
            raise ValueError("No value for key %s" % (key,))
        
class ParseContext(object):
    def __init__(self, resource, line=None, column=None):
        self.__resource = resource
        self.__line = line
        self.__column = column

    def get_resource(self):
        return self.__resource

    def get_line(self):
        return self.__line

    def get_column(self):
        return self.__column
    
    def __str__(self):
        return "%s (%s)" % (str(self.__resource), ", ".join(filter(None, ("line %i" % self.__line if self.__line else None, 
                                                                          "col %i" % self.__column if self.__column else None))))

    resource = property(get_resource, None, None, "resource's docstring")
    line = property(get_line, None, None, "line's docstring")
    column = property(get_column, None, None, "column's docstring")

class ParseError(object):
    def __init__(self, severity, message, context):
        assert isinstance(context, ParseContext)
        self.__severity = severity
        self.__message = message
        self.__context = context

    def get_severity(self):
        return self.__severity

    def get_message(self):
        return self.__message

    def get_context(self):
        return self.__context
    
    def __str__(self):
        return "%s: %s (%s)" % (self.__severity, self.__message, self.__context)
    
    def __repr__(self):
        return "ParseError(%s,%s,%s)" % (repr(self.__severity), repr(self.__message), repr(self.__context))

    severity = property(get_severity, None, None,  "severity's docstring")
    message = property(get_message, None, None,  "message's docstring")
    context = property(get_context, None, None, "context's docstring")

class IAutoWireConfigParser(object):
    def parse_lines(self, lines):
        """
        Provides parse results over an iterable of input lines which are 
        parsed according to the format of the implementation.
        
        @attention: This is a generator function, i.e. it does not process
          the input lines at once, but only one by one when you iterate 
          through its result. C{has_errors} and C{get_errors} will only contain 
          information based on the lines which have already been processed.
          Usually, it makes only sense to call C{has_errors} and C{get_errors}
          after you have iterated through the complete result. If you call C{parse_lines}
          multiple times, any errors will be added to the previous errors.
          Currently, the errors will never be reset during the lifetime
          of the IAutoWireConfigParser object.        
        
        @param lines: the input data as an iterable of strings
        @return: the parsed entries
        @rtype: an iterable of entries of the type (str, (str, dict))
        """
        raise NotImplementedError(self.__class__)
    
#    def parse_resources(self, resources):
#        raise NotImplementedError(self.__class__)

    def parse_files(self, filenames):
        raise NotImplementedError(self.__class__)

    def has_errors(self):
        """
        Checks whether any input lines parsed by the generated iterable of 
        C{parse_lines} contained any errors. 
        
        If has_errors returns False, get_errors will return an empty iterable.  
        
        @attention: This only returns errors of the lines which have already 
          been processed. See note under C{parse_lines}.
        @rtype: BooleanType
        """
        raise NotImplementedError(self.__class__)
    
    def get_errors(self):
        """
        Returns the identified errors in the input lines parsed by the generated 
        iterable of C{parse_lines}. 
        
        @attention: This only returns errors of the lines which have already 
          been processed. See note under C{parse_lines}.
          
        @rtype: an iterable of ParseError objects
        """
        raise NotImplementedError(self.__class__)
    
class IAutoWireConfigUnparser(object):
    def get_configuration_lines(self):
        raise NotImplementedError(self.__class__)        
    
class IAutoWireFormatSuite(object):
    """
    A factory for parsers and unparsers of some autowire configuration format.  
    
    Intended to be implemented by extensions that a custom autowire configuration format.
    """
    
    def get_parser(self):
        """
        @rtype: IAutoWireConfigParser
        """
        raise NotImplementedError(self.__class__)
    
    def get_unparser(self, abstracts_to_concrete_map):
        """
        Returns an unparser for the configuration format. 
        
        @raise OperationNotSupported: If unparsing is not supported.
        
        @rtype: IAutoWireConfigUnparser
        """
        raise NotImplementedError(self.__class__)
    
