#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 05.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_util import AggregateMapper
from commons.config_if import ConfigDependent
from commons.core_if import ContentMetric
from commons.core_util import StringTools, frozendict, call_and_return
from commons.graph.attrgraph_if import NodeGrouper
from commons.metric_util import PlainLinesOfCodeMetric
from commons.os_util import (NormalizedPathsIter, ResourceResolver, WalkTools, 
    PathTools)
from cpp.cpp_if import (FileToModuleMapSupply, VirtualModuleTypes, 
    CppFileConfiguration)
from itertools import chain, imap
from string import Template
import logging
import os.path
import copy

class IncludePathMappingResolver(object):
    def __init__(self, variables=dict()):
        self.__variables = variables

    def __replace_variables(self, line):
        return Template(line[0]).safe_substitute(self.__variables)

    def interpret_line(self, line):
        if len(line) > 1:
            return (self.__replace_variables(line), line[1])
        else:
            return (self.__replace_variables(line), None) # TODO oder sollen die einfach wegfallen?
    


class IncludePathMapping(object):
    def __init__(self, mapping_source, variables):
        self.__resolver = IncludePathMappingResolver(variables)
        self.__include_directory_to_module_map = self.__calculate_include_directory_to_module_map(mapping_source)
    
    @staticmethod
    def _include_path_mapping_filename(config_dir, system_name):
        #self.__logger.debug("config_basic is %s, config dir is %s" % (config_basic, config_basic.get_config_dir()))
        return os.path.join(config_dir,
                            'config.local.%s.includepaths' % system_name)
    
    def __calculate_include_directory_to_module_map(self, mapping_source):
        return dict(self.__resolver.interpret_line(line) for line in mapping_source)

    def get_include_directory_to_module_map(self):
        # TODO man muss auch Untermodule definieren können, dies jedoch in einer separaten Datei, die
        # unabhängig von den absoluten Includeverzeichnissen ist
        return frozendict(self.__include_directory_to_module_map)
    
    def get_include_directories(self):
        return self.get_include_directory_to_module_map().iterkeys()
    
    def get_external_modules(self):
        return set(self.get_include_directory_to_module_map().values())
    
    def find_module_for_header(self, header):
        # TODO kommt es hier auch vor, dass ein Verzeichnis Unterverzeichnis des anderen ist?
        # dann müsste man sie rückwärts sortieren
        for (directory, module) in self.get_include_directory_to_module_map().iteritems():
            if header.startswith(directory):
                return module
        return None
    
    def map_dir_to_external_module(self, header):
        for (directory, module) in self.get_include_directory_to_module_map().iteritems():
            if header.startswith(directory):
                return header.replace(directory, '<%s>' % module)
        return header

class IncludePathMappingFactory(object):
    def _default_directory_vars(self):
        return dict({"local_source_base_dir":self.__basic_config.get_local_source_base_dir()})

    def __init__(self, basic_config, directory_vars=None, additional_directory_vars=None):
        self.__basic_config = basic_config
        if directory_vars:
            self.__directory_vars = copy.copy(directory_vars)
        else:
            self.__directory_vars = self._default_directory_vars()
        if additional_directory_vars:
            self.__directory_vars.update(additional_directory_vars)
        

    @staticmethod
    def get_default_mapping_source(config_dir, system_name):
        return NormalizedPathsIter.create(filename=IncludePathMapping._include_path_mapping_filename(config_dir, system_name),
                                          what="local include path", 
                                          delimiter=',')
        
    def create(self):
        return IncludePathMapping(mapping_source=self.get_default_mapping_source(self.__basic_config.get_config_dir(), 
                                                                                 self.__basic_config.get_system()),
                                  variables=self.__directory_vars)

    
def regular_guard(file_name):
    return os.path.basename(file_name).upper().replace(".", "_")

def is_ms_generated_guard(file_name, guard):
    return guard.upper().startswith("AFX_" + regular_guard(file_name)) and guard.upper().endswith("__INCLUDED_")


class PseudoModuleSizer(object):
    def __init__(self, mapper, path_resolver, file_length_calculator=None):
        assert(isinstance(mapper, FileNameMapper))
        self.__mapper = mapper
        self.__module_sizes = dict()
        assert isinstance(path_resolver, ResourceResolver)
        self.__path_resolver = path_resolver
        if file_length_calculator:
            assert isinstance(file_length_calculator, ContentMetric)
            self.__metric = file_length_calculator
        else:
            self.__metric = PlainLinesOfCodeMetric()
     
    def module_size(self, pseudomodule_name):
        if pseudomodule_name not in self.__module_sizes:
            self.__module_sizes[pseudomodule_name] = \
               sum(imap(self.__metric.apply_metric, imap(lambda x: self.__path_resolver.resolve(x).open(), 
                        self.__mapper.get_individuals_for_output_aggregate(pseudomodule_name))))
            
        return self.__module_sizes[pseudomodule_name]


