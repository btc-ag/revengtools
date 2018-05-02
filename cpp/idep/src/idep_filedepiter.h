// idep_filedepiter.h
#ifndef INCLUDED_IDEP_FILEDEPITER
#define INCLUDED_IDEP_FILEDEPITER

// This component defines 1 fully insulated iterator class:
//   idep_FileDepIter: iterate over the header files included by a file.


class idep_FileDepIter_i;
class idep_FileDepIter {
    idep_FileDepIter_i *d_this;
    
  private:
    idep_FileDepIter(const idep_FileDepIter&);            // not implemented
    idep_FileDepIter& operator=(const idep_FileDepIter&); // not implemented

  public:
    // CREATORS
    idep_FileDepIter(const char *fileName);
        // Create a compile-time dependency iterator for the specified file.
        // The filenames in preprocessor include directives will be presented
        // in the order in which they appear in the file.  Dependencies that
        // are conditionally compiled or commented out with multi-line 
        // /* ... */ comments will none-the-less be returned by this iterator.

    ~idep_FileDepIter();

    // MANIPULATORS
    void reset();
        // Return to the first dependency in the file (if one exists).

    void operator++();
        // Advance to next dependency in the file.  The behavior of this 
        // function is undefined if the iteration state is invalid. 

    // ACCESSORS
    int isValidFile() const;
        // Return non-zero if the specified file is valid/readable; else 0.

    operator const void *() const;
        // Return non-zero if the current iteration state (i.e., dependency)
        // is valid; else 0.  Note that this function will correctly return 0 
        // if the file itself is not valid.

    const char *operator()() const;
        // Return the name of current file on which this file depends.
        // If the iteration state is not valid, 0 is returned.
};

#endif

