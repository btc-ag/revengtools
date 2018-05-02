// idep_aliastable.h
#ifndef INCLUDED_IDEP_ALIASTABLE
#define INCLUDED_IDEP_ALIASTABLE

// This leaf component defines 2 classes:
//       idep_AliasTable: supports efficient (hashed) name to name mapping
//   idep_AliasTableIter: iterate through the collection of name mappings

#include <iosfwd>

class idep_AliasTableLink;
class idep_AliasTableIter;

class idep_AliasTable {
    idep_AliasTableLink **d_table_p;            // hash table
    int d_size;                                 // size of hash table
    friend class idep_AliasTableIter;

  private:
    idep_AliasTable(const idep_AliasTable&);            // not implemented
    idep_AliasTable& operator=(const idep_AliasTable&); // not implemented

  public:
    // CREATORS
    idep_AliasTable(int sizeHint = 0); 
        // Create a new table; optionally specify expected number of entries.
    ~idep_AliasTable();                                       

    // MANIPULATORS
    int add(const char *alias, const char *originalName);
        // Add an alias to the table.  Returns 0 on success, 1 if the
        // identical alias/originalName was already present, -1 if an
        // alias with a different original name was present.  Under
        // no circumstances will an alias be overwritten with a new
        // original name.  (Neither alias nor originalName may be 0.)

    // ACCESSORS
    const char *lookup(const char *alias) const;
        // Return the original name if the alias exists, else 0.
};
        
std::ostream& operator<<(std::ostream& output, const idep_AliasTable& table);
    // Write the entire logical contents of the specified alias table in some 
    // reasonable format to the specified output stream.
        
class idep_AliasTableIter {
    const idep_AliasTable& d_table;     // reference to const alias table
    idep_AliasTableLink *d_link_p;      // ptr to current link in table 
    int d_index;                        // index of current slot

  private:
    idep_AliasTableIter(const idep_AliasTableIter&);            // not impl.
    idep_AliasTableIter& operator=(const idep_AliasTableIter&); // not impl.

  public:
    // CREATORS
    idep_AliasTableIter(const idep_AliasTable& table);
        // Create an iterator for the specified table.
    ~idep_AliasTableIter();

    // MANIPULATORS
    void reset();
        // Reset this iterator to the start of the iteration.

    void operator++();
        // Advance state of iteration to next alias/originalName pair.

    // ACCESSORS
    operator const void *() const;
        // Return non-zero if current element is valid; else 0.

    const char *alias() const;
        // Return current alias name.

    const char *originalName() const;
        // Return the (original) name corresponding to current alias name. 
};

#endif


