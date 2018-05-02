#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from base.basic_config_if import BasicConfig
from commons.configurator import Configurator
from commons.progress_default import (DefaultProgressListener, 
    CountingProgressListener)
from commons.progress_if import progress_listener_attached_to
from cpp.cpp_if import CppFileConfiguration
from cpp.cpp_util import CppProjectUtil
from cpp.incl_deps.file_transform_facade import CppFileTransformerFactory
from cpp.incl_deps.file_transform_if import FileTransformationModes
from cpp.incl_deps.file_transform_resolver import IncludeCollectorProcessor
from cpp.incl_deps.include_list_generator_wrap import IncludeListGenerator
from cpp.incl_deps.repair_includes_base import BaseFileNormalizer
from cpp.incl_deps.repair_includes_if import RequiredIncludeFilesCalculator
from optparse import OptionParser, OptionGroup
import logging
import os
import sys

class FileRepairProcessorRunnerHelper(object):
    def __init__(self, file_repair_processor):
        self.__file_repair_processor = file_repair_processor
        
    def process_files(self, starting_files):
        # TODO change parameter from plain paths to ProjectFile instances
            #progress_listener = DefaultProgressListener()
        progress_listener = CountingProgressListener()
        with progress_listener_attached_to(self.__file_repair_processor, progress_listener):
            self.__file_repair_processor.process_files(starting_files)
        
        return self.__file_repair_processor.get_statistics_dict()

