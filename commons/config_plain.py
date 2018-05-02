'''
Implementation of a simple line-based autowire format (commons.config_extension_if.IAutoWireFormatSuite).

It has limited support for specifying parameters to pass to constructors of the concrete adapter classes, but has no support
for defining named objects that can be referenced in other parameters.

Created on 30.05.2011

@author: SIGIESEC
'''
from commons.config_extension_if import IAutoWireFormatSuite, ParseError, ParseContext,\
    IAutoWireConfigUnparser
from commons.config_util import (ClassLoader, ConfigTools, 
    AutoWireConfigParserBase)
import logging
import re
from types import TupleType

class PlainAutoWireFormatSuite(IAutoWireFormatSuite):
    def get_parser(self):
        return PlainAutoWireConfigParser()

    def get_unparser(self, abstracts_to_concrete_map):
        return PlainAutoWireConfigGenerator(abstracts_to_concrete_map,
                                            args_func=ClassLoader.get_constructor_args)


class PlainAutoWireConfigGenerator(IAutoWireConfigUnparser):
    """
    >>> gen = AutoWireConfigGenerator()
    >>> gen.scan_module('commons.database_if')
    >>> print(gen)
    # commons.database_if.DatabaseConfiguration=???
    >>> gen.scan_module('configuration.config_db')
    >>> print(gen)
    # commons.database_if.DatabaseConfiguration=configuration.config_db.RevEngToolsDatabaseConfiguration
    """

    def __init__(self, abstracts_to_concrete_map, selection_strategy_func=lambda x, y: None, args_func=lambda x: None):
        self.__abstracts_to_concrete_map = abstracts_to_concrete_map
        self.__selected = selection_strategy_func
        self.__args = args_func

    def __abstract_to_concrete(self):
        return self.__abstracts_to_concrete_map

    @staticmethod
    def __argstring(args):
        if args != None and len(args):
            if isinstance(args, dict):
                return '[%s]' % ",".join("%s=%s" % (arg, val) for (arg, val) in args.iteritems())
            else:
                return '[%s]' % ",".join("%s=???" % arg for arg in args)
        else:
            return ''
        
    @staticmethod
    def as_names(some_map):
        """
        Returns an abstract-to-concrete map as name
        
        @param some_map: dict(str,str) dict(tuple(str,str),tuple(str,str)) or dict(object, object)
        @rtype: iter(tuple(str,str))
        """
        if len(some_map):
            key = some_map.iterkeys().next()
            if isinstance(key, basestring):
                return some_map.iteritems()
            elif isinstance(key, TupleType) and isinstance(key[0], basestring):
                return ((ConfigTools.pair_to_fqn(a), [ConfigTools.pair_to_fqn(cs)])
                        for (a, (cs, _args)) in some_map.iteritems()
                        )
            else:
                return ((ConfigTools.to_fqn(a), map(ConfigTools.to_fqn, cs))
                        for (a, cs) in some_map.iteritems())
        else:
            return ()

    def get_configuration_lines(self):
        COMMENT_PREFIX = "# "
        if len(self.__abstract_to_concrete()):
            abstract_to_concrete_names = sorted(self.as_names(self.__abstract_to_concrete()))
            for abstract, concretes in abstract_to_concrete_names:
                if len(concretes) == 0:
                    yield ("%s%s=???" % (COMMENT_PREFIX, abstract))
                else:
                    selected = self.__selected(abstract, concretes)
                    for concrete in concretes:
                        args = self.__args(concrete)
                        yield ("%s%s=%s%s" % (COMMENT_PREFIX if concrete != selected else '',
                                            abstract,
                                            concrete,
                                            self.__argstring(args)))

                yield ("")

    def __str__(self):
        lines = self.get_configuration_lines()
        return "\n".join(lines)

class PlainAutoWireConfigParser(AutoWireConfigParserBase):
    def __init__(self, *args, **kwargs):
        AutoWireConfigParserBase.__init__(self, *args, **kwargs)
        self._current_line_number = None

    @staticmethod
    def __parse_parameter(arg):
            # alternatives:
            #  1. use some heuristic 
            #  2. encode type in parameter value, e.g. ...:str, ...:class, ...:int;  
            #  3. supply this information by metadata (cf. Eclipse extension points)
            
            # currently, a combination of 2 and 1 is done. If a type is given, it is used; the default is str
        (name, value) = arg.split("=")
        if value.find(":") != -1:
            (value, parameter_type) = value.split(":")             
        else:
            parameter_type = "str"
        return (name, dict({"type":parameter_type, "value":value}))
                 
    def parse_lines(self, lines):
        """
        All lines which are not commented, not empty and match the regular
        expression are parsed into modules and classes with arguments.
        e.g. abstract.Abstract=concrete.Concrete[a=12] will be parsed to
        ("abstract", "Abstract"), (("concrete", "Concrete"),
        dict({"a": dict({"type": "str", "value": "12"})})
        """
        for (self._current_line_number, line) in enumerate(lines):
            line = line.strip()
            if not line.startswith('#') and len(line) > 0:
                match = re.match(r'^([\w.]+)[.](\w+)=([\w.]+)[.](\w+)(?:[[](.*)[]])?$', line)
                context = ParseContext(self._current_resource, self._current_line_number + 1)
                if match != None:
                    abstract_module = match.group(1)
                    abstract_class = match.group(2)
                    concrete_module = match.group(3)
                    concrete_class = match.group(4)
                    arguments = match.group(5)
                    if not arguments:
                        parsed_arguments = None
                    else:
                        parsed_arguments = dict(self.__parse_parameter(arg)
                                    for arg in arguments.split(",")) 
                        
                    entry = ((abstract_module, abstract_class),
                               ((concrete_module, concrete_class),
                               parsed_arguments))
                        # TODO no comma, equal sign or colon may appear in the argument values this way!
                    if self._process_entry(entry, context):
                        yield entry
                else:
#                    warnings.warn("Invalid line in autowire configuration %s" % (line))                    
                    self._errors.append(ParseError(logging.WARNING,
                                                    "Invalid line in autowire configuration: %s" % (line,),
                                                    context))
        self._current_line_number = None