class CppProjectUtil(object):
    @staticmethod
    def scan_project_files(base_dirs, local_source_base_dir, cpp_file_configuration, logger):
        extensions = tuple([] + cpp_file_configuration.get_implementation_file_extensions() + cpp_file_configuration.get_header_file_extensions())
        #self.__logger.log(logging.INFO, "Scanning files with extensions %s in %s recursively" % (extensions, base_dirs))
        abs_paths = chain.from_iterable((
                WalkTools.walk_extensions(onerror=logger.warning, extensions=extensions, top=path, skip_dirs=[".svn"]) if os.path.isdir(path) else 
                ((path, ) if os.path.exists(path) else call_and_return(lambda:logger.warning("%s does not exist" % path), ()))) for 
            path in imap(lambda rel_path:os.path.join(local_source_base_dir, rel_path), base_dirs))
        files = (PathTools.relative_path(path_name=abs_path, relative_to=local_source_base_dir + os.path.sep, ignore_absolute=False) for abs_path in abs_paths)
        return list(files)
    
class CommentFilter(object):
    """
    Filters C/C++ comments from an input stream.
    The transformation has the following properties:
    * The number of lines is not changed.
    * Line endings are normalized to unix style.
    
    Limitations:
    * Trigraphs are not supported. Certain cases containing trigraphs will produce erroneous results.
    """
    LINE_COMMENT = "//"
    COMMENT_START = "/*"
    COMMENT_END = "*/"
    STRING_QUOTE = '"'
    CHAR_QUOTE = '\''
    ESCAPE_CHAR = '\\'
    
    def __init__(self):
        self.__lines_with_comment = 0
        self.__total_lines = 0
        self.__comment_lines = 0
        self.__in_comment = False
        self.__in_string = False
        self.__in_char = False
        self.__logger = logging.getLogger(self.__class__.__module__)
        
    @staticmethod
    def __even_escapes_before(line, pos):
        even = True
        for i in range(pos-1, -1, -1):
            if line[i] == CommentFilter.ESCAPE_CHAR:
                even = not even
            else:
                break
        return even
    
    def filter(self, line_iterator):
        """
        Filters comments from C/C++ code lines.
        
        Implementation note:
        The input is transformed line by line, so memory consumption does not depend on the size of the input.
        
        The state is preserved between calls of filter, so the result of the following is identical:
        
        >>> cf = CommentFilter()
        >>> list(cf.filter("/* first line"))
        ['\\n']
        >>> list(cf.filter("second line */"))
        ['\\n']
        >>> cf = CommentFilter()
        >>> list(cf.filter(["/* first line", "second line */"]))
        ['\\n', '\\n']
        
        @type line_iterator: a iterator of str/unicode (typically an open file) or a single str/unicode
        @rtype: iterator of str or unicode (depending on the type of the input)
        """
        line_no = 0 # TODO convert to field?
        if isinstance(line_iterator, basestring):
            line_iterator = (line_iterator, ) 
        for line in line_iterator:
            line_no += 1
            self.__total_lines += 1
            current_has_comment = self.__in_comment
            
            result = line.__class__()
            skip_until = 0
            line = line.strip("\n\r")
            for i in range(len(line)):
                if i < skip_until:
                    continue
                if line[i] == self.CHAR_QUOTE and self.__even_escapes_before(line, i) and not self.__in_comment and not self.__in_string:
                    self.__in_char = not self.__in_char
                if line[i] == self.STRING_QUOTE and self.__even_escapes_before(line, i) and not self.__in_comment and not self.__in_char:
                    self.__in_string = not self.__in_string
                if i < len(line) and not self.__in_string and not self.__in_char:
                    if line[i:i+len(self.LINE_COMMENT)] == self.LINE_COMMENT and not self.__in_comment:
                        current_has_comment = True
                        break
                    elif line[i:i+len(self.COMMENT_END)] == self.COMMENT_END and self.__in_comment:
                        self.__in_comment = False
                        skip_until = i+len(self.COMMENT_END)
                        continue
                    elif line[i:i+len(self.COMMENT_START)] == self.COMMENT_START and not self.__in_comment:
                        self.__in_comment = True
                        skip_until = i+len(self.COMMENT_START)
                        current_has_comment = True
                        opening_line = (line_no, line) 
                if not self.__in_comment:
                    result += line[i]
                
            if self.__in_string and not line[len(line) - 1] == self.ESCAPE_CHAR:
                self.__logger.warning("Open string at end of line %i = %s" % (line_no, line))
                self.__in_string = False

            if current_has_comment:
                self.__logger.debug("Line with comment: %s" % line)
                self.__lines_with_comment += 1
                
            if not len(result.strip()):
                self.__logger.debug("Comment or empty line: %s" % line)
                self.__comment_lines += 1
                
            self.__logger.debug("Filtered line: %s" % result) 
            yield "%s\n" % result
        if self.__in_comment:
            self.__logger.warning("Open comment at end of iteration, opening line was line %i/%i: %s" % (opening_line[0], line_no, opening_line[1]))
            
    def in_comment(self):
        return self.__in_comment
    
    def lines_with_comment(self):
        return self.__lines_with_comment
            
    def get_statistics_dict(self):
        return dict({"Lines with at least a partial comment": self.__lines_with_comment,
                     "Empty or comment lines": self.__comment_lines,
                     "Total lines": self.__total_lines,
                    })

