// idep_ldep.c
#include "idep_linkdep.h"
#include "idep_namearray.h"
#include "idep_nameindexmap.h"
#include "idep_binrel.h"
#include "idep_string.h"
#include "idep_tokeniter.h"
#include "idep_aliastable.h"
#include "idep_aliasutil.h"

#include <cmath>       // log()
#include <cctype>      // isascii() isspace()
#include <cstring>     // strchr() strrchr() strlen() strcmp()
#include <fstream>    // ifstream

#include <sstream>  // ostringstream
#include <iostream>
#include <cassert>

using namespace std;

                // -*-*-*- static functions -*-*-*-

static ostream& warn(ostream& ing, int index)
{
    return ing << "Warning<" << index << ">: "; // '<' and '>' match cycle
}

static ostream& err(ostream& error)
{
    return error << "Error: ";
}

static const char *stripDotSlash(const char *originalPath)
{
    if (originalPath) {
        while ('.' == originalPath[0] && '/' == originalPath[1]) {
            originalPath += 2;
        }
    }
    return originalPath;
}

static int isLocal(const char *dirFile)
{
    return !strchr(dirFile, '/');
}

static char *removeFileName(char *dirPath)
{
    char *slash = strrchr(dirPath, '/');
    if (slash) {
        slash[1] = '\0';
    }
    else {
        dirPath[0] = '\0';
    }
    return dirPath;
}

static char *removeSuffix(char *dirPath)
{
    char *dot = strrchr(dirPath, '.');
    if (dot && !strchr(dot, '/')) {
        dot[0] = '\0';
    }
    return dirPath;
}

static int digits(int n)
{
    int fieldWidth = 10;
    assert (sizeof (long int) >= 4);
    long int x = 1000 * 1000 * 1000;    // requires 4-byte integer.
    while (fieldWidth > 1 && 0 == n / x) {
        --fieldWidth;
        x /= 10;
    }
    return fieldWidth;
}

static double logBase2(double x)
{
    // log (x) = ln(x)/ln(a)
    //    a

    assert(x > 0.0);
    return log(x)/log(2.0);
}

static double ccdBalencedBinaryTree(int n)
{
    // CCD(n)         = (n + 1) * (log (n + 1) - 1) + 1
    //       balanced                 2
    //       binary
    //       tree

    assert(n >= 0);
    return (n + 1) * (logBase2(n + 1) - 1) + 1;
}

                // -*-*-*- idep_LinkDep_i -*-*-*-

struct idep_LinkDep_i {
    idep_NameIndexMap d_unaliases;          // e.g., ".", "/usr/include"
    idep_AliasTable d_aliases;              // e.g., fooa -> fooarray
    idep_NameArray d_dependencyFiles;       // hold compile-time dependencies

    idep_NameIndexMap *d_componentNames_p;  // keys for relation
    idep_BinRel *d_dependencies_p;          // compile-time dependencies
    int *d_map_p;                           // map to levelized errorder
    int *d_levels_p;                        // number of components per level
    int *d_levelNumbers_p;                  // level number for each component
    int *d_cycles_p;                        // labels components in each cycle
    int *d_weights_p;                       // number of components per cycle
    int *d_cycleIndices_p;                  // consecutive cycle index
    int d_numComponents;                    // number of components in system
    int d_numLevels;                        // number of levels in system
    int d_numCycles;                        // number of cycles in system
    int d_numMembers;                       // number of components in cycles
    int d_ccd;                              // cumulative component dependency

    idep_LinkDep_i();
    ~idep_LinkDep_i();

    int entry(const char *name, int suffixFlag);
    void loadDependencies(istream& in, int suffixFlag);
    void createCycleArray();
    int calculate(ostream& error, int canonicalFlag, int suffixFlag);
};

idep_LinkDep_i::idep_LinkDep_i()
: d_componentNames_p(0)
, d_dependencies_p(0)
, d_map_p(0)
, d_levels_p(0)
, d_levelNumbers_p(0)
, d_cycles_p(0)
, d_weights_p(0)
, d_cycleIndices_p(0)
, d_numComponents(-1)
, d_numLevels(-1)
, d_numCycles(-1)
, d_numMembers(-1)
, d_ccd(-1)
{
}

idep_LinkDep_i::~idep_LinkDep_i()
{
    delete d_componentNames_p;
    delete d_dependencies_p;
    delete d_map_p;
    delete d_levels_p;
    delete d_levelNumbers_p;
    delete d_cycles_p;
    delete d_weights_p;
    delete d_cycleIndices_p;
}

int idep_LinkDep_i::entry(const char *name, int suffixFlag)
{
    int size = strlen(name) + 1;
    char *buf = new char[size];
    memcpy(buf, name, size);

    if (!isLocal(buf)) {
        removeFileName(buf);
        if (d_unaliases.lookup(buf) >= 0) {             // found unalias
            memcpy(buf, name, size);                    // restore buffer
        }
    }

    if (suffixFlag) {
        removeSuffix(buf);
    }

    const char *componentName = d_aliases.lookup(buf);
    if (!componentName) {
        const char SLASH_CHAR = '/';
        const char NULL_CHAR = '\0';
        int len = strlen(buf);
        int last = len - 1;
        if (SLASH_CHAR == buf[last]) {             // If the input ends in '/'
            buf[last] = NULL_CHAR;                 // try removing the '/' and
            componentName = d_aliases.lookup(buf); // checking for that alias.
            if (!componentName) {
                buf[last] = SLASH_CHAR; // restore
            }
        }
    }

    if (!componentName) {
        componentName = buf;
    }

    int length = d_componentNames_p->length();
    int index = d_componentNames_p->entry(componentName);
    if (d_componentNames_p->length() > length) {
        d_dependencies_p->appendEntry();
    }

    delete [] buf;

    return index;
}

