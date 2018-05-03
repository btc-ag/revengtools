#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from commons.core_util import CollectionTools
from cpp.cpp_util import regular_guard, is_ms_generated_guard
import csv
import logging
import os.path
import sys
#from commons.configurator import Configurator


def check_include_guards(files_to_guards, path_name, guard):
    missing = 0
    irregular = 0
    correct = 0
    pragma_once = 0
    ms_generated = 0
    for path_name, guard in files_to_guards.iteritems():
        file_name = os.path.basename(path_name)
        expectedGuard = regular_guard(file_name)
        if len(guard) == 0:
            print ("add:%s" % (path_name, ))
            missing += 1
        elif guard == "#pragma once":
            correct += 1
            pragma_once += 1
        elif guard != expectedGuard:
            print ("change:%s:%s:%s" % (path_name, guard, expectedGuard))
            irregular += 1
            if is_ms_generated_guard(file_name, guard):
                ms_generated += 1
        else:
            correct += 1
    
    return correct, pragma_once, missing, irregular, ms_generated, guard

def main():
    logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
    #Configurator().default()
        
    if (len(sys.argv) < 2):
        print("Call: %s <output from FindIncludeGuards.sh>" % (sys.argv[0], ))
        exit()
        
    # TODO move i
        
    files_to_guards = dict([(path_name, guard) for (path_name, guard) in csv.reader(open(sys.argv[1]), delimiter=':')])
    #duplicates = CollectionTools.find_duplicates(files_to_guards.itervalues(), lambda x: len(x)==0 or x == '#pragma once')
    duplicates_dict = CollectionTools.find_duplicate_values(files_to_guards.iteritems(), lambda x: len(x)==0 or x == '#pragma once')
    
    correct, pragma_once, missing, irregular, ms_generated, guard = check_include_guards(files_to_guards, path_name, guard)
            
    print("%i correct (%i of which using #pragma once before or without a guard), %i missing guard or malformed structure, %i irregular (%i of which are MS generated)" % (correct,pragma_once,missing,irregular,ms_generated))
    #print("%i duplicates: %s" % (len(duplicates), ",".join(duplicates)))
    print("%i duplicates" % (len(duplicates_dict)))
    for guard in sorted(duplicates_dict.keys()):
        print("%s:%s" % (guard, ",".join(sorted(duplicates_dict[guard]))))

if __name__ == "__main__":
    main()
