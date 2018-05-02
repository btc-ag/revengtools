// idep_namearray.h
#ifndef INCLUDED_IDEP_NAMEARRAY
#define INCLUDED_IDEP_NAMEARRAY

// This leaf component defines 1 class:
//   idep_NameDep: extensible array of managed character string names.

#include <iosfwd>

class idep_NameArray {
    char **d_array_p;   // array of dynamically allocated character strings
    int d_size;         // physical size of array
    int d_length;       // logical size of array

  private: 
    idep_NameArray(const idep_NameArray&);              // not implemented
    idep_NameArray& operator=(const idep_NameArray&);   // not implemented

  public:
    // CREATORS
    idep_NameArray(int maxEntriesHint = 0); 
        // Create a variable length array of const character strings.
        // The array will be allocated assuming a maximum expected number
        // of entries specified by the optional maxEntriesHint argument. 
        // By default a fairly small array will be allocated.

    ~idep_NameArray();                                        
        // Destroy this array including its contained copies of string names.

    // MANIPULATORS
    int append(const char *newName);
        // Append a copy of the specified string to the end of the array. 
        // The value of the new index is returned.  No attempt is made to 
        // check for repeated string values.

    // ACCESSORS
    const char *operator[] (int index) const;
        // Return a pointer to the specified string.  Strings are stored at
        // at consecutive non-negative index locations beginning with 0 up
        // to one less than the current length.  If the index is out of range, 
        // a null pointer will be returned.

    int length() const;
        // Return the number of names currently stored in this array.  
};

std::ostream& operator<<(std::ostream& out, const idep_NameArray& array);
    // Print the logical contents of this name array to the specified
    // output stream (out) in some suitable format. 

#endif
        