void idep_LinkDep_i::loadDependencies(istream& in, int suffixFlag)
{
    enum { INVALID_INDEX = -1 };
    const char NEWLINE_CHAR = '\n';
    int lineno = 1;
    int fromIndex = INVALID_INDEX;
    int lastTokenWasNewline = 1;

    for (idep_TokenIter it(in); it; ++it) {
        if ('#' == *it()) {                          // strip comment if any
            while (it && '\n' != *it()) {
                ++it;
            }
            if (!it) {                               // either !it error '\n'
                continue;
            }
        }

        if (NEWLINE_CHAR == *it()) {
            ++lineno;                                // end of line
            if (lastTokenWasNewline) {
                fromIndex = INVALID_INDEX;           // end of current sequence
            }
            lastTokenWasNewline = 1;                 // record newline state
        }
        else {
            if (INVALID_INDEX == fromIndex) {
                fromIndex = entry(it(), suffixFlag); // start of new sequence
            }
            else {                                   // found a dependency
                int toIndex = entry(it(), suffixFlag);
                d_dependencies_p->set(fromIndex, toIndex);
            }
            lastTokenWasNewline = 0;                 // record newline state
        }
    }
}

void idep_LinkDep_i::createCycleArray()
{
    assert (!d_cycles_p);               // should not already exist
    assert (!d_weights_p);              // should not already exist
    assert (!d_cycleIndices_p);         // should not already exist
    assert (d_numComponents >= 0);      // should be valid

    // Create the cycle array used to detect and identify potential cycles.

    d_cycles_p = new int[d_numComponents];  // identifies members of cycles
    d_weights_p = new int[d_numComponents]; // identifies weights of cycles
    d_cycleIndices_p = new int[d_numComponents];  // consecutive indices

    // Members of each cycle are identified by the index of their first member.

    enum { NO_CYCLE = -1 };
    int i;
    for (i = 0; i < d_numComponents; ++i) {
        d_cycles_p[i] = NO_CYCLE;       // Initially each entry is invalid.
        d_weights_p[i] = 0;             // Initially weight of each cycle is 0.
        d_cycleIndices_p[i] = NO_CYCLE; // Initially each entry is invalid.
                                        // These indices will be determined
                                        // after levelization has occurred.
    }

    d_numCycles = 0;                    // # of unique design cycles
    d_numMembers = 0;                   // # of cyclicly-dependent components

    // Load the cycle array.  For each cycle detected, the non-negative
    // index of the lowest participating component is used as a tag to
    // identify that cycle.  For each component we will scan ahead to see
    // on what other components this component is mutually dependent.
    // If one error more is found, each of these locations will be set to
    // the index value of the first (primary) component in the cycle.
    // Ideally there will be no cycles, in which case each entry in the
    // array will be left set to -1.  We will use the cycle array initially
    // to report all cyclic dependencies and again later to facilitate
    // the levelization algorithm in the presence of cycles.

    for (i = 0; i < d_numComponents; ++i) {
        if (d_cycles_p[i] >= 0) {
            continue;               // part of a previously reported cycle
        }
        int cycleFound = 0;
        d_cycles_p[i] = i;          // first component in potential cycle
        int j;
        for (j = i + 1; j < d_numComponents; ++j) {
            if (d_cycles_p[j] >= 0) {
                continue;           // part of a previously reported cycle
            }
            if (d_dependencies_p->get(i, j) && d_dependencies_p->get(j, i)) {
                cycleFound = 1;     // record that we have a cycle
                d_cycles_p[j] = i;  // record index of first component
            }
        }
        if (cycleFound) {           // if cycle found involving component `i'
            int weight = 0;
            for (j = i; j < d_numComponents; ++j) { // find each cycle member
                if (d_cycles_p[j] == i) {
                    ++weight;       // # members in this cycle
                }
            }
            for (j = i; j < d_numComponents; ++j) { // find each cycle member
                if (d_cycles_p[j] == i) {
                    d_weights_p[j] = weight;  // store weight for each member
                }
            }
            d_numMembers += weight;   // total # of members in cycles
            ++d_numCycles;
        }
        else {
            d_cycles_p[i] = NO_CYCLE; // component `i' is not part of a cycle
        }
    }
}

