#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
An X{include path specification} is either 
a) internal: a relative path relative to the project root or the including file,
b) external: a relative path relative to an external include directory in angle brackets.
All paths must be valid POSIX paths. For example, the following are valid internal include 
path specifications, assuming the corresponding header files exist:
a.h
a/b.h

The following are valid external include path specifications:
<string>
<cppunit/cppunit.h>

The following are INVALID include path specifications:
"a.h"
cppunit\cppunit.h

NOTE: this distinction of internal and external include path specifications is not the same as 
that of the C/C++ standard, which only distinguishes between include path specifications that MAY
be relative to the including file (enclosed by double quotes) or those that can only be relative 
to a specified include directory (enclosed by angle brackets).

Created on 20.09.2010

@author: SIGIESEC
@copyright: Copyright 2010-2012 by BTC Business Technology Consulting AG
'''
from commons.config_if import AutoConfigurable
from commons.os_util import PathTools
from cpp.cpp_if import CppLiterals
from cpp.cpp_util import regular_guard
from datetime import datetime
from itertools import imap
import logging
import os.path
import re

# TODO split into interface, implementation and wrapper modules
# TODO separate rewriting of a single include directive out of IncludeListGeneratorConfig 

class HeaderExceptionMapper(AutoConfigurable):
    # TODO Klären, ob dieser auch die Abbildung von analyzer-paths auf rel_to_root-paths übernehmen soll
    # oder alternativ (klingt besser) bereits als Eingabe rel_to_root_paths bekommt. Dann können analyzer_paths 
    # ganz aus IncludeListGenerator entfernt werden 
    
    def map_exceptions(self, header_paths_analyzer):
        raise NotImplementedError(self.__class__)
    
class NullHeaderExceptionMapper(HeaderExceptionMapper):
    def map_exceptions(self, header_paths_analyzer):
        return header_paths_analyzer
    
    
class HeaderCanonicalSorter(AutoConfigurable):
    
    def canonical_groups(self, include_paths_rel_to_root_or_external):
        """
        Sorts & groups a list of include path specifications.
        
        @param include_paths_rel_to_root_or_external: the include path specifications
        @type include_paths_rel_to_root_or_external: an iterable of strings (include path specifications)
        
        @rtype: iterable of tuples of strings (include path specifications)
        
        @postcondition: the set of elements returned is equal to that of the input, i.e. 
          sorted(set(itertools.chain.from_iterable(self.canonical_groups(include_paths_rel_to_root_or_external))))==sorted(set(include_paths_rel_to_root_or_external)), 
          assuming include_paths_rel_to_root_or_external is a collection 
        @postcondition: every group contains at least one element, i.e. 
          len(filter(lambda group: len(group)==0, self.canonical_groups(include_paths_rel_to_root_or_external)))==0
        """
        raise NotImplementedError(self.__class__)
    
class NullHeaderCanonicalSorter(HeaderCanonicalSorter):    
    """
    Only sorts and filters duplicates.
    """
    
    def canonical_groups(self, include_paths_rel_to_root_or_external):
        """
        >>> HeaderCanonicalSorter().canonical_groups(['<string>', '__prid4/inc/foo.c', 'inc/bar.c', '<string>'])
        (('<string>', '__prid4/inc/foo.c', 'inc/bar.c'),)
        """ 
        #return (sorted(set(map(os.path.normpath, include_paths_rel_to_root_or_external))), )
        if len(include_paths_rel_to_root_or_external) > 0:
            return (tuple(sorted(set(include_paths_rel_to_root_or_external))), )
        else:
            return ()
    
class StandardGroupCanonicalSorter(HeaderCanonicalSorter):
    """
    Splits include path specifications into two groups, first internal, then external 
    include path specifications.
    """

    def canonical_groups(self, include_paths_rel_to_root_or_external):
        groups = [set(), set()]
        for include_path_rel_to_root_or_external in include_paths_rel_to_root_or_external:
            if include_path_rel_to_root_or_external.startswith("<"):
                groups[1].add(include_path_rel_to_root_or_external)
            else:
                groups[0].add(include_path_rel_to_root_or_external)
        return tuple(imap(tuple, imap(sorted, (group for group in groups if len(group) > 0))))
        
class HeaderPathMapper(AutoConfigurable):
    def server_to_rel_to_root_path(self, server_path):
        """
        Maps an (absolute) server path to a path relative to the project root directory.
        The default implementation assumes that the server path already is relative to the 
        project root directory.
        """
        assert not os.path.isabs(server_path)
        return server_path
    
class IncludeListGeneratorConfig(object):
    def __init__(self, 
                 use_redundant_include_guards = True,
                 include_paths_rel_to_root = True,
                 use_pragma_once = False):
        self.__use_redundant_include_guards = use_redundant_include_guards
        self.__include_paths_rel_to_root = include_paths_rel_to_root
        self.__use_pragma_once = use_pragma_once
        if self.__use_redundant_include_guards and self.__use_pragma_once:
            raise ValueError("Cannot use redundant include guards when using #pragma once")
    
    def use_redundant_include_guards(self):
        """
        
        @rtype: BooleanType
        """
        return self.__use_redundant_include_guards
    
    def include_paths_rel_to_root(self):
        """
        if False, relative to including file

        @rtype: BooleanType
        """
        return self.__include_paths_rel_to_root
    
    def use_pragma_once(self):
        """
        if False, use "traditional" include guards

        @rtype: BooleanType
        """
        return self.__use_pragma_once


class IncludeGuardNormalizer(object):
    # TODO also move redundant include guard creation here?
    
    def __init__(self, use_pragma_once):
        self.__use_pragma_once = use_pragma_once
        
    def has_include_guards(self):
        return not self.__use_pragma_once
        
    def create_include_guard(self, path):
        if self.__use_pragma_once:
            raise RuntimeError("internal error: cannot create include guard, using pragma once") # use better exception  
        else:
            return regular_guard(path)
        
    def create_header(self, path):
        lines = list()
        if self.__use_pragma_once:
            lines.append("#pragma once")
        else:
            lines.append("#ifndef %s" % (self.create_include_guard(path), ))
            lines.append("#define %s" % (self.create_include_guard(path), ))
            lines.append("")
        return lines

    def create_footer(self, path):
        if not self.__use_pragma_once:
            yield "#endif // END of #ifndef %s" % (self.create_include_guard(path), )
        else:
            pass # #pragma once does not need an end
        
class PreprocessorConstants(object):
    INCLUDE_DIRECTIVE = "#include"
    INCLUDE_DIRECTIVE_REGEX_RAW = r"#\s*include"
    INCLUDE_DIRECTIVE_REGEX = re.compile(INCLUDE_DIRECTIVE_REGEX_RAW)
    INCLUDE_DIRECTIVE_SPLIT_REGEX = re.compile(r'(.*)' + INCLUDE_DIRECTIVE_REGEX_RAW + r'(.*)')
    REGEXSTR_FILENAME_CHAR = r'[A-Za-z0-9._\-/\\]'
    REGEX_INCLUDE_SPECIFICATION_QUOTED = re.compile(r'"(' + REGEXSTR_FILENAME_CHAR + r'+)"')
    REGEX_INCLUDE_SPECIFICATION_ANGLE = re.compile(r'<\s*(' + REGEXSTR_FILENAME_CHAR + r'+)\s*>')
    
class IncludePathSpecificationTools(object):
    @staticmethod
    def is_external_include(include_path_rel_to_root_or_external):
        # TODO check if valid
        return include_path_rel_to_root_or_external.startswith("<")
    
class IncludeDirectiveGenerator(object):
    def __init__(self, include_paths_rel_to_root):
        self.__include_paths_rel_to_root = include_paths_rel_to_root
    
    def __include_parameter_internal(self, include_path_rel_to_root, repair_path):
        if self.__include_paths_rel_to_root:
            include_path = include_path_rel_to_root
        else:
            include_path = PathTools.relative_path(include_path_rel_to_root, repair_path)
        return PathTools.unix_normpath(include_path)

    def create_raw_include_directive(self, repair_path, include_path_rel_to_root_or_external):
        if IncludePathSpecificationTools.is_external_include(include_path_rel_to_root_or_external):
            include_parameter = include_path_rel_to_root_or_external
        else:
            include_parameter = "\"%s\"" % self.__include_parameter_internal(include_path_rel_to_root_or_external, repair_path)
        raw_include_directive = "%s %s" % (PreprocessorConstants.INCLUDE_DIRECTIVE, include_parameter)
        return raw_include_directive
        
class IncludeListGeneratorInternal(object):
    def __init__(self, include_guard_normalizer, config, include_rule_checker, header_exception_mapper, header_path_mapper, header_canonical_sorter, include_generation_timestamp=True):
        self.__use_pragma_once = config.use_pragma_once()
        self.__redundant_include_guards = config.use_redundant_include_guards()
        self.__include_guard_normalizer = include_guard_normalizer
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__include_rule_checker = include_rule_checker
        self.__header_exception_mapper = header_exception_mapper
        self.__header_path_mapper = header_path_mapper
        self.__header_canonical_sorter = header_canonical_sorter
        self.__include_generation_timestamp = include_generation_timestamp
        self.__include_directive_generator = IncludeDirectiveGenerator(include_paths_rel_to_root=config.include_paths_rel_to_root())
    
    def __process_internal_include_path(self, include_path_rel_to_root, repair_path, raw_include_directive):
        lines = []
        if self.__include_rule_checker.is_legal_dependency(repair_path, include_path_rel_to_root):
            comment_prefix = ''
        else:
            comment_prefix = CppLiterals.LINE_COMMENT_PREFIX
            self.__logger.warning("Illegal included file %s, probably wrong duplicate, commenting out #include directive" % (include_path_rel_to_root, ))
        indentation = ""
        if (not self.__use_pragma_once) and self.__redundant_include_guards:
            lines.append("#ifndef %s" % self.__include_guard_normalizer.create_include_guard(include_path_rel_to_root))
            indentation = "    "
        lines.append(comment_prefix + indentation + raw_include_directive)
        if (not self.__use_pragma_once) and self.__redundant_include_guards:
            lines.append("#endif")
        return lines

    def __process_include_groups(self, include_paths_rel_to_root_or_external_groups, repair_path):
        lines = []
        for include_paths_rel_to_root_or_external_ordered in include_paths_rel_to_root_or_external_groups:
            for include_path_rel_to_root_or_external in include_paths_rel_to_root_or_external_ordered:
                raw_include_directive = self.__include_directive_generator.create_raw_include_directive(repair_path, include_path_rel_to_root_or_external)
                if IncludePathSpecificationTools.is_external_include(include_path_rel_to_root_or_external):
                    lines_this_directive = (raw_include_directive, )
                else:
                    lines_this_directive = self.__process_internal_include_path(include_path_rel_to_root_or_external, repair_path, raw_include_directive)
                lines.extend(lines_this_directive)
            lines.append("")
        if len(lines) > 0:
            lines.pop()
        return lines

    def generate_include_directives(self, repair_path, include_paths):
        self.__logger.info("Generating include directives for %s" % (repair_path, ))
        lines = []
        
        include_paths_mapped = self.__header_exception_mapper.map_exceptions(include_paths)
        include_paths_rel_to_root_or_external = map(self.__header_path_mapper.server_to_rel_to_root_path, include_paths_mapped)
        include_paths_rel_to_root_or_external_groups = \
            self.__header_canonical_sorter.canonical_groups(include_paths_rel_to_root_or_external)
        lines.append("// *** list of %i include directives%s (%i)" %
                      (sum(map(len, include_paths_rel_to_root_or_external_groups)), 
                       ", generated on %s" % str(datetime.today()) if self.__include_generation_timestamp else "", 
                       hash(include_paths_rel_to_root_or_external_groups)))
        lines.extend(self.__process_include_groups(include_paths_rel_to_root_or_external_groups, repair_path))
        lines.append("// *** end of generated include list")
        lines.append("")
        #self.__previous_empty = 1
        
        return lines

class NullHeaderPathMapper(HeaderPathMapper):
    def server_to_rel_to_root_path(self, server_path):
        return server_path

if __name__ == "__main__":
    import doctest
    doctest.testmod()