class FileRepairProcessorRunner(object):
    def __init__(self, output, cpp_file_configuration, basic_config):
        self.__output = output
        self.__logger = logging.getLogger(main.__module__)
        self.__cpp_file_configuration = cpp_file_configuration
        self.__basic_config = basic_config
        self.__file_repair_processor_factory = CppFileTransformerFactory(cpp_file_configuration, basic_config)
    
    @classmethod
    def __create_option_parser(cls):
        parser = OptionParser(usage="usage: %prog [options] input_path(s)", 
                              description="Normalizes include directives in C++ implementation and header files.", 
                              add_help_option=False)
    #parser.add_option("-F", "--files-from-stdin", action="store_true", dest="csproj_from_stdin", default=False, help="Read list of .csproj from stdin")
    #parser.add_option("-f", "--files-from-cmdline", action="store_true", dest="csproj_from_stdin", help="Read list of .csproj from command line (default)")
        parser.add_option("-r", "--recursive", action="store_true", dest="recursive", help="Recurse into subdirectories")
        parser.add_option("-c", "--closure", action="store_true", dest="closure", help="Traverse into transitive closure of all included files")
        parser.add_option("-t", "--target", choices=["inplace", "external"], default="inplace", dest="target", help="Modify files in place (inplace) or write output to external directory tree (external)")
        parser.add_option("-T", "--target-dir", action="store", dest="target_dir", help="The external target directory if target==external")
        parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Debug mode")
        parser.add_option("-N", "--normalize-only", action="store_true", dest="normalize_only", help="Normalize individual include directives only, do not modify include hierarchy.")
        parser.add_option("-L", "--list-includes", action="store_true", dest="list_includes", help="Do not modify files, only list includes.")
        parser.add_option("-I", "--invalidate", action="store_true", dest="invalidate", help="Invalidate all caches.")
        parser.add_option("", "--skip-comments", action="store", dest="skip_comments", help="Skip comments (defaults to True if --list-includes).")
        parser.add_option("-h", "--help", action="store_true", dest="help", help="Print this help and exit.")
        overriding_options = OptionGroup(parser, "Overrriding options", "These options override configuration defaults.")
        overriding_options.add_option("-S", "--source-dir", action="store", dest="source_dir", help="Override default source base directory")
        overriding_options.add_option("-R", "--required-includes", action="store", dest="required_includes", help="CSV file specifying required includes for each CPP file")
        parser.add_option_group(overriding_options)
        return parser
    

    def __log_and_print(self, loglevel, msg):
        self.__logger.log(loglevel, msg)
        print >> self.__output, msg


    def __print_statistics(self, statistics):
        print >> self.__output, "Statistics:"
        for key, value in statistics.iteritems():
            print >> self.__output, "  %s = %s" % (key, value)

    def run(self, argv):
        # TODO abstract from UsedSymbolsLister + SymbolScanner + HeaderLister, instead allow to use directly the  
        # correct list of files to include
        
        # TODO also copy all non-source files to external target directory (when working recursively) 
        
        # Namenskonvention für verschiedene Arten von Pfaden (mit \\ als Seperator, wenn nicht anders angegeben):
        #   Absoluter Server-Pfad: *_path_server
        #   Absoluter lokaler Pfad: *_path_local
        #   Pfad relativ zum Basisverzeichnis (prinsmod) mit / als Separator: *_path_rel_to_root_unix
        #   Pfad relativ zu einer anderen Datei (deprecated)
        #   basename: *_basename
        # (alle Pfade sollten stets mit os.path.normpath normalisiert sein)
        
        # TODO Dateien mit generierter Include-Liste erkennen und Zeitstempel vergleichen
    
        # PRINS-Spezifika:    
        # TODO #pragma pack berücksichtigen!
        # TODO #define INCL_STS_CLIB_* berücksichtigen
        # TODO #include-Liste hinter #pragma warning einfügen 
        # TODO Sonderbehandlung f�r vorhandene .co-Includes.
        # Sind diese nicht eigentlich �berfl�ssig, da es genau eine Datei gibt, die sie einbindet?
        
        # TODO daus.df,antablis.df,auskopip.df enthalten vermutlich zu viele Includes (alle PSM-Includes)
        
        # TODO mssql.df ... ist wohl ein Wrapper um externe Header. Muss wohl nicht gefixt werden.
    
        parser = self.__create_option_parser()
        (options, args) = parser.parse_args(args=argv)
        if options.normalize_only and options.list_includes:
            print >>self.__output, "Cannot use both --normalize-only and --list-includes"
            return 1
        
        if options.normalize_only:
            mode = FileTransformationModes.NormalizeOnly
        elif options.list_includes:
            mode = FileTransformationModes.ListIncludes
        else:
            mode = FileTransformationModes.Repair
    
        local_source_base_dir = options.source_dir if options.source_dir else self.__basic_config.get_local_source_base_dir()
        self.__log_and_print(logging.INFO, "Using source base directory %s" % local_source_base_dir)
        
        
        if options.debug:
            BaseFileNormalizer.debug = True
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            BaseFileNormalizer.debug = False
            #logging.getLogger().setLevel(logging.INFO)
        if len(args) == 0 or options.help:
            print >>self.__output, "No input paths given"
            parser.print_help(file=self.__output)
            return 0
        
        if options.recursive:
            # TODO filelist can be used here too 
            args = CppProjectUtil.scan_project_files(args, local_source_base_dir, self.__cpp_file_configuration, self.__logger)
            self.__logger.debug("Result of file scan: %s" % (args))
            
        if options.target=="inplace" and options.target_dir:
            print >>self.__output, "When using target==inplace, no target directory must be given"
            return 1
            
        if len(args) > 0:
            if mode == FileTransformationModes.Repair:
                if not options.required_includes:
                    required_include_files_calculator_class = Configurator().get_concrete_adapter(RequiredIncludeFilesCalculator)
                else:
                    required_include_files_calculator_class = None
                include_list_generator_factory = IncludeListGenerator
            else:
                required_include_files_calculator_class = None
                include_list_generator_factory = None
            file_repair_processor = self.__file_repair_processor_factory.create_file_repair_processor(local_source_base_dir=local_source_base_dir,
                                                                        target=options.target, 
                                                                        target_dir=options.target_dir, 
                                                                        mode=mode, 
                                                                        required_includes=options.required_includes, 
                                                                        closure=options.closure,
                                                                        invalidate=options.invalidate,
                                                                        required_include_files_calculator_class = required_include_files_calculator_class,
                                                                        include_list_generator_factory=include_list_generator_factory)
            runner = FileRepairProcessorRunnerHelper(file_repair_processor=file_repair_processor)
                
            statistics = runner.process_files(args)
            if options.list_includes:
                assert hasattr(file_repair_processor, "get_include_map")
                include_map_items = file_repair_processor.get_include_map()
                for line in IncludeCollectorProcessor.format_include_map(local_source_base_dir, include_map_items):
                    print line
            self.__print_statistics(statistics)
            #total = reduce(lambda x, y: x+y, statistics)
            #print "Total files: %i" % total
            #print "%i successful, %i skipped, %i with error, %i with unexpected exception" % statistics
        else:
            print >>self.__output, "No valid input files specified!"
            return 1
        
config_basic = BasicConfig()
config_cpp_file_configuration = CppFileConfiguration()
#config_required_include_files_calculator_class = RequiredIncludeFilesCalculator

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    os.environ['LANGUAGE'] = 'cpp'
    Configurator().default()
    
    return FileRepairProcessorRunner(output=sys.stderr,
                                     basic_config=config_basic,
                                     cpp_file_configuration=config_cpp_file_configuration).run(argv=sys.argv[1:])
    
if __name__ == "__main__":
    main()