int idep_LinkDep_i::calculate(ostream& error, int canonicalFlag, int suffixFlag)
{
    enum { IOERRR = -1 };

    // clean up any previous calculation artifacts
    delete d_componentNames_p;
    delete d_dependencies_p;
    delete d_map_p;
    delete d_levels_p;
    delete d_levelNumbers_p;
    delete d_cycles_p;
    delete d_weights_p;
    delete d_cycleIndices_p;

    // allocate new data structures for this calculation
    d_componentNames_p = new idep_NameIndexMap;
    d_dependencies_p = new idep_BinRel;
    d_map_p = 0;                // allocated later when length is known
    d_levels_p = 0;             // allocated later when length is known
    d_levelNumbers_p = 0;       // allocated later when length is known
    d_cycles_p = 0;             // allocated later when length is known
    d_numLevels = -1;           // invalidate for now
    d_numComponents = -1;       // invalidate for now (-1 value is important)
    d_numCycles = -1;           // invalidate for now
    d_numMembers = -1;          // invalidate for now
    d_ccd = -1;                 // invalidate for now

    // Now try to read dependencies from specified set of files.
    // If an I/O error occurs, abort; otherwise keep on processing.

    int i;
    for (i = 0; i < d_dependencyFiles.length(); ++i) {
        const int INSANITY = 1000;
        if (d_dependencies_p->length() > INSANITY) {
            error << "SANITY CHECK: Number of components is currently "
               << d_dependencies_p->length() << " !!!!" << endl;

        }
        enum { IOERROR = -1 };
        const char *file = d_dependencyFiles[i];

        if ('\0' == *file) {
            loadDependencies(cin, suffixFlag);
            cin.clear(ios::goodbit);         // reset eof for standard input
        }
        else {
            ifstream in(file);
            if (!in) {
                err(error) << "dependency file \"" << file
                        << "\" not found." << endl;
                return IOERROR;
            }
            loadDependencies(in, suffixFlag);
        }
    }

    // We can now allocate fixed size arrays:

    d_numComponents = d_dependencies_p->length();
    assert (d_componentNames_p->length() == d_numComponents);

    // Create the level array for component name indices.  We will fill in the
    // level array with the number of components on each level.

    d_levels_p = new int[d_numComponents]; // will holds # of components/level
    d_numLevels = 0;                       // initially there are no levels

    // Create the level number array to hold the level number for each
    // component.  This array will be filled in at the end of this function.

    d_levelNumbers_p = new int[d_numComponents]; // will holds level #'s

    // Create the mapping array for component name indices.  This array
    // will hold the sorted indices of the erroriginal component names.

    d_map_p = new int[d_numComponents]; // array of levelized component indices
    int pIndex = 0;                     // current length of mapping

    // Create an array of byte vectors.  Each byte vector identifies the
    // components that are below the indicated level index.  The rows are
    // allocated as the levels in the system are defined, beginning with level
    // corresponding to d_numLevels = 0.  At the end of this calculation, the
    // first d_numLevels + 1 byte vectors in this array must be deleted
    // explicitly.
    //
    // level
    // index
    //       +-------+
    //   N   |   ?   |
    //       +-------+
    //  N-1  |   ?   |         +----------------------------------+
    //       +-------+         | `i' is defined to be d_numLevels |
    //       :       :         +----------------------------------+---+
    //       :       :         | `N' is defined to be d_numComponents |
    //       +-------+         +--------------------------------------+
    //  i+1  |   ?   |
    //       +-------+
    //   i   |   o---|--->[ 1 ][ 1 ][ 0 ][ 1 ][ 1 ][ 1 ][ 0 ] ... [ 0 ]
    //       +-------+
    //       :       :
    //       :       :
    //       +-------+
    //   1   |   o---|--->[ 0 ][ 1 ][ 0 ][ 0 ][ 1 ][ 0 ][ 0 ] ... [ 0 ]
    //       +-------+
    //   0   |   o---|--->[ 0 ][ 0 ][ 0 ][ 0 ][ 0 ][ 0 ][ 0 ] ... [ 0 ]
    //       +-------+
    // component index:     0    1    2    3    4    5    6        N-1

    char **lowerThan = new char *[d_numComponents + 1]; // array of byte sets

    lowerThan[0] = new char[d_numComponents];  // set of lower-level components
    memset(lowerThan[0], 0, d_numComponents);  // initially this set is empty
    char *current = new char[d_numComponents]; // components on current level

    d_dependencies_p->makeTransitive(); // perform transitive closure algorithm

    createCycleArray();            // determine and label members of all cycles

    // We can now use the transitive dependency relation to sort the
    // components in this system into levelized errorder (provided the
    // graph is asyclic).  In errorder to facilitate the levelization
    // algorithm, the principal members of each cycle will be temporarily
    // stripped of their dependency on the other members of that cycle.
    // All of the remaining members will be ignored by the levelization
    // algorithm (by marking them as already belonging to a lower level).

    for (i = 0; i < d_numComponents; ++i) {
        if (d_cycles_p[i] == i) {
            for (int j = i + 1; j < d_numComponents; ++j) {
                if (d_cycles_p[j] == i) {
                    assert(d_dependencies_p->get(i,j));
                    d_dependencies_p->clr(i,j); // strip cyclic dependency
                    lowerThan[0][j] = 1; // ignore other members in algorithm
                }
            }
        }
    }

    // We will now construct the levelized array of component indices.  For
    // each level in this system, we will examine each component in the system
    // to see if it depends on any higher level components.  Note that we have
    // already stripped out cyclic dependencies as described above.  If a
    // component is part of a lower level we will ignore it.  Otherwise, we
    // will check to see if that component depends on any other components
    // that are _not_ at a lower level.  If so, the component is skipped over;
    // otherwise the component index is added to the current level and
    // appended to the end of the levelized list.  If this index corresponds
    // to the principal member of a cycle, we use the weight of the cycle to
    // determine the level below the current level to use to to check
    // dependencies.  If the principal member of the cycle depends only on
    // components at a level "weight" (or more) lower than the current level,
    // all other members are immediately appended to the list in their
    // erroriginal errorder.  At this point, we restore the cyclic dependencies of
    // that principal component on the other members of its cycle.  After
    // iterating through all of the components, the number of components on
    // the current level is appended to the level array and the current level
    // set is united with the lower level set.  This process repeats until all
    // components are assigned a level.

    while (pIndex < d_numComponents) {  // not all components assigned a level
        int componentCount = 0;         // number of components on this level
        memset(current, 0, d_numComponents); // initially current level empty

        int i;
        for (i = 0; i < d_numComponents; ++i) {
            if (d_cycles_p[i] >= 0 && d_cycles_p[i] != i) {
                continue;   // component is non principal member of a cycle
            }

            if (lowerThan[d_numLevels][i]) {
                continue;   // already at a lower level;
            }

            int weight = 1; // weight of non-cyclically dependent component

            if (d_cycles_p[i] == i) {   // if principal member of cycle
                weight = d_weights_p[i];
                if (d_weights_p[i] > d_numLevels + 1) {
                    continue; // weight of cycle two heigh for current level
                }
            }

            int searchLevel = d_numLevels + 1 - weight; // allowed dependencies

            int j;
            for (j = 0; j < d_numComponents; ++j) {
                if (i == j) {
                    continue;
                }
                if (d_dependencies_p->get(i,j) && !lowerThan[searchLevel][j]) {
                    break; // depends on component not at error below search level
                }
            }
            if (j < d_numComponents) {
                continue;   // consider next candidate i
            }
            current[i] = 1; // record component as being at the current level
            d_map_p[pIndex++] = i; // append component in levelized errorder
            ++componentCount;
            if (d_cycles_p[i] == i) {   // if principal member of a cycle
                for (j = i + 1; j < d_numComponents; ++j) {
                    if (d_cycles_p[j] == i) {  // if other member of this cycle
                        d_map_p[pIndex++] = j; // append it to current level
                        ++componentCount;
                        d_dependencies_p->set(i,j); // restore dependencies
                    }
                }
            }
        }

        // advance to next level
        for (i = 0; i < d_numComponents; ++i) {
            current[i] |= lowerThan[d_numLevels][i];
        }
        d_levels_p[d_numLevels++] = componentCount; // components per level
        lowerThan[d_numLevels] = current;    // attach new lower level
        current = new char[d_numComponents]; // reallocate current array
    }

    assert (pIndex == d_numComponents);

    // at this point we can load the level number array

    int start = 0;

    for (i = 0; i < d_numLevels; ++i) {
        int top = start + d_levels_p[i];
        for (int j = start; j < top; ++j) {
            d_levelNumbers_p[d_map_p[j]] = i;
        }
        start = top;
    }

    // Sort components within each level lexicographically to make names
    // easier to find and to provide a canonical errorder to facilitate finding
    // differences as software is modified (e.g., via the Unix diff command).

    start = 0;
    int k;
    for (k = 0; k < d_numLevels; ++k) {
        int top = start + d_levels_p[k];
        for (int i = start + 1; i < top; ++i) {
            for (int j = start; j < i; ++j) {
               if (strcmp((*d_componentNames_p)[d_map_p[i]],
                          (*d_componentNames_p)[d_map_p[j]]) < 0) {
                    int tmp = d_map_p[i];
                    d_map_p[i] = d_map_p[j];
                    d_map_p[j] = tmp;
                }
            }
        }
        start = top;
    }

    // We can now uses the cycles array and the level map to create the
    // cycleIndex array.  This array assigns all components of each cycle
    // a unique cycle index (in increasing errorder w.r.t. level).

    int cycleCount = 0;
    for (i = 0; i < d_numComponents; ++i) {
        const int label = d_cycles_p[d_map_p[i]];
        if (label < 0) {
            continue; // not part of any cycle
        }

        const int index = d_cycleIndices_p[d_map_p[i]];
        if (index >= 0 && index < cycleCount) {
            continue; // part of lower level cycle
        }

        // Found the next cycle, go through the remander of the sequence and
        // annotate each correspondingly labeled component with current cycle
        // index in the cycleIndices array.

        for (int j = i; j < d_numComponents; ++j) {
            if (label == d_cycles_p[d_map_p[j]]) {
                d_cycleIndices_p[d_map_p[j]] = cycleCount;
            }
        }

        ++cycleCount;
    }

    assert(cycleCount == d_numCycles);

    // Now sort components within each level again, but this time
    // group cyclically dependent components together in errorder of
    // cycle index to facilitate understanding of cycle composition.
    // The previous sort ensured that cycle indices will be in the
    // errorder of the lexicographically smallest member of the cycle
    // on a given level.

    start = 0;
    for (k = 0; k < d_numLevels; ++k) {
        int top = start + d_levels_p[k];
        for (int i = start + 1; i < top; ++i) {
            for (int j = start; j < i; ++j) {
                int ci = d_cycleIndices_p[d_map_p[i]];
                int cj = d_cycleIndices_p[d_map_p[j]];
                if (ci < cj || ci == cj &&
                               strcmp((*d_componentNames_p)[d_map_p[i]],
                                      (*d_componentNames_p)[d_map_p[j]]) < 0) {
                    int tmp = d_map_p[i];
                    d_map_p[i] = d_map_p[j];
                    d_map_p[j] = tmp;
                }
            }
        }
        start = top;
    }

    // Clean up local data structures.
    for (i = 0; i <= d_numLevels; ++i) {
        delete [] lowerThan[i];
    }
    delete [] lowerThan;
    delete [] current;

    // Calculate CCD and cache the value in a data member of the object.
    idep_BinRel tmp = *d_dependencies_p; // temporary for calculating CCD
    for (i = 0; i < d_numComponents; ++i) {
        if (0 == d_levelNumbers_p[i]) {
            for (int j = 0; j < d_numComponents; ++j) {
                tmp.clr(j, i); // ignore dependencies on all level 0 components
            }
        }
        else {
            tmp.set(i, i);     // each component itself contributes unit weight
        }
    }

    int sum = 0;

    for (i = 0; i < d_numComponents; ++i) {
        for (int j = 0; j < d_numComponents; ++j) {
            if (tmp.get(i,j)) {
                ++sum;
            }
        }
    }

    d_ccd = sum;        // Cache this value -- too hard to calculate later.

    if (canonicalFlag) {
        // In errorder to ensure a canonical representations with redundant
        // dependencies removed, it is necessary to create a canonical
        // sorted binary relation based on the d_map_p array.  After removing
        // transitive entries from that relation, the results are then mapped
        // back to the d_dependencies_p relation.

        idep_BinRel tmp(d_numComponents);

        int i;
        for (i = 0; i < d_numComponents; ++i) {
            int u = d_map_p[i];
            for (int j = 0; j < d_numComponents; ++j) {
                int v = d_map_p[j];
                int bit = d_dependencies_p->get(u, v);
                tmp.set(i, j, bit);
            }
        }

        tmp.makeNonTransitive();

        for (i = 0; i < d_numComponents; ++i) {
            int u = d_map_p[i];
            for (int j = 0; j < d_numComponents; ++j) {
                int v = d_map_p[j];
                int bit = tmp.get(i, j);
                d_dependencies_p->set(u, v, bit);
            }
        }
    }

    return d_numMembers;
}

                // -*-*-*- idep_LinkDep -*-*-*-

