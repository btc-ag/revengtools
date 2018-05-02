'''
Created on 05.02.2012

@author: SIGIESEC
'''

from commons.configurator import Configurator
from cpp.incl_deps.include_deps_if import FileIncludeDepsSupply
from cpp.incl_deps.include_deps_util import FileIncludeDepsListerFacade
from optparse import OptionParser
import logging
import sys

config_file_include_deps = FileIncludeDepsSupply()

def __create_option_parser():
    parser = OptionParser(usage="usage: %prog [options] input_path(s)", description="Shows include dependencies for given input files.")
#parser.add_option("-F", "--files-from-stdin", action="store_true", dest="csproj_from_stdin", default=False, help="Read list of .csproj from stdin")
#parser.add_option("-f", "--files-from-cmdline", action="store_true", dest="csproj_from_stdin", help="Read list of .csproj from command line (default)")
    #parser.add_option("-r", "--recursive", action="store_true", dest="recursive", help="Recurse into subdirectories")
    parser.add_option("-c", "--closure", action="store_true", dest="closure", help="Traverse into transitive closure of all included files")
    parser.add_option("-s", "--sort", action="store_true", dest="sort", help="Sort list of output files.")
#    overriding_options = OptionGroup(parser, "Overrriding options", "These options override configuration defaults.")
#    overriding_options.add_option("-S", "--source-dir", action="store", dest="source_dir", help="Override default source base directory")
#    parser.add_option_group(overriding_options)
    return parser


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    Configurator().default()
    
    parser = __create_option_parser()
    (options, args) = parser.parse_args()
    logger = logging.getLogger(main.__module__)

    if len(args) > 0:
        for target in FileIncludeDepsListerFacade(include_deps_supply=config_file_include_deps, 
                                                  closure=options.closure, 
                                                  sort=options.sort).required_files(args):
            print target
    else:
        print >>sys.stderr, "No valid input files specified!"
        sys.exit(1)

if __name__ == "__main__":
    main()
