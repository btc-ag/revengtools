// idep_binrel.h
#ifndef INCLUDED_IDEP_BINREL
#define INCLUDED_IDEP_BINREL

// This leaf component defines 1 class:
//   idep_BinRel: Square matrix of bits with transitive closure capability.

#include <iosfwd>

class idep_BinRel {
    char **d_rel_p;     // array of pointers into a contiguous byte array
    int d_size;         // physical size of array
    int d_length;       // logical size of array

  private:
    void grow();
      // Increase the physical size of this relation.

    void compress();
      // Make the physical size same as Logical size (unless that is 0).

    void warshall(int bit);
      // Perform Warshall's algorithm either forward or backward. 

  public:
    // CREATORS
    idep_BinRel(int initialEntries = 0, int maxEntriesHint = 0);
        // Create a binary relation that can be extended as needed.
        // By default, the initial number of entires in the relation
        // is 0.  If the final number of entries is known and is not
        // the same as initialEntries, that value may optionally be
        // specified as the second argument (as a "hint").

    idep_BinRel(const idep_BinRel& rel);
    ~idep_BinRel();

    // MANIPULATORS
    idep_BinRel& operator=(const idep_BinRel& rel);

    void set(int row, int col, int bit);
        // Set the specified row/col of this relation to the specified 
        // binary value.

    void set(int row, int col);
        // Set the specified row/col of this relation to 1.

    void clr(int row, int col);
        // Set specified row/col of this relation to 0.

    void makeTransitive();
        // Apply Warshall's algorithm to this relation.  The result is the
        // reflexive transitive closure of the original relation.

    void makeNonTransitive();
        // Remove all redundant relationships such that the transitive
        // closure would be left unaffected.  In cases where there is
        // a cyclic dependency, the solution is not unique.  To work 
        // properly, the relation must already be fully transitive 
        // (see makeTransitive).

    int appendEntry();
        // Append an entry to this relation and return its integer index.
        // The logical size is increased by 1 with all new entries 0'ed.

    // ACCESSORS
    int get(int row, int col) const;
        // Get the boolean value at the specified row/col of this relation.

    int cmp(const idep_BinRel& rel) const;
        // Return 0 if and only if the specified relation has the same
        // length and logical values as this relation.

    int length() const;
        // Return number of rows and columns in this relation.  The length
        // represents the cardinality of the set on which this relation is
        // defined.
};

std::ostream& operator<<(std::ostream& out, const idep_BinRel& rel);
   // Output this binary relation in row/column format with the upper left 
   // corner as the origin to the specified output stream (out).

int operator==(const idep_BinRel& left, const idep_BinRel& right);
   // Return 1 if two relations are equal, and 0 otherwise (see cmp).

int operator!=(const idep_BinRel& left, const idep_BinRel& right);
   // Return 1 if two relations are not equal, and 0 otherwise (see cmp).


// #########################################################################
// The following consists of inline function definitions for this component. 
// #########################################################################

inline
int idep_BinRel::appendEntry() 
{
    if (d_length >= d_size) {
        grow();
    }
    return d_length++;
}

inline
void idep_BinRel::set(int row, int col, int bit) 
{
    d_rel_p[row][col] = !!bit;
}

inline
void idep_BinRel::set(int row, int col) 
{
    d_rel_p[row][col] = 1;
}

inline
void idep_BinRel::clr(int row, int col) 
{
    d_rel_p[row][col] = 0;
}

inline
int idep_BinRel::get(int row, int col) const
{
    return d_rel_p[row][col];
}

inline
int idep_BinRel::length() const
{
    return d_length;
}

inline
int operator==(const idep_BinRel& left, const idep_BinRel& right) 
{
    return left.cmp(right) == 0;
}

inline
int operator!=(const idep_BinRel& left, const idep_BinRel& right) 
{
    return left.cmp(right) != 0;
}

#endif