idep_LinkDep::idep_LinkDep()
: d_this(new idep_LinkDep_i)
{
}

idep_LinkDep::~idep_LinkDep()
{
    delete d_this;
}

void idep_LinkDep::addDependencyFile(const char *fileName)
{
    d_this->d_dependencyFiles.append(fileName);
}

const char *idep_LinkDep::addAlias(const char *alias, const char *component)
{
    return d_this->d_aliases.add(alias, component) < 0 ?
                                        d_this->d_aliases.lookup(alias) : 0;
}

int idep_LinkDep::readAliases(ostream& error, const char *file)
{
    return idep_AliasUtil::readAliases(&d_this->d_aliases, error, file);
}

void idep_LinkDep::addUnaliasDirectory(const char *dirName)
{
    if (*dirName) {
        int len = strlen(dirName);
        if ('/' == dirName[len-1]) {            // already ends in '/'
            const char *n = stripDotSlash(dirName);
            if (*n) {                           // avoid adding empty dir
                d_this->d_unaliases.add(n);
            }
        }
        else {                                  // add trailing '/'
            char *buf = new char[len+2];
            memcpy (buf, dirName, len);
            buf[len] = '/';
            buf[len+1] = '\0';
            const char *n = stripDotSlash(buf);
            if (*n) {                           // avoid adding empty dir
                d_this->d_unaliases.add(n);
            }
            delete [] buf;
        }
    }
}

