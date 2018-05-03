// idep_aliasutil.h
#ifndef INCLUDED_IDEP_ALIASUTIL
#define INCLUDED_IDEP_ALIASUTIL

// This component defines 1 procedural utility class:
//   idep_AliasUtil: load an alias table with information read from a file

#include <iosfwd>

class idep_AliasTable;

struct idep_AliasUtil {
    static int readAliases(idep_AliasTable *table, std::ostream& err, std::istream& in,
                                                       const char *inputName);
    static int readAliases(idep_AliasTable *table, std::ostream& err, 
                                                       const char *file);
        // Read a description of aliases from a specified stream or file 
        // and load this information into the specified alias table.
        // A contiguous sequence of non-whitespace characters is treated
        // as a name.  The first name on a line represents the "to" name
        // the rest represent "from" names.  If a single name appears on the 
        // first line of a definition, the list is delimited by a blank line.
        // Any token beginning with a pound ('#') character will be ignored
        // as will all subsequent tokens until the end of the current line.
        //
        //   # this is just a comment
        //   a b c #d e f               # b -> a; c -> a   
        //   d e                        # e -> d
        //   f                          
        //   g h                        # g -> f; h -> f
        //   i                          # i -> f
        //
        //   j k                        # k -> j 
        //
        // A line can be continued by preceding the newline ('\n') 
        // with a backslash ('\\') as a separate token.  Note that neither 
        // "a\" nor "\# comment" are treated as line continuation.
        //
        //   l \ # line is continued
        //   m n                        # m -> l; n -> l
        //
        //   o                          
        //   p q                        # p -> o; q -> o
        //   \ # just a comment \       
        //   r                          # r -> o
        //
        //   s t \                      # t -> s
        //
        //   u v                        # v -> u
        //
        // A backslash that is not followed by a newline is treated
        // as an identifier.  A warning will be issued in such cases.
        //
        //   \ w                        # w -> \        (warning)
        //   x \ \                      # \ -> x        (warning)
        //   y\                         # y\ -> x
        //   z z \#oops                 # z -> z; \#oops -> z
        // 
        // The read-from-file function returns -1 if the file is not readable.
        // Otherwise both functions return the non-negative number of aliases
        // that where inconsistent with existing alias definitions.  All such
        // errors are also reported explicitly to the specified output stream 
        // (err).
};

#endif

