// idep_aliasdep.h
#ifndef INCLUDED_IDEP_ALIASDEP
#define INCLUDED_IDEP_ALIASDEP

// This component defines 1 fully insulated wrapper class:
//   idep_AliasDep: environment for creating/verifying filename aliases

#include <iosfwd>

class idep_AliasDep_i;
class idep_AliasDep {
    idep_AliasDep_i *d_this;

  private:
    idep_AliasDep(const idep_AliasDep&);                // not implemented
    idep_AliasDep& operator=(const idep_AliasDep&);     // not implemented

  public:
    // CREATORS
    idep_AliasDep();
    ~idep_AliasDep();

    // MANIPULATORS
    void addIgnoreName(const char *name);
        // Add a name to ignored during processing.  A command-line argument 
        // or -f<filelist> entry matching the specified name will not be 
        // considered during any subsequent analysis.

    int readIgnoreNames(const char *file);
        // Add a list of names to ignore during processing.  This function
        // assumes that each contiguous sequence of non-whitespace characters 
        // represents a name to be ignored.  This function returns 0 unless 
        // the specified file is unreadable or contains non-ascii characters.

    const char *addAlias(const char *aliasName, const char *componentName);
        // Add an alias/component name pair to the set of aliases.  This 
        // function returns 0 on success or a character string containing 
        // a previously corresponding component name for this alias that is 
        // not identical to the one specified here.

    int readAliases(std::ostream& err, const char *file);
        // Read a list of component aliases from the specified file.  Each
        // contiguous sequence of non-whitespace characters represents a name.
        // Names are also arranged into sequences.  The first name in a name
        // sequence represents the actual component name.  Names that follow
        // on the same line (horizontal sequence) or subsequent lines 
        // (vertical sequence) are interpreted as aliases for that component 
        // name.  A horizontal sequence is terminated by a newline ('\n') 
        // unless preceded by a backslash ('\\').  A vertical sequence is 
        // terminated by a blank line.  This function quietly returns 0 on 
        // success.  If the specified file is not readable, this function 
        // quietly returns -1.  If an alias that is inconsistent with a 
        // previously specified alias is encountered, the conflicting aliases 
        // are identified to the err stream.  After parsing is complete, the 
        // number of offending aliases is returned as the value of this 
        // function.

    void addFileName(const char *fileName);  
        // Add the name of a file to be analyzed.  Errors in reading this file
        // will be detected only when a processing operation is invoked.

    int readFileNames(const char *file);  
        // Add a list of file names read from a specified file.  This function 
        // assumes that each contiguous sequence of non-whitespace characters 
        // represents a file name to be added.  The effect is the same as if
        // each file name had been added individually.  This function returns 
        // 0 unless the specified file is unreadable or contains non-ascii 
        // characters.  Errors in reading individual files named there in
        // will be detected only when a processing operation is invoked.

    void inputFileNames();
        // Similar to readFileNames except that input is presumed to come 
        // from <stdin>, which is reset on eof.  No check is done for 
        // non-ascii characters.

    // ACCESSORS
    int unpaired(std::ostream& out, std::ostream& err, int suffixFlag = 1) const;
        // Format a list of unpaired files to the specified output
        // stream (out).  If more than two files have the same root,
        // produce a warning on the error stream (err).  By default
        // suffixes will be included when identifying unpaired files
        // setting this flag to 0 causes only the root names to be 
        // printed and these names to be sorted in a more convenient 
        // order for creating an alias file via editor cut-and-paste.
        // This function returns the number of unpaired files.

    int verify(std::ostream& err) const;
        // Verify that all specified (.c) file dependencies are properly 
        // paired after any aliases are applied.  If a specified file fails 
        // to include its corresponding header file as the first include 
        // directive, an error will be reported to the specified error 
        // stream (err).  If any file cannot be opened, the value returned 
        // by this function is negative.  Otherwise, this function returns
        // the number of files containing missing or misplaced include 
        // directives.  

    int extract(std::ostream& out, std::ostream& err) const;
        // Extract any necessary aliases from the specified set of (.c) files 
        // and format them to the specified output stream (out) assuming that 
        // the corresponding header file is the first include directive in the 
        // specified (.c) file.  If a specified (.c) file contains no include 
        // directives, an error will be reported to the specified error 
        // stream (err).  If the same header is deduced as belonging to more 
        // than a single (.c ) file, a warning message is printed to (err).
        // If any file cannot be opened, the value returned by this function 
        // is negative.  Otherwise, this function returns the number of files 
        // containing no include directives.
};

#endif