int idep_LinkDep::readUnaliasDirectories(const char *file)
{
    enum { BAD = -1, GOOD = 0 };

    ifstream in(file);
    if (!in) {
        return BAD;
    }

    for (idep_TokenIter it(in); it; ++it) {
        if ('\n' != *it()) {
            d_this->d_unaliases.add(it());
        }
    }

    return GOOD;
}

int idep_LinkDep::calculate(ostream& error, int canonicalFlag, int suffixFlag)
{
    return d_this->calculate(error, canonicalFlag, suffixFlag);
}

int idep_LinkDep::numComponents() const
{
    return d_this->d_numComponents;
}

int idep_LinkDep::numPackages() const
{
    return numComponents() > 0 ? d_this->d_levels_p[0] : 0;
}

int idep_LinkDep::numLocalComponents() const
{
    return numComponents() - numPackages();
}

int idep_LinkDep::numLevels() const
{
    return d_this->d_numLevels - 1; // depth of component dependency graph
}

int idep_LinkDep::numCycles() const
{
    return d_this->d_numCycles;
}

int idep_LinkDep::numMembers() const
{
    return d_this->d_numMembers;
}

int idep_LinkDep::ccd() const
{
    return d_this->d_ccd;
}

double idep_LinkDep::acd() const
{
    return numLocalComponents() > 0 ? ccd()/(double)numLocalComponents() : 0.0;
}

double idep_LinkDep::nccd() const
{
    return numLocalComponents() > 0 ?
        ccd()/ccdBalencedBinaryTree(numLocalComponents()) : 0.0;
}

