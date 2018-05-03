#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 02.09.2010

@author: SIGIESEC
'''
from __future__ import with_statement
from commons.config_if import FactoryRequired
from commons.core_util import isinstance_or_duck
from cpp.incl_deps.file_transform_if import (FileTransformationException, 
    ManualProcessingException)
from cpp.incl_deps.include_list_generator import (IncludeListGeneratorConfig, 
    IncludeGuardNormalizer)
from cpp.incl_deps.repair_includes_if import (FileNormalizer, HeaderLister, 
    UsedSymbolsLister, SymbolScanner, RequiredIncludeFilesCalculator)
from itertools import imap
import logging
import re
import warnings

# TODO Handling of symbol references in preprocessor macro definitions: While from the compiler's 
# perspective, the referenced symbol only needs to be declared when the macro is used, for 
# well-formedness, its declaration should be included in the header defining the macro.

# TODO Instead of the file transformation exceptions, own exceptions should be used

class BaseFileNormalizer(FileNormalizer):
    # CONFIG
    config_use_pragma_once = False
    debug = True
    # CONFIG END

    def __init__(self, is_implementation_file_func, include_list_generator_factory, use_pragma_once=None):
        """
        Constructs the object.
        
        @param is_implementation_file_func: a function that determines whether a filename corresponds to an implementation file (.cpp, .cc, 
            .c, ..., as opposed to a header file). The important property of implementation files in this context is whether it can be assumed
            that it can be assumed that used symbols occur literally in the file (header files containing implementations thus need to be 
            considered implementation files in this sense).
        """
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__is_implementation_file = is_implementation_file_func
        if use_pragma_once == None:
            self.__use_pragma_once = self.config_use_pragma_once
            warnings.warn("use use_pragma_once parameter!", category=DeprecationWarning)
        else:
            self.__use_pragma_once = use_pragma_once
        self.__include_guard_normalizer = IncludeGuardNormalizer(use_pragma_once=self.__use_pragma_once)
        self.__include_list_generator_factory = include_list_generator_factory
        
    def __print(self, string):
        if len(string.strip())==0 and self.__previous_empty:
            return
        self.__previous_empty = len(string.strip())==0
        print >>self.__output_file, string
        
    def __print_flush(self):
        if len(self.__previous_line) > 0:
            print >>self.__output_file, self.__previous_line, 
            self.__previous_line = ''

    def __print_no_end_and_flush(self, string):
        if len(string.strip())==0 and self.__previous_empty:
            return
        self.__print_flush()
        self.__previous_empty = len(string.strip())==0
        print >>self.__output_file, string, 
                    
    def __comment_line(self, line, stripped_line):
        if self.__in_comment:
            if stripped_line.find('*/') != -1:
                self.__in_comment = False
            self.__write_line = False
            self.__previous_line += line
            return True
        elif stripped_line.startswith('//'):
            self.__write_line = False
            self.__previous_line += line
            return True
        elif stripped_line.startswith('/*'):
            self.__print_flush()
            # TODO das folgende ist PRINS-spezifisch
            if stripped_line.find('/************') != -1:
                # TODO Dieser Fall sollte allgemeiner jeden Kopfkommentar finden (bzw. den Kopfkommentar puffern und dann gesammelt ausgeben)
                self.__output_include_statements()
            if not (stripped_line.rfind('*/') > stripped_line.find('/*')):
                self.__in_comment = True
            self.__write_line = False
            self.__previous_line += line
            return True
        elif re.match(r'/[*].*[*]/.+', stripped_line):
            self.__logger.warning("Irregular comment line: %s" % (stripped_line, ))
        else:
            return False
            
    def __preamble_line(self, line, stripped_line):
        if self.__preamble == -1:
            # Pr�ambel bereits beendet
            return False
        if self.__preamble == 0 or self.__preamble == 1:
            if stripped_line.startswith('#define VCS') or stripped_line.startswith('VCS'):
                self.__preamble = 1
                self.__write_line = True
                return True
            elif self.__preamble == 1:
                # Ende der Pr�ambel
                self.__preamble = -1
                return False
                
    def __empty_line(self, line, stripped_line):
        if len(stripped_line) == 0:
            # self.__write_line = not self.__previous_empty
            # self.__previous_empty = True
            self.__write_line = True
            return True
        else:
            # self.__previous_empty = False
            return False

    def __log_info(self):
        if self.debug:
            return " (line %i, file %s, state: %s)" % (self.__line_no, self.__repair_path, self.__state_string())
        else:
            return " (line %i, file %s)" % (self.__line_no, self.__repair_path)
            
    def __debug(self, message):
        self.__logger.debug(message + self.__log_info())

    def __warning(self, message):
        self.__logger.warning(message + self.__log_info())

    def __error(self, message):
        self.__logger.error(message + self.__log_info())
        raise FileTransformationException(message)
    
    def __info(self, message):
        self.__logger.info(message + self.__log_info())
        
    def __output_include_statements(self):
        if not self.__includes_written:
            if self.debug:
                self.__debug("First statement line")
            # TODO das folgende ist CAST-spezifisch. Ist das hier überhaupt nötig?
            #include_paths = map(lambda x:x.strip("[]"), self.__included_paths)
            include_paths = self.__included_paths
            if not self.__implementation_file:
                for line in self.__include_guard_normalizer.create_header(path=self.__repair_path):
                    self.__print(line)
            # TODO turn include_list_generator into an attribute and remove the factory
            include_list_generator = self.__include_list_generator_factory(
                                                          include_guard_normalizer=self.__include_guard_normalizer,
                                                          config=IncludeListGeneratorConfig(use_pragma_once = self.__use_pragma_once, use_redundant_include_guards=not self.__use_pragma_once))
            for line in include_list_generator.generate_include_directives(repair_path=self.__repair_path, 
                                                          include_paths=include_paths):
                self.__print(line)
            self.__includes_written = True

    def __include_statement(self, line, stripped_line):
        # TODO skip over already generated include statements!!!
        if stripped_line.startswith("#include"):
            self.__debug("include statement \'%s\'" % (stripped_line, ))
            if self.__includes_written:
                self.__warning("Include statements \'%s\' found after first other statement" % (stripped_line, ))
            self.__write_line = False
            if self.__in_include_guard:
                self.__in_include_guard = False
                self.__in_guarded_include = True
            return True
        else:
            return False

    def __include_guard(self, line, stripped_line):
        # TODO F�r die known/unknown ifdef's br�uchte man eignetlich einen Stack, damit das #endif richtig zugeordnet werden kann
        if self.__in_unknown_ifdef > 0:
            if re.match(r'#include', stripped_line):
                self.__warning("Include statement \'%s\' in unknown #if" % (stripped_line, ))
            if re.match(r'#endif', stripped_line):
                self.__if_level -= 1
                self.__in_unknown_ifdef -= 1
            return False
        elif self.__in_include_guard:
            # TODO check if #define matches #ifndef
            if not self.__implementation_file and re.match('#define\s+[A-Za-z0-9_]+$', stripped_line):
                self.__write_line = False
                self.__include_guard_present = True
                self.__in_include_guard = False
                self.__previous_line = ''
                #self.__output_include_statements()
                return True
            elif self.__include_statement(line, stripped_line):
                self.__previous_line = ''
                return True
            else:
                self.__warning("Not an include guard: (%s/%s)" % (self.__previous_line.strip(), stripped_line))
                self.__print_flush()
                self.__in_include_guard = False
                self.__in_unknown_ifdef += 1
        if self.__include_statement(line, stripped_line):
            return True
        if re.match(r'#if', stripped_line):
            self.__if_level += 1
            if re.match(r'^#ifndef\s+[A-Za-z0-9_]+', stripped_line) or re.match(r'#if[!(]{1,2}defined\(?[A-Za-z0-9_]+\)', stripped_line.replace(' ', '')):
                self.__print_flush()
                self.__previous_line = line
                self.__in_include_guard = True
                self.__write_line = False
                return True
            else:
                self.__warning("Unknown #if found: %s" % (stripped_line, ))
                self.__in_unknown_ifdef += 1
                return False
        elif re.match(r'#endif', stripped_line):
            self.__if_level -= 1
            if self.__if_level < 0:
                self.__error("#endif without matching #if, internal error")
            if self.__include_guard_present and self.__if_level == 0 and self.__use_pragma_once:
                # suppress final #endif if converting from traditional include guard to #pragma once
                self.__write_line = False
                return True
            if self.__in_guarded_include:
                self.__in_guarded_include = False
                self.__write_line = False
                return True
            else:
                return False
        else:
            return False
            
    def __state_string(self):
        return "includes_written=%i, in_comment=%i, preamble=%i, previous_empty=%i, in_guarded_include=%i, include_guard_present=%i, in_include_guard=%i, in_unknown_ifdef=%i, if_level=%i" % \
        (self.__includes_written, self.__in_comment, self.__preamble, self.__previous_empty, self.__in_guarded_include, self.__include_guard_present, self.__in_include_guard, self.__in_unknown_ifdef, self.__if_level)
            
    def __initialize_process_state(self):
        self.__includes_written = False
        self.__in_comment = False
        self.__preamble = 0
        self.__previous_empty = True
        self.__implementation_file = self.__is_implementation_file(self.__repair_path)
        self.__line_no = 0
        self.__in_guarded_include = False
        self.__include_guard_present = False
        self.__in_include_guard = False
        self.__in_unknown_ifdef = 0
        self.__if_level = 0
        self.__previous_line = ''

    def process(self, repair_path, included_paths, input_file, output_file):        
        # TODO move to factory method
        self.__repair_path = repair_path
        self.__included_paths = included_paths
        self.__input_file = input_file
        self.__output_file = output_file
        self.__initialize_process_state()
        for line in self.__input_file:
            self.__line_no += 1
            stripped_line = line.strip()
            self.__logger.debug("stripped_line %i = %s" % (self.__line_no, stripped_line, ))
            # TODO apply state design pattern?
            self.__write_line = False
            if stripped_line.startswith("//MANUAL_INCLUDES"):
                raise ManualProcessingException()
            if (not self.__comment_line(line, stripped_line)) and \
                (not self.__empty_line(line, stripped_line)) and \
                (not self.__implementation_file or not self.__preamble_line(line, stripped_line)) and \
                (not self.__include_guard(line, stripped_line)):
                self.__write_line = True
                # copy comments up to include guard
                # repair include guard
                # copy further comments
                # on first non-comment, output new include statements
                
                self.__output_include_statements()
                    
                # skip over all include statements in input (with defined exceptions: oem headers that have not been analyzed)
                # output rest of file
                # end with end of include guarded area (#endif)
                # warn if something unusual is found (regular include guard at a later point, include statement after first other statement, ...)
            if self.__write_line:
                self.__print_no_end_and_flush(line)
        self.__print_flush()
        if self.__if_level > 0:
            self.__error("Open #if at end of file, internal error")
        if not self.__includes_written:
            self.__warning("Input file is essentially empty")
            self.__output_include_statements()
        if not self.__include_guard_present and not self.__implementation_file:
            for line in self.__include_guard_normalizer.create_footer(path=self.__repair_path):
                    self.__print(line)
        return (included_paths, dict())

class DefaultSymbolScanner(SymbolScanner):
    """
    A simple, heuristic implementation of SymbolScanner, which does not make use of the preprocessor.

    Symbols that occur in a forward declaration are ignored.
    """
        
    def __init__(self):
        SymbolScanner.__init__(self)
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def scan_for_symbols(self, lines, search_keywords):
        # TODO skip over comments
        found_all = set()
        for line in lines:
            found_this = set()
            ignore_this = set()
            for (object_id, symbol) in search_keywords.iteritems():
                # Anscheinend ist es gar nicht notwendig, forward declarations zu �bergehen, 
                # da diese (bei CAST) gar nicht als referenzierte Symbole gelten. Sicherheitshalber bleibt 
                # dies aber mal drin.
                if line.startswith("//MANUAL_INCLUDES"):
                    raise ManualProcessingException()
                elif re.search(r'(class|struct|union)\s+%s\s*;' % (re.escape(symbol), ), line):
                    self.__logger.debug("Forward declaration found for %s, ignoring" % (symbol, ))
                    ignore_this.add(object_id)
                elif re.search(r'\b%s\b' % re.escape(symbol), line):
                    self.__logger.debug("found symbol %s" % (symbol, ))
                    found_this.add(object_id)
            for object_id in found_this | ignore_this:
                del search_keywords[object_id]
            found_all |= found_this
        return found_all
    
class OnePhaseRequiredIncludeFilesCalculator(RequiredIncludeFilesCalculator):
    
    
    def __init__(self, include_map, is_implementation_file_func, resource_resolver):
        self.__include_map = include_map
        self.__is_implementation_file_func = is_implementation_file_func
        self.__resource_resolver = resource_resolver
        self.__logger = logging.getLogger(self.__class__.__module__)

    def calculate_required_include_files(self, project_file):
        """
        
        @param project_file:
        @type project_file: ProjectFile
        """
        path = project_file.get_path_rel_to_root_unix()
        if path in self.__include_map:
            return self.__include_map[path]
        else:
            self.__logger.warning("No required include files for %s" % project_file)
            return []

class TwoPhaseRequiredIncludeFilesCalculator(RequiredIncludeFilesCalculator, FactoryRequired):
    """
    An implementation of RequiredIncludeFilesCalculator which works in two (or three) phases:
    First, determine the symbols that are used (using a UsedSymbolsLister), then map 
    these symbols to the headers they are defined in (using a HeaderLister). In case of a header file,
    the contents of the file are scanned using a DefaultSymbolScanner to ignore symbols that are not
    referenced or only in a forward declaration. 
    """
    def __init__(self, used_symbols_lister, header_lister, is_implementation_file_func, resource_resolver):
        # TODO resource resolver is never used!
        assert isinstance_or_duck(header_lister, HeaderLister)
        assert isinstance_or_duck(used_symbols_lister, UsedSymbolsLister)
        self.__used_symbols_lister = used_symbols_lister
        self.__header_lister = header_lister
        self.__is_implementation_file = is_implementation_file_func
        self.__symbol_scanner = DefaultSymbolScanner()
        self.__resource_resolver = resource_resolver
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def _find_used_symbol_ids(self, search_keywords, project_file):        
        if self.__is_implementation_file(project_file.get_path_rel_to_root_unix()):
            # implementation file
            object_ids = search_keywords.keys()
        else:
            # header file
            with project_file.get_resource().open() as input_lines:
                object_ids = self.__symbol_scanner.scan_for_symbols(input_lines, search_keywords)
        return object_ids

    def calculate_required_include_files(self, project_file):
        # TODO merge repair_path_rel_to_root_unix and input_path_local         
        symbol_candidates = self.__used_symbols_lister.get_symbol_candidates(project_file)
        object_ids = self._find_used_symbol_ids(symbol_candidates, project_file)
        self.__logger.debug("object_ids = %s" % (",".join(imap(str, object_ids))))
        required_include_files = self.__header_lister. \
                        map_symbol_ids_to_headers(object_ids, 
                                                  project_file)
        return required_include_files

if __name__ == "__main__":
    import doctest
    doctest.testmod()
