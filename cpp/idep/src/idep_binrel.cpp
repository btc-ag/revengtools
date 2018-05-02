// idep_binrel.c
#include "idep_binrel.h"

#include <cstring>     // memcpy() memset() memcmp()
#include <iostream>
#include <cassert>

using namespace std;

// IMPLEMENTATION NOTE: MEMORY LAYOUT
// +---------+          +---------+             +---+---+---+---+
// |         |--------->|         |------------>|   |   |   |   |
// +---------+          +---------+             +---+---+---+---+
//    char**            |         |------------>|   |   |   |   |
//                      +---------+             +---+---+---+---+
//                      |         |------------>|   |   |   |   |
//                      +---------+             +---+---+---+---+
//                      |         |------------>|   |   |   |   |
//                      +---------+             +---+---+---+---+
//                      char*[size]             contiguous memory
//                                              char[size * size]

                // -*-*-*- static functions -*-*-*-

enum { START_SIZE = 1, GROW_FACTOR = 2 };

static void clean(char **p) 
{
    delete [] *p;               // only one 2-d block is allocated
    delete [] p;                // delete single block  
}

static char **alloc(int size) 
{
    register int s = size;
    char **rel = new char *[s];
    register char *p = new char[s * s];
    for (register int i = 0; i < s; ++i, p += s) {
        rel[i] = p;
    }
    return rel;
}

static void clear(char *const *rel, int size) 
{
    memset(*rel, 0, size * size);
}

static void copy(char **left, const char *const *right, int size)
{
    memcpy(*left, *right, size * size);
}

                // -*-*-*- private functions -*-*-*-

void idep_BinRel::grow()
{
    int newSize = d_size * GROW_FACTOR;
    char **tmp = d_rel_p;
    d_rel_p = alloc(newSize);
    clear(d_rel_p, newSize);

    for (int i = 0; i < d_size; ++i) {
        memcpy(d_rel_p[i], tmp[i], d_size);
    }

    d_size = newSize;
    clean(tmp);
}

void idep_BinRel::compress()
{
    if (d_size > d_length && d_length > 0) {
        d_size = d_length;
        char **tmp = d_rel_p;
        d_rel_p = alloc(d_size);
        clear(d_rel_p, d_size);
        for (int i = 0; i < d_size; ++i) {
            memcpy(d_rel_p[i], tmp[i], d_size);
        }
        clean(tmp);
    }
}

                // -*-*-*- public functions -*-*-*-

idep_BinRel::idep_BinRel(int initialEntries, int maxEntriesHint) 
: d_size(maxEntriesHint > 0 ? maxEntriesHint : START_SIZE) 
, d_length(initialEntries > 0 ? initialEntries : 0)
{
    if (d_size < d_length) {
        d_size = d_length;
    }
    d_rel_p = alloc(d_size);
    clear(d_rel_p, d_size);
}

idep_BinRel::idep_BinRel(const idep_BinRel& rel) 
: d_size(rel.d_size)
, d_length(rel.d_length)
, d_rel_p(alloc(rel.d_size))
{ 
    ::copy(d_rel_p, rel.d_rel_p, d_size);
}

idep_BinRel& idep_BinRel::operator=(const idep_BinRel& rel) 
{  
    if (&rel != this) {
        if (d_size != rel.d_size) { 
            clean(d_rel_p);
            d_size = rel.d_size;
            d_rel_p = alloc(d_size);
        }
        ::copy(d_rel_p, rel.d_rel_p, d_size);
        d_length = rel.d_length;
    }
    return *this;
}

idep_BinRel::~idep_BinRel() 
{
    clean(d_rel_p);
}

int idep_BinRel::cmp(const idep_BinRel& rel) const
{
    enum { SAME = 0, DIFFERENT = 1 };

    if (d_length != rel.d_length) {
        return DIFFERENT;
    }

    if (d_size == rel.d_size && 
                            memcmp(*d_rel_p, *rel.d_rel_p, d_size * d_size)) {
        return DIFFERENT;
    }

    for (int i = 0; i < d_length; ++i) {
        if (memcmp(d_rel_p[i], rel.d_rel_p[i], d_length)) {
            return DIFFERENT;
        }
    }

    return SAME;
}

void idep_BinRel::warshall(int bit) 
{
    // DEFINITION: Transitive Closure
    //
    // Given: R is a relation (matrix) indicating transitions in 1 step.
    // TransitiveClosure(R) = R + R^2 + R^3 + ... + R^N 
    //      where N is the number of rows and columns in the square matrix R.
    //
    // Warshall's algorithm to construct the transitive closure:
    // foreach index k
    //     foreach row i
    //         foreach column j
    //             if (A[i][k] && A[k][j]) 
    //                 A[i][j] = 1;      
    // 
    // See Aho, Hopcroft, & Ullman, "Data Structures And Algorithms,"
    // Addison-Wesley, Reading MA, pp. 212-213.  Also see, Warshall, S. [1962].
    // "A theorem on Boolean matrices," Journal of the ACM, 9:1, pp. 11-12.

    compress();
    assert(d_size == d_length || 0 == d_length);

    register const int VALUE = !!bit;
    register int s = d_length;  // size and length are the same or length is 0
    register char *top_row = d_rel_p[0] + s * s;

    for (int k = 0; k < s; ++k) {
        register char *row_k = d_rel_p[k];
        for (register char *row_r = d_rel_p[0]; row_r < top_row; row_r += s) {
            if (!row_r[k]) { 
                continue;                   // huge optimization
            }
            if (d_rel_p[k] == row_r) {  
                continue;                   // note: ignore self dependency
            }
            for (register int c = 0; c < s; ++c) {
                if (row_k[c] && row_r[k]) { // note: both conditions are needed
                                            // in reverse (consider k == c).
                    if (c != k) {           // note: ignore self dependency
                        row_r[c] = VALUE;   
                    }
                }
            }
        }
    }
}

void idep_BinRel::makeTransitive() 
{
    warshall(1);
}

void idep_BinRel::makeNonTransitive() 
{
    warshall(0);
    // make non-reflexive too -- i.e., subtract the identity matrix.
    for (int i = 0; i < length(); ++i) {
        d_rel_p[i][i] = 0;
    }
}

                // -*-*-*- free operators -*-*-*-

ostream& operator<<(ostream& o, const idep_BinRel& rel) 
{
    int r, c;
    const int GAP_GRID = 10;
    const char *SP = rel.length() < 30 ? " " : "";
    for (r = 0; r < rel.length(); ++r) {
        if (r && 0 == r % GAP_GRID) { 
            o << endl;
        }
        
        for (c = 0; c < rel.length(); ++c) {
            if (c && 0 == c % GAP_GRID) { 
                o << ' ' << SP;
            }
            o << (rel.get(r,c) ? '1' : '_') << SP;
        }
        o << endl;
    }
    return o;
}