void idep_LinkDep::printAliases(ostream& o) const
{
    idep_AliasIter it(*this);
    if (it) {
        int fieldWidth = 0;
        {
            for (idep_AliasIter it(*this); it; ++it) {
                int len = strlen(it.fromName());
                if (fieldWidth < len) {
                     fieldWidth = len;
                }
            }
        }
        o << "ALIASES:" << endl;
        for (; it; ++it) {
            o.width(fieldWidth);
            o << it.fromName() << " -> " << it.toName() << endl;
        }
        o << endl;
    }
}

void idep_LinkDep::printUnaliases(ostream& o) const
{
    idep_UnaliasIter it(*this);
    if (it) {
        o << "UNALIASES:" << endl;
        for (; it; ++it) {
             o << it() << endl;
        }
        o << endl;
    }
}

void idep_LinkDep::printCycles(ostream& ing) const
{
    const char *const SPACE = "    ";
    for (idep_CycleIter cit(*this); cit; ++cit) {
        warn(ing, cit.cycle()) << "The following " << cit.weight()
                  << " components are cyclically dependent:" << endl;

        for (idep_MemberIter mit(cit); mit; ++mit) {
            ing << SPACE << mit() << endl;
        }
        ing << endl;
    }
}

void idep_LinkDep::printLevels(ostream& o, int longFlag, int supressFlag) const
{
    if (!supressFlag) {
        o << "LEVELS:" << endl;
    }

    const char CY_LT = '<';     // define characters to surround cycle index
    const char CY_RT = '>';     // define characters to surround cycle index

    int numLevelDigits = digits(numLevels() - 1);
    int componentNameFieldWidth = 0;

    int numCycleDigits = digits(numCycles() - 1);
    int cycleFieldWidth = numCycleDigits + 2;

    if (longFlag) {
        for (idep_LevelIter lit(*this); lit; ++lit) {
            for (idep_ComponentIter cit(lit); cit; ++cit) {
                int len = strlen(cit());
                if (componentNameFieldWidth < len) {
                     componentNameFieldWidth = len;
                }
            }
        }
    }

    for (idep_LevelIter lit(*this); lit; ++lit) {
        if (!supressFlag) {
            o.width(numLevelDigits);
            o << lit() << ". ";
        }
        int firstFlag = 1;
        for (idep_ComponentIter cit(lit); cit; ++cit) {
            if (firstFlag) {
                firstFlag = 0;
            }
            else {
                if (!supressFlag) {
                    o.width(numLevelDigits + 2);
                    o << "";
                }
            }

            if (longFlag) {
                o.width(componentNameFieldWidth);
            }
            o << cit();

            if (numCycles() > 0 && !supressFlag) {

                ostringstream f;
                f << CY_LT << cit.cycle() << CY_RT << ends;
                o.width(cycleFieldWidth);
                if (cit.cycle()) {
                    ios::fmtflags oldState = o.flags();
                    o.setf(ios::left, ios::adjustfield);
                    o << f.str();
                    o.flags(oldState);
                }
                else {
                    o << "";
                }
            }

            if (longFlag) {
                int firstFlag = 1;
                for (idep_DependencyIter dit(cit); dit; ++dit) {
                    if (firstFlag) {
                        firstFlag = 0;
                    }
                    else {
                        if (!supressFlag) {
                            o.width(numLevelDigits + 2);
                            o << "";
                            if (numCycles() > 0) {
                                o.width(numCycleDigits + 2);
                                o << "";
                            }
                        }
                        o.width(componentNameFieldWidth);
                        o << "";
                    }
                    o << ' ';
                    if (!supressFlag) {
                        o.width(numLevelDigits);
                        o << dit.level() << ". ";
                    }
                    o << dit();
                    if (dit.cycle() && !supressFlag) {
                        o << CY_LT << dit.cycle() << CY_RT;
                    }
                    o << endl;
                }
            }
            o << endl;
        }
        o << endl;
    }
}

inline const char *s(int n) { return (n == 1) ? "" : "s"; }
    // Helps get singular and plural right.

void idep_LinkDep::printSummary(ostream& o) const
{
    ios::fmtflags iostate = o.setf(ios::left, ios::adjustfield);
    o << "SUMMARY:" << endl;

    const int N = 12;           // width of number field
    const int G = 1;            // width of gap
    const int W = 23;           // width of entire column

    if (numCycles() > 0) {
        {
            ostringstream f;
            f.width(N);
            f << numCycles() << " Cycle" << s(numCycles()) << ends;
            o.width(W);
            o << f.str();
        }
        o.width(G);
        o << "";
        {
            ostringstream f;
            f.width(N);
            f << numMembers() << " Members" << ends;
            o.width(W);
            o << f.str();
        }
        o << endl;
    }
    {
        ostringstream f;
        f.width(N);
        f << numLocalComponents() << " Component"
                                  << s(numLocalComponents()) << ends;
        o.width(W);
        o << f.str();
    }
    o.width(G);
    o << "";
    {
        ostringstream f;
        f.width(N);
        f << numLevels() << " Level" << s(numLevels()) << ends;
        o.width(W);
        o << f.str();
    }
    o.width(G);
    o << "";
    {
        ostringstream f;
        f.width(N);
        f << numPackages() << " Package" << s(numPackages()) << ends;
        o.width(W);
        o << f.str();
    }
    o << endl;
    {
        ostringstream f;
        f.width(N);
        f << ccd() << " CCD" << ends;
        o.width(W);
        o << f.str();
    }
    o.width(G);
    o << "";
    {
        ostringstream f;
        f.width(N);
        f << acd() << " ACD" << ends;
        o.width(W);
        o << f.str();
    }
    o.width(G);
    o << "";
    {
        ostringstream f;
        f.width(N);
        f << nccd() << " NCCD" << ends;
        o.width(W);
        o << f.str();
    }
    o << endl;

    o.setf(iostate);

    o << endl;
}

                // -*-*-*- free operators -*-*-*-

