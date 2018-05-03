// idep_nimap.c
#include "idep_nameindexmap.h"
#include "idep_namearray.h"

#include <cstring>     // strcmp() 
#include <iostream> 
#include <cassert> 

using namespace std;

                // -*-*-*- static functions -*-*-*-

enum { DEFAULT_TABLE_SIZE = 521 };
enum { BAD_INDEX = -1 };

static unsigned hash(register const char* name) // Note: returns unsigned!
{
    register unsigned sum = 1000003; // 1,000,003 is the 78,498th prime number
    while (*name) {
        sum *= *name++; // integer multiplication is a subroutine on a SPARC
    }
    return sum; // unsigned ensures positive value for use with (%) operator.  
}

                // -*-*-*- idep_NameIndexMapLink -*-*-*-

struct idep_NameIndexMapLink {
    const char *d_name_p;                       // name
    int d_index;                                // index of name
    idep_NameIndexMapLink *d_next_p;            // pointer to next link

    idep_NameIndexMapLink(const char *name, int index, 
                          idep_NameIndexMapLink *d_next_p);
};

idep_NameIndexMapLink::idep_NameIndexMapLink(const char *name, int index, 
                                                idep_NameIndexMapLink *next)
: d_name_p(name)
, d_index(index)
, d_next_p(next)
{
}

static const idep_NameIndexMapLink *find(const idep_NameIndexMapLink *p, 
                                                            const char *name)
{
    while (p && 0 != strcmp(p->d_name_p, name)) {
        p = p->d_next_p;
    }
    return p;
}

                // -*-*-*- idep_NameIndexMap_i -*-*-*-

struct idep_NameIndexMap_i { 
    idep_NameArray d_array;                     // array of names
    idep_NameIndexMapLink **d_table_p;          // hash table of names
    int d_tableSize;                            // size of hash table

    idep_NameIndexMap_i(int size); 
        // create a map representation assuming the specified (max) size

    ~idep_NameIndexMap_i(); 

    idep_NameIndexMapLink *& findSlot(const char *name); 
        // find the appropriate slot for this name

    int insert(idep_NameIndexMapLink *& slot, const char *name);
        // insert name into specified slot
};

idep_NameIndexMap_i::idep_NameIndexMap_i(int size)
: d_array(size)
, d_tableSize(size > 0 ? size : DEFAULT_TABLE_SIZE)
{ 
    d_table_p = new idep_NameIndexMapLink *[d_tableSize];
    assert(d_table_p);
    memset(d_table_p, 0, d_tableSize * sizeof *d_table_p);
}

idep_NameIndexMap_i::~idep_NameIndexMap_i()
{ 
    for (int i = 0; i < d_tableSize; ++i) {
        idep_NameIndexMapLink *p = d_table_p[i];
        while (p) {
        idep_NameIndexMapLink *q = p;
            p = p->d_next_p;
            delete q;
        }
    }
    delete [] d_table_p;
}

idep_NameIndexMapLink *& idep_NameIndexMap_i::findSlot(const char *name)
{
    int index = hash(name) % d_tableSize;
    assert(index >= 0 && index < d_tableSize);
    return d_table_p[index];
}

int idep_NameIndexMap_i::insert(idep_NameIndexMapLink *& slot, const char *nm)
{
    int index = d_array.append(nm); // index is into a managed string array
    slot = new idep_NameIndexMapLink(d_array[index], index, slot);
    return index;
}

                // -*-*-*- idep_NameIndexMap -*-*-*-

idep_NameIndexMap::idep_NameIndexMap(int maxEntriesHint)
: d_this(new idep_NameIndexMap_i(maxEntriesHint))
{
} 

idep_NameIndexMap::~idep_NameIndexMap()
{
    delete d_this;
}                                     

int idep_NameIndexMap::add(const char* name)
{
    idep_NameIndexMapLink *& slot = d_this->findSlot(name);
    return find(slot, name) ? BAD_INDEX : d_this->insert(slot, name);
}

int idep_NameIndexMap::entry(const char* name)
{
    idep_NameIndexMapLink *& slot = d_this->findSlot(name);
    const idep_NameIndexMapLink *link = find(slot, name);
    return link ? link->d_index : d_this->insert(slot, name);
}

const char *idep_NameIndexMap::operator[](int i) const
{
    return d_this->d_array[i];
}

int idep_NameIndexMap::length() const
{
    return d_this->d_array.length();
}

int idep_NameIndexMap::lookup(const char *name) const
{
    idep_NameIndexMapLink *& slot = d_this->findSlot(name);
    const idep_NameIndexMapLink *link = find(slot, name);
    return link ? link->d_index : BAD_INDEX;
}

ostream& operator<<(ostream& out, const idep_NameIndexMap& map)
{
    int fieldWidth = 10;
    int maxIndex = map.length() - 1;
    assert (sizeof (long int) >= 4);
    long int x = 1000 * 1000 * 1000;    // requires 4-byte integer.
    while (fieldWidth > 1 && 0 == maxIndex / x) {
        --fieldWidth;
        x /= 10;
    }
 
    for (int i = 0; i < map.length(); ++i) {
        out.width(fieldWidth);
        out << i << ". " << map[i] << endl;
    }
 
    return out;
}

