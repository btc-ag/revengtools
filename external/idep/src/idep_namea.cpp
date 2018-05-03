// idep_namea.c
#include "idep_namearray.h"

#include <cstring>     // strlen()
#include <iostream>
#include <cassert>

using namespace std;

                // -*-*-*- static functions -*-*-*-
 
enum { START_SIZE = 1, GROW_FACTOR = 2 };
 
static char *newStrCpy(const char *oldStr)
{
    int size = strlen(oldStr) + 1;
    char *newStr = new char[size];
    assert(newStr);
    memcpy(newStr, oldStr, size);
    return newStr;
}
 
                // -*-*-*- idep_NameArray -*-*-*-
 
idep_NameArray::idep_NameArray(int maxEntriesHint)
: d_size(maxEntriesHint > 0 ? maxEntriesHint : START_SIZE)
, d_length(0)
{
    d_array_p = new char *[d_size];
} 

idep_NameArray::~idep_NameArray()
{                                     
    for (int i = 0; i < d_length; ++i) {
        delete [] d_array_p[i];
    }
    delete [] d_array_p;
}

int idep_NameArray::append(const char *name) 
{
    if (d_length >= d_size) {
        int oldSize = d_size;
        d_size *= GROW_FACTOR;
        char **tmp = d_array_p;
        d_array_p = new char *[d_size];
        assert (d_array_p);
        memcpy (d_array_p, tmp, oldSize * sizeof *d_array_p);
        delete [] tmp;
    }
    assert(d_length < d_size);
    d_array_p[d_length++] = newStrCpy(name);
    return d_length - 1;
}

const char *idep_NameArray::operator[] (int i) const
{
    return i < d_length && i >= 0 ? d_array_p[i] : 0;
}

int idep_NameArray::length() const
{
    return d_length;
};

ostream& operator<<(ostream& out, const idep_NameArray& array) 
{
    int fieldWidth = 10;
    int maxIndex = array.length() - 1;
    assert (sizeof (long int) >= 4);
    long int x = 1000 * 1000 * 1000;    // requires 4-byte integer.
    while (fieldWidth > 1 && 0 == maxIndex / x) {
        --fieldWidth;  
        x /= 10;
    }

    for (int i = 0; i < array.length(); ++i) {
        out.width(fieldWidth);
        out << i << ". " << array[i] << endl;
    }

    return out;
}