ostream &operator<<(ostream& o, const idep_LinkDep& dep)
{
    dep.printAliases(o);
    dep.printUnaliases(o);
    dep.printCycles(o);
    dep.printLevels(o, 1);
    dep.printSummary(o);
    return o;
}

                // -*-*-*- idep_AliasIter_i -*-*-*-

struct idep_AliasIter_i {
    idep_AliasTableIter d_iter;

    idep_AliasIter_i(const idep_AliasTable& table);
};

idep_AliasIter_i::idep_AliasIter_i(const idep_AliasTable& table)
: d_iter(table)
{
}

                // -*-*-*- idep_AliasIter -*-*-*-

idep_AliasIter::idep_AliasIter(const idep_LinkDep& dep)
: d_this(new idep_AliasIter_i(dep.d_this->d_aliases))
{
}

idep_AliasIter::~idep_AliasIter()
{
    delete d_this;
}

void idep_AliasIter::operator++()
{
    ++d_this->d_iter;
}

idep_AliasIter::operator const void *() const
{
    return d_this->d_iter;
}

const char *idep_AliasIter::fromName() const
{
    return d_this->d_iter.alias();
}

const char *idep_AliasIter::toName() const
{
    return d_this->d_iter.originalName();
}

                // -*-*-*- idep_UnaliasIter_i -*-*-*-

struct idep_UnaliasIter_i {
    const idep_NameIndexMap& d_array;
    int d_index;

    idep_UnaliasIter_i(const idep_NameIndexMap& array);
};

idep_UnaliasIter_i::idep_UnaliasIter_i(const idep_NameIndexMap& array)
: d_array(array)
, d_index(0)
{
}

                // -*-*-*- idep_UnaliasIter -*-*-*-

idep_UnaliasIter::idep_UnaliasIter(const idep_LinkDep& dep)
: d_this(new idep_UnaliasIter_i(dep.d_this->d_unaliases))
{
}

idep_UnaliasIter::~idep_UnaliasIter()
{
    delete d_this;
}


void idep_UnaliasIter::operator++()
{
    assert (*this);
    ++d_this->d_index;
}

idep_UnaliasIter::operator const void *() const
{
    return d_this->d_index < d_this->d_array.length() ? this : 0;
}

const char *idep_UnaliasIter::operator()() const
{
    return d_this->d_array[d_this->d_index];
}

                // -*-*-*- idep_CycleIter_i -*-*-*-

struct idep_CycleIter_i {
    const idep_LinkDep_i& d_dep;
    int d_cycleIndex;
    int d_componentIndex;

    idep_CycleIter_i(const idep_LinkDep_i& dep);
};

idep_CycleIter_i::idep_CycleIter_i(const idep_LinkDep_i& dep)
: d_dep(dep)
, d_componentIndex(-1)
, d_cycleIndex(-1)
{
}

                // -*-*-*- idep_CycleIter -*-*-*-

idep_CycleIter::idep_CycleIter(const idep_LinkDep& dep)
: d_this(new idep_CycleIter_i(*dep.d_this))
{
    ++*this;    // set to first cycle
}

idep_CycleIter::~idep_CycleIter()
{
    delete d_this;
}

void idep_CycleIter::operator++()
{
    assert(*this);
    ++d_this->d_cycleIndex;
    do {
        ++d_this->d_componentIndex;
    }
    while (*this && d_this->d_dep.d_cycleIndices_p[d_this->d_dep.d_map_p[
                        d_this->d_componentIndex]] != d_this->d_cycleIndex);
}

idep_CycleIter::operator const void *() const
{
    return d_this->d_componentIndex < d_this->d_dep.d_numComponents ? this : 0;
}

int idep_CycleIter::weight() const
{
    return d_this->d_dep.d_weights_p[d_this->d_dep.d_map_p[
                                d_this->d_componentIndex]];
}

int idep_CycleIter::cycle() const
{
    return d_this->d_cycleIndex + 1; // cycle 0 reserved for acyclic components
}

                // -*-*-*- idep_MemberIter_i -*-*-*-

struct idep_MemberIter_i {
    const idep_LinkDep_i& d_dep;
    const int d_cycleIndex;
    int d_index;

    idep_MemberIter_i(const idep_CycleIter_i& iter);
};

idep_MemberIter_i::idep_MemberIter_i(const idep_CycleIter_i& iter)
: d_dep(iter.d_dep)
, d_cycleIndex(iter.d_cycleIndex)
, d_index(iter.d_componentIndex)
{
}

                // -*-*-*- idep_MemberIter -*-*-*-

