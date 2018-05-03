// ldep.c
#include "idep_linkdep.h"
#include <iostream>

using namespace std;

// This file contains a main program to exercise the idep_linkdep component.

#define NL "\n"
static const char *help()
{
return NL
"ldep: Analyze the link-time dependencies among a collection of components." NL
""                                                                           NL
"  The following command line interface is supported:"                       NL
""                                                                           NL
"    ldep [-U<dir>] [-u<un>] [-a<aliases>] [-d<deps>] [-l|-L] [-x|-X] [-s]"  NL
""                                                                           NL
"      -U<dir>     Specify directory not to group as a package."             NL
"      -u<un>      Specify file containing directories not to group."        NL
"      -a<aliases> Specify file containg list of component name aliases."    NL
"      -d<deps>    Specify file containg list of compile-time dependencies." NL
"      -l          Long listing: provide non-redundant list of dependencies."NL
"      -L          Long listing: provide complete list of dependencies."     NL
"      -x          Suppress printing any alias/unalias information."         NL
"      -X          Suppress printing all but the levelized component names." NL
"      -s          Do _not_ remove suffixes; consider each file separately." NL
""                                                                           NL
"    This command takes no arguments.  The dependencies themselves will"     NL
"    come from standard input unless the -d option has been invoked."        NL
""                                                                           NL
"  TYPICAL USAGE:"                                                           NL
""                                                                           NL
"    ldep -aaliases -ddependencies"                                          NL
NL;
}

static enum { IOERROR = -1, SUCCESS = 0, DESIGN_ERROR = 1 } s_status = SUCCESS;

static ostream& err() 
{
    s_status = IOERROR;
    return cerr << "Error: ";
}

static int missing(const char *argName, char option) 
{  
    err() << "missing `" << argName << "' argument for -" 
          << option << " option." << endl;
    return s_status;
}

static int extra(const char *text, char option) 
{  
    err() << "extra text \"" << text << "\" encountered after -" 
          << option << " option." << endl;
    return s_status;
}

static int unreadable(const char *dirFile, char option) 
{  
    err() << "unable to read \"" << dirFile << "\" for -" 
          << option << " option." << endl;
    return s_status;
}

static int incorrect(const char *file, char option) 
{  
    err() << "file \"" << file << "\" contained invalid contents for -" 
          << option << " option." << endl;
    return s_status;
}

static const char *getArg(int *i, int argc, char *argv[])
{
    return 0 != argv[*i][2] ? argv[*i] + 2 :
           ++*i >= argc || '-' == argv[*i][0] ? "" : argv[*i];
}

main (int argc, char *argv[]) 
{
    int fileFlag = 0;        // -d<file> sets this to 1
    int longListingFlag = 0; // both -l and -L set this to 1
    int canonicalFlag = 1;   // -L sets this to 0 and -l sets it back to 1
    int suffixFlag = 1;      // -s sets this to 1
    int suppression = 0;     // -x sets this to 1; -X sets it to 2.
    idep_LinkDep environment;
    for (int i = 1; i < argc; ++i) {
        const char *word = argv[i];
        if  ('-' == word[0]) {
            char option = word[1];
            switch(option) {
              case 'U': {
                const char *arg = getArg(&i, argc, argv);
                if (!*arg) {
                    return missing("dir", option);
                }
                environment.addUnaliasDirectory(arg);
              } break;
              case 'u': {
                const char *arg = getArg(&i, argc, argv);
                if (!*arg) {
                    return missing("file", option);
                }
                if (0 != environment.readUnaliasDirectories(arg)) {
                    return unreadable(arg, option);
                }
              } break;
              case 'a': {
                const char *arg = getArg(&i, argc, argv);
                if (!*arg) {
                    return missing("file", option);
                }
                int s = environment.readAliases(cerr, arg);
                if (s < 0) {
                    return unreadable(arg, option);
                }
                if (s > 0) {
                    return incorrect(arg, option);
                }
              } break;
              case 'd': {
                const char *arg = getArg(&i, argc, argv);
                if (!*arg) {
                    return missing("file", option);
                }
                environment.addDependencyFile(arg);
                fileFlag = 1;
              } break;
              case 'l': {
                const char *arg = word + 2;
                if (*arg) {
                    return extra(arg, option);
                }
                canonicalFlag = 1;
                longListingFlag = 1;
              } break;
              case 'L': {
                const char *arg = word + 2;
                if (*arg) {
                    return extra(arg, option);
                }
                longListingFlag = 1;
                canonicalFlag = 0;
              } break;
              case 's': {
                const char *arg = word + 2;
                if (*arg) {
                    return extra(arg, option);
                }
                suffixFlag = 0;
              } break;
              case 'x': {
                const char *arg = word + 2;
                if (*arg) {
                    return extra(arg, option);
                }
                suppression = 1;
              } break;
              case 'X': {
                const char *arg = word + 2;
                if (*arg) {
                    return extra(arg, option);
                }
                suppression = 2;
              } break;
              default: {
                 err() << "unknown option \"" << word << "\"." << endl 
                       << help(); 
                 return s_status;
              } break;
            }
        }
        else {
             err() << "illegal argument \"" << word << "\"." << endl 
                   << help(); 
             return s_status;
        }
    }

    if (!fileFlag) {
        environment.addDependencyFile(""); // "" is synonym for standard input
    }

    int result = environment.calculate(cerr, canonicalFlag, suffixFlag);

    s_status = result < 0 ? IOERROR : result > 0 ? DESIGN_ERROR : SUCCESS; 

    if (s_status >= 0) {
        if (0 == suppression) {
            environment.printAliases(cout);
            environment.printUnaliases(cout);
        }
        environment.printCycles(cerr);
        environment.printLevels(cout, longListingFlag, suppression >= 2);
        if (suppression <= 1) {
            environment.printSummary(cout);
        }
    }

    return s_status;
}

