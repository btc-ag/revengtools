// cdep.c
#include "idep_compiledep.h"
#include <iostream>

using namespace std;

// This file contains a main program to exercise the idep_compiledep component.

#define NL "\n"
static const char *help() 
{
return NL
"cdep: Extract compile-time dependencies from a collection of files."        NL
""                                                                           NL
"  The following command line interface is supported:"                       NL
""                                                                           NL
"    cdep [-I<dir>] [-i<dirlist>] [-f<filelist>] [-x] <filename>*"           NL
""                                                                           NL
"      -I<dir>      Specify include directory to search."                    NL
"      -i<dirlist>  Specify file containing a list of directories to search."NL
"      -f<filelist> Specify file containing a list of files to process."     NL
"      -x           Do _not_ check recursively for nested includes."         NL
""                                                                           NL
"    Each filename on the command line specifies a file to be considered for"NL
"    processing.  Specifying no arguments indicates that the list of files"  NL
"    is to come from standard input unless the -f option has been invoked."  NL
""                                                                           NL
"  TYPICAL USAGE:"                                                           NL
""                                                                           NL
"    cdep -iincludes *.[ch]"                                                 NL
NL;
}

static enum { IOERROR = -1, GOOD = 0 } s_status = GOOD;

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

static const char *getArg(int *i, int argc, char *argv[]) 
{
    return 0 != argv[*i][2] ? argv[*i] + 2 : 
           ++*i >= argc || '-' == argv[*i][0] ? "" : argv[*i];
}

main (int argc, char *argv[]) 
{
    int argCount = 0;        // record the number of files on the command line
    int fileFlag = 0;        // -f<file> sets this to 1
    int recursionFlag = 1;   // -x sets this to 0
    idep_CompileDep environment;
    for (int i = 1; i < argc; ++i) {
        const char *word = argv[i];
        if  ('-' == word[0]) {
            char option = word[1];
            switch(option) {
              case 'I': {
                const char *arg = getArg(&i, argc, argv);
                if (!*arg) {
                    return missing("dir", option);
                }
                environment.addIncludeDirectory(arg);
              } break;
              case 'i': {
                const char *arg = getArg(&i, argc, argv);
                if (!*arg) {
                    return missing("file", option);
                }
                if (0 != environment.readIncludeDirectories(arg)) {
                    return unreadable(arg, option);
                }
              } break;
              case 'f': {
                const char *arg = getArg(&i, argc, argv);
                if (!*arg) {
                    return missing("file", option);
                }
                if (0 != environment.readRootFiles(arg)) {
                    return unreadable(arg, option);
                }
                fileFlag = 1;
              } break;
              case 'x': {
                const char *arg = getArg(&i, argc, argv);
                if (*arg) {
                    return extra(arg, option);
                }
                recursionFlag = 0;
              } break;
              default: {
                 err() << "unknown option \"" << word << "\"." << endl
                       << help();
                 return s_status;
              } break;
            }
        }
        else {
            ++argCount;
            environment.addRootFile(argv[i]);
        }
    }

    if (!fileFlag && !argCount) {
        environment.inputRootFiles();
    }

    if (environment.calculate(cerr, recursionFlag)) {
         s_status = IOERROR;
    }

    cout << environment;

    return s_status;
}