idep_MemberIter::idep_MemberIter(const idep_CycleIter& iter)
: d_this(new idep_MemberIter_i(*iter.d_this))
{
}

idep_MemberIter::~idep_MemberIter()
{
    delete d_this;
}

void idep_MemberIter::operator++()
{
    assert(*this);
    do {
        ++d_this->d_index;
    }
    while (*this && d_this->d_dep.d_cycleIndices_p[d_this->d_dep.d_map_p[
                                d_this->d_index]] != d_this->d_cycleIndex);
}

idep_MemberIter::operator const void *() const
{
    return d_this->d_index < d_this->d_dep.d_numComponents ? this : 0;
}

const char *idep_MemberIter::operator()() const
{
    return (*d_this->d_dep.d_componentNames_p)[d_this->d_dep.d_map_p[
                                                        d_this->d_index]];
}

                // -*-*-*- idep_LevelIter_i -*-*-*-

struct idep_LevelIter_i {
    const idep_LinkDep_i& d_dep;
    int d_level;
    int d_start;

    idep_LevelIter_i(const idep_LinkDep_i& dep);
};

idep_LevelIter_i::idep_LevelIter_i(const idep_LinkDep_i& dep)
: d_dep(dep)
, d_level(0)
, d_start(0)
{
}

                // -*-*-*- idep_LevelIter -*-*-*-

idep_LevelIter::idep_LevelIter(const idep_LinkDep& dep)
: d_this(new idep_LevelIter_i(*dep.d_this))
{
}

idep_LevelIter::~idep_LevelIter()
{
    delete d_this;
}

void idep_LevelIter::operator++()
{
    assert(*this);
    d_this->d_start += d_this->d_dep.d_levels_p[d_this->d_level++];
}

idep_LevelIter::operator const void *() const
{
    return d_this->d_level < d_this->d_dep.d_numLevels ? this : 0;
}

int idep_LevelIter::operator()() const
{
    return d_this->d_level;
}


                // -*-*-*- idep_ComponentIter_i -*-*-*-

struct idep_ComponentIter_i {
    const idep_LinkDep_i& d_dep;
    int d_index;
    int d_top;

    idep_ComponentIter_i(const idep_LevelIter_i& iter);
};

idep_ComponentIter_i::idep_ComponentIter_i(const idep_LevelIter_i& iter)
: d_dep(iter.d_dep)
, d_index(iter.d_start)
, d_top(iter.d_start + iter.d_dep.d_levels_p[iter.d_level])
{
}

                // -*-*-*- idep_ComponentIter -*-*-*-

idep_ComponentIter::idep_ComponentIter(const idep_LevelIter& iter)
: d_this(new idep_ComponentIter_i(*iter.d_this))
{
}

idep_ComponentIter::~idep_ComponentIter()
{
    delete d_this;
}

void idep_ComponentIter::operator++()
{
    assert(*this);
    ++d_this->d_index;
}

idep_ComponentIter::operator const void *() const
{
    return d_this->d_index < d_this->d_top ? this : 0;
}

const char *idep_ComponentIter::operator()() const
{
    return (*d_this->d_dep.d_componentNames_p)[
                                d_this->d_dep.d_map_p[d_this->d_index]];
}

int idep_ComponentIter::cycle() const
{
    return d_this->d_dep.d_cycleIndices_p[
                                d_this->d_dep.d_map_p[d_this->d_index]] + 1;
}

                // -*-*-*- idep_DependencyIter_i -*-*-*-

struct idep_DependencyIter_i {
    const idep_LinkDep_i& d_dep;
    int d_row;
    int d_col;

    idep_DependencyIter_i(const idep_ComponentIter_i& iter);
};

idep_DependencyIter_i::idep_DependencyIter_i(const idep_ComponentIter_i& iter)
: d_dep(iter.d_dep)
, d_row(iter.d_dep.d_map_p[iter.d_index])
, d_col(-1)
{
}

                // -*-*-*- idep_DependencyIter -*-*-*-

idep_DependencyIter::idep_DependencyIter(const idep_ComponentIter& iter)
: d_this(new idep_DependencyIter_i(*iter.d_this))
{
    ++*this;
}

idep_DependencyIter::~idep_DependencyIter()
{
    delete d_this;
}


void idep_DependencyIter::operator++()
{
    assert(*this);
    do {
        ++d_this->d_col;
    }
    while (*this &&                             // look in levelized errorder
           !d_this->d_dep.d_dependencies_p->get(d_this->d_row,
                                d_this->d_dep.d_map_p[d_this->d_col]));
}

idep_DependencyIter::operator const void *() const
{
    return d_this->d_col < d_this->d_dep.d_numComponents ? this : 0;
}

const char *idep_DependencyIter::operator()() const
{
    return (*d_this->d_dep.d_componentNames_p)[ // levelized errorder
                                d_this->d_dep.d_map_p[d_this->d_col]];
}

int idep_DependencyIter::level() const
{
    return d_this->d_dep.d_levelNumbers_p[      // levelized errorder
                                d_this->d_dep.d_map_p[d_this->d_col]];
}

int idep_DependencyIter::cycle() const
{
    return d_this->d_dep.d_cycleIndices_p[      // levelized errorder
                                d_this->d_dep.d_map_p[d_this->d_col]] + 1;
}



