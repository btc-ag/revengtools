from __future__ import with_statement
from commons.metric_util import PlainLinesOfCodeMetric
from csharp.csproj_parser import (CSProjParser, 
     CSProjCheckerDefault, CSProjCheckerTools)
from xml.parsers.expat import ExpatError
import logging
import os.path
import sys
    
class CSProjMakeTableProcessor(object):
    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger()
    
    def parse_file(self, filename, filter_pred):
        try:
            parser = CSProjParser(open(os.path.abspath(filename)))
            checker = CSProjCheckerDefault(parser)
            CSProjCheckerTools.log_irregularities(self.__logger, source=parser.get_filename(), irregularities=checker.get_irregularities())
            
            if not checker.has_errors():
                from_proj = parser.get_assembly_name()
                if filter_pred(from_proj):
                    source_files = list(parser.get_source_files())
                    print "| *%s* | %i files |" % (from_proj, len(source_files))
                    for source_file in source_files:
                        basename = os.path.basename(source_file.name())
                        if basename not in ["AssemblyInfo.cs", ]:
                            print "| %s | %i LOC |" % (basename, PlainLinesOfCodeMetric().apply_metric(open(source_file.name())))
                    
        except ExpatError, exc:
            self.__logger.error("Unparsable file %s: %s" % (filename, exc))
            
    def parse_files(self, filenames, selected_assemblies):
        for filename in filenames:
            self.parse_file(filename, lambda x: x in selected_assemblies if selected_assemblies else lambda x: True)



if __name__ == "__main__":
    from optparse import OptionParser
    logging.basicConfig(level=logging.DEBUG)
    parser = OptionParser()
    #parser.add_option("-f", "--files", dest="csproj_files", help="Input .csproj files")    
    parser.add_option("-F", "--files-from-stdin", action="store_true", dest="csproj_from_stdin", default=False, help="Read list of .csproj from stdin")
    parser.add_option("-f", "--files-from-cmdline", action="store_true", dest="csproj_from_stdin", help="Read list of .csproj from command line (default)")
    parser.add_option("-s", "--select", action="store", dest="assembly_list", help="Comma-separated list of assembly names to select")
    (options, args) = parser.parse_args()
    if options.assembly_list:
        selected_assemblies = options.assembly_list.split(",")
    else:
        selected_assemblies=None
    if not options.csproj_from_stdin and len(args) > 0:
        CSProjMakeTableProcessor().parse_files(args, selected_assemblies=selected_assemblies)
    elif options.csproj_from_stdin:
        CSProjMakeTableProcessor().parse_files((x.strip() for x in sys.stdin), selected_assemblies=selected_assemblies)
    else:
        parser.print_help()