class FileNameMapper(AggregateMapper, ConfigDependent):
    """
    >>> from cpp.cpp_default import DefaultCppFileConfiguration

    # TODO check if this is really the expected behaviour
    >>> mapper = FileNameMapper({"A/a.cpp": "A", "B/a.cpp": "B", "B/b.cpp": "B"}, ("A", "B"), optimiseNodeNames=True, config_cpp_files=DefaultCppFileConfiguration())
    >>> mapper.get_pseudomodule_name("A/a.cpp")
    'A:a'
    
    # TODO check what was meant here
    #>>> mapper.get_nodename_for_filename("A/a.cpp")
    #'A:a'
    #>>> mapper.get_nodename_for_filename("B/b.cpp")
    #'b'

    >>> sorted(mapper.get_individuals_for_output_aggregate("A:a"))
    ['A/a.cpp']

    # TODO check what was meant here
    #>>> sorted(mapper.get_individuals_for_output_aggregate("B"))
    #['B/b.cpp']

    # TODO check if this is really the expected behaviour
    >>> mapper = FileNameMapper({"A/a.cpp": "XA", "B/a.cpp": "XB", "B/b.cpp": "XB"}, ("XA", "XB"), optimiseNodeNames=True, config_cpp_files=DefaultCppFileConfiguration())
    >>> sorted(mapper.get_individuals_for_output_aggregate("A:a"))
    ['A/a.cpp']
    """

    @staticmethod
    def filename_to_cpp_pseudomodule_func(cpp_extensions):
        return lambda filename:StringTools.strip_suffixes(os.path.basename(filename), cpp_extensions)
    
    @staticmethod
    def filename_to_cpp_pseudomodule(filename, cpp_extensions):
        """
        >>> FileNameMapper.filename_to_cpp_pseudomodule("A/b.cpp", (".cpp",))
        'b'
        """
        return FileNameMapper.filename_to_cpp_pseudomodule_func(cpp_extensions)(filename)

    def __init__(self, file_to_module_map, modules, config_cpp_files=CppFileConfiguration(), *args, **kwargs):
        cpp_extensions = tuple(chain(config_cpp_files.get_header_file_extensions(), 
            config_cpp_files.get_implementation_file_extensions(), 
            (".impl", )))
        AggregateMapper.__init__(self,
                        file_to_module_map=file_to_module_map,
                        modules=modules,
                        local_output_aggregate_for_individual_func=self.filename_to_cpp_pseudomodule_func(cpp_extensions), 
                        get_raw_modulename=VirtualModuleTypes.remove_suffixes,
                        *args, **kwargs)

config_file_to_module_map_supply = FileToModuleMapSupply()

class FileBasedNodeGrouper(NodeGrouper, ConfigDependent):
    def __init__(self):
        self.__individual_to_input_aggregate_map = None

    def configure_nodes(self, nodes):
        node_set = set(nodes)
        file_to_module_map = config_file_to_module_map_supply.generate_file_to_module_map().iteritems()
        self.__individual_to_input_aggregate_map = dict((key, VirtualModuleTypes.remove_suffixes(value))
                                         for (key, value) in file_to_module_map
                                         if key in node_set)

    def get_node_group_prefix(self, module):
        if module in self.__individual_to_input_aggregate_map:
            return self.__individual_to_input_aggregate_map[module]
        else:
            return None

    def node_group_prefixes(self):
        return set(self.__individual_to_input_aggregate_map.values())    
    
    
# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()


