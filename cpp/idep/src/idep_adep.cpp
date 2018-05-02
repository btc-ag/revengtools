// idep_adep.c
#include "idep_aliasdep.h"
#include "idep_namearray.h"
#include "idep_nameindexmap.h"
#include "idep_filedepiter.h"
#include "idep_tokeniter.h"
#include "idep_aliastable.h"
#include "idep_aliasutil.h"

#include <cctype>      // isascii() isspace()
#include <cstring>     // strlen() strrchr()
#include <fstream>     // ifstream
#include <cstdlib>     // memcpy()
#include <iostream>
#include <cassert>

using namespace std;

                // -*-*-*- static functions -*-*-*-

static ostream& warn(ostream& ing)
{
    return ing << "Warning: ";
}

static ostream& err(ostream& ing )
{
    return ing << "Error: ";
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

static const char *stripDir(const char *s)
{
    if (s) {
        const char *slash = strrchr(s, '/');
        return slash ? slash + 1 : s;
    }
    return s;   // input was null
}

static int isAsciiFile(const char *fileName)
{
    enum { NO = 0, YES = 1 };
    ifstream in(fileName);
    if (!in) {
        return NO;
    }

    // check for non-ascii characters
    char c;
    while (in && !in.get(c).eof()) {
       if (!isascii(c)) {
          return NO;
       }
    }
    return YES;
}

typedef void (idep_AliasDep::*Func)(const char *);
static void loadFromStream(istream& in, idep_AliasDep *dep, Func add)
{
    assert(in);
    for (idep_TokenIter it(in); it; ++it) {
        if ('#' == *it()) {                     // strip comment if any
             while (it && '\n' != *it()) {
                ++it;
            }
            continue;                           // either !it or '\n'
        }
        if ('\n' != *it()) {
            (dep->*add)(it());
        }
    }
}

static int loadFromFile(const char *file, idep_AliasDep *dep, Func add)
{
    enum { BAD = -1, GOOD = 0 };
    if (!isAsciiFile(file)) {
        return BAD;
    }
    ifstream in(file);
    assert(in);
    loadFromStream(in, dep, add);
    return GOOD;
}

static char *newStrCpy(const char *name)
{
    int size = strlen(name) + 1;
    char *buf = new char[size];
    memcpy(buf, name, size);
    return buf;
}

static char *removeSuffix(char *dirPath)
{
    char *dot = strrchr(dirPath, '.');
    if (dot && !strchr(dot, '/')) {     // if '.' found in final path segment
        dot[0] = '\0';                  // eliminate suffix ("a/.b" -> "a/")
    }
    return dirPath;
}

                // -*-*-*- idep_AliasDepIntArray -*-*-*-

class idep_AliasDepIntArray {   // auxiliary class to manage array memory
    int *d_array_p;
    int d_length;
    idep_AliasDepIntArray(const idep_AliasDepIntArray&);
    idep_AliasDepIntArray& operator=(const idep_AliasDepIntArray&);
  public:
    idep_AliasDepIntArray(int length) : // does not zero the memory!
			d_array_p(new int[length]), d_length(length) {}
    ~idep_AliasDepIntArray() { delete [] d_array_p; }
    int& operator[](int i) { return d_array_p[i]; }
    int length() const { return d_length; }
};

static void zero(idep_AliasDepIntArray *a) // non-primitive operation on array
{
    for (int i = 0; i < a->length(); ++i) {
        (*a)[i] = 0;
    }
}

                // -*-*-*- idep_AliasDepString -*-*-*-

class idep_AliasDepString {     // auxiliary class to manage modifiable char *
    char *d_string_p;
    idep_AliasDepString(const idep_AliasDepString&);
    idep_AliasDepString& operator=(const idep_AliasDepString&);
  public:
    idep_AliasDepString(const char *s) : d_string_p(newStrCpy(s)){}
    ~idep_AliasDepString() { delete [] d_string_p; }
    operator char *() { return d_string_p; }
};

                // -*-*-*- idep_AliasDep_i -*-*-*-

struct idep_AliasDep_i {
    idep_NameIndexMap d_ignoreNames;          // e.g., idep_compiledep.t.c
    idep_AliasTable d_aliases;                // e.g., my_inta -> my_intarray
    idep_NameIndexMap d_fileNames;            // files to be analyzed
};

                // -*-*-*- idep_AliasDep -*-*-*-

idep_AliasDep::idep_AliasDep()
: d_this(new idep_AliasDep_i)
{
}

idep_AliasDep::~idep_AliasDep()
{
    delete d_this;
}

void idep_AliasDep::addIgnoreName(const char *fileName)
{
    d_this->d_ignoreNames.add(fileName);
}

int idep_AliasDep::readIgnoreNames(const char *file)
{
    return ::loadFromFile(file, this, &idep_AliasDep::addIgnoreName);
}

const char *idep_AliasDep::addAlias(const char *alias, const char *component)
{
    return d_this->d_aliases.add(alias, component) < 0 ?
                                        d_this->d_aliases.lookup(alias) : 0;
}

int idep_AliasDep::readAliases(ostream& error, const char *file)
{
    return idep_AliasUtil::readAliases(&d_this->d_aliases, error, file);
}

void idep_AliasDep::addFileName(const char *fileName)
{
    d_this->d_fileNames.add(fileName);
}

int idep_AliasDep::readFileNames(const char *file)
{
    return loadFromFile(file, this, &idep_AliasDep::addFileName);
}

void idep_AliasDep::inputFileNames()
{
    if (cin) {
        loadFromStream(cin, this, &idep_AliasDep::addFileName);
        cin.clear(ios::goodbit);             // reset eof for standard input
    }
}

int idep_AliasDep::unpaired(ostream& out, ostream& ing, int suffixFlag) const
{
    int maxLength = d_this->d_fileNames.length();
    idep_AliasDepIntArray hits(maxLength);  // records num files per component
    idep_AliasDepIntArray cmap(maxLength);  // map component to (last) file
    zero(&hits);
    idep_NameIndexMap components;
    int numComponents = 0;

    idep_NameIndexMap printNames;   // Used to sort names for ease of use
                                    // during cut and past in the editor.

    int i;
    for (i = 0; i < maxLength; ++i) {
        idep_AliasDepString s(d_this->d_fileNames[i]);

        if (d_this->d_ignoreNames.lookup(s) >= 0) {
            continue; // ignore this file
        }
        removeSuffix(s);

        const char *componentName = d_this->d_aliases.lookup(s);
        if (!componentName) {
            componentName = s;
        }

        int componentIndex = components.entry(componentName);
        if (components.length() > numComponents) {      // new component
            ++numComponents;

        }

        assert(components.length() == numComponents);

        ++hits[componentIndex];
        cmap[componentIndex] = i; // overwrite with most recent index
    }

    for (i = 0; i < numComponents; ++i) {
        assert(hits[i] > 0);
        if (1 == hits[i]) {
            printNames.add(suffixFlag ? d_this->d_fileNames[cmap[i]]
                                      : components[i]);
        }
        if (hits[i] > 2) {
            warn(ing) << "component \"" << components[i]
                      << "\" consists of " << hits[i] << " files." << endl;
        }
    }

    // Because of library .o file name-length limitations it is often the
    // header which has the longer name representing the true name of the
    // component.  If the suffixFlag is 0, we will sort into almost
    // lexicographic order except that the shorter of two initially identical
    // names will *follow* rather than precede longer.  This ordering will
    // facilitate cut and past when creating an alias file by hand in a
    // text editor.

    int numUnpaired = printNames.length();
    idep_AliasDepIntArray smap(numUnpaired);
    for (i = 0; i < numUnpaired; ++i) {
        smap[i] = i;                            // identity mapping to start
    }

    for (i = 1; i < numUnpaired; ++i) {
        for (int j = 0; j < numUnpaired; ++j) {
            int swap;
            if (suffixFlag) {
                swap = strcmp(printNames[smap[i]], printNames[smap[j]]) < 0;
            }
            else {
                int li = strlen(printNames[smap[i]]);
                int lj = strlen(printNames[smap[j]]);
                int len = li < lj ? li : lj;    // min length
                int cmp = strncmp(printNames[smap[i]],
                                  printNames[smap[j]], len);
                swap = cmp < 0 || 0 == cmp && li > lj;  // longer first if tie
            }
            if (swap) {                                 // swap if necessary
                int tmp = smap[i];
                smap[i] = smap[j];
                smap[j] = tmp;
            }
        }
    }

    // print out names in (almost) lexicographic order (if suffixFlag set to 0)

    for (i = 0; i < numUnpaired; ++i) {
        out << printNames[smap[i]] << endl;
    }

    return printNames.length();
}

static const char *th(int n)
{
    return 1 == n ? "st" : 2 == n ? "nd" : 3 == n ? "rd" : "th";
}

int idep_AliasDep::verify(ostream& error) const
{
    enum { IOERROR = -1, GOOD = 0 } status = GOOD;
    int errorCount = 0; // keep track of the number of readable faulty files

    int length = d_this->d_fileNames.length();
    for (int i = 0; i < length; ++i) {
        const char *path = d_this->d_fileNames[i];
        idep_AliasDepString c(path);

        if (d_this->d_ignoreNames.lookup(c) >= 0) {
            continue; // ignore this file
        }

        // strip off suffix and path from component file name and check aliases
        removeSuffix(c);
        const char *actualComponent = stripDir(c);
        const char *compAlias = d_this->d_aliases.lookup(actualComponent);
        const char *component = compAlias ? compAlias : actualComponent;

        int directiveIndex = 0;
        idep_FileDepIter it(path);
        for (; it; ++it) {

            ++directiveIndex;

            // strip off suffix and path from header name and check aliases
            idep_AliasDepString h(it());
            removeSuffix(h);
            const char *actualHeader = stripDir(h);
            const char *headerAlias = d_this->d_aliases.lookup(actualHeader);
            const char *header = headerAlias ? headerAlias : actualHeader;

            if (0 == strcmp(component, header)) { // if the same, we found it
                break;
            }
        }

        if (!it.isValidFile()) { // if the file was never valid to begin with
            err(error) << "unable to open file \""
                    << path << "\" for read access." << endl;
            status = IOERROR;
        }
        else if (!it) {                         // header not found
            err(error) << "corresponding include directive for \"" << path
                    << "\" not found."
                    << endl;
            ++errorCount;
        }
        else if (1 != directiveIndex) {         // header found but not first
            err(error) << '"' << path
                    << "\" contains corresponding include as "
                    << directiveIndex << th(directiveIndex)
                    << " directive." << endl;
            ++errorCount;
        }

        // else there is nothing wrong here
    }

    return status == GOOD ? errorCount : status;
}


int idep_AliasDep::extract(ostream& out, ostream& error) const
{
    enum { IOERROR = -1, GOOD = 0 } status = GOOD;
    enum { INVALID_INDEX = -1 };
    int errorCount = 0; // keep track of number of readable faulty files

    idep_NameIndexMap uniqueHeaders;       // used to detect multiple .c files
    int length = d_this->d_fileNames.length();
    idep_AliasDepIntArray hits(length);    // records frequency of headers
    zero(&hits);
    idep_AliasDepIntArray hmap(length);    // index header file index in table
    idep_AliasDepIntArray verified(length);// verifies that guess was correct
    zero(&verified);

    int i;
    for (i = 0; i < length; ++i) {
        hmap[i] = INVALID_INDEX;   // set valid when a suitable header is found

        const char *path = d_this->d_fileNames[i];
        idep_AliasDepString c(path);

        if (d_this->d_ignoreNames.lookup(c) >= 0) {
            continue; // ignore this file
        }

        // strip off suffix and path from component file name and check aliases
        removeSuffix(c);
        const char *actualComponent = stripDir(c);
        const char *compAlias = d_this->d_aliases.lookup(actualComponent);
        const char *component = compAlias ? compAlias : actualComponent;

        idep_FileDepIter it(path);      // hook up with first dependency.

        if (!it.isValidFile()) {        // unable to read file
            err(error) << "unable to open file \""
                    << path << "\" for read access." << endl;
            status = IOERROR;
            continue;                   // nothing more we can do here
        }

        if (!it) {                      // no include directives
            err(error) << '"' << path
                    << "\" contains no include directives." << endl;
            ++errorCount;
            continue;                   // nothing more we can do here
        }

        // strip off suffix and path from header name and check aliases
        idep_AliasDepString h(it());
        removeSuffix(h);
        const char *actualHeader = stripDir(h);
        const char *headerAlias = d_this->d_aliases.lookup(actualHeader);
        const char *header = headerAlias ? headerAlias : actualHeader;

        if (0 == strcmp(component, header)) {

            // At this point, we have the component name and header name
            // that match either because the root names were matching or
            // because we found an alias that made it work.  Record this
            // fact in the verified array.

            verified[i] = 1;
        }
        else {

            // We suspect this may be an alias pair, but we are not sure.
            // We will check to see if an alias involving this .c file
            // already exists.  If so, that will override and we will
            // not regenerate the alias.

            if (compAlias) {
                continue;               // nothing more we can do here
            }
        }

        // We have no reason *not* to think this is a valid match (yet).
        // Record this header as being associated with the this .c file.

        int hIndex = uniqueHeaders.entry(header); // obtaine index of header
        ++hits[hIndex];                           // record frequency
        hmap[i] = hIndex;                         // set .c -> header index
    }

    const int FW = 25;
    const char *const ARROW = ">- probably correct -> ";

    // For each unique header, if more than one .c file names this header
    // int its first include directive, output a warning to the error stream.

    for (i = 0; i < uniqueHeaders.length(); ++i) {
        if (hits[i] > 1) {
            warn(error) << hits[i] << " files specify \"" << uniqueHeaders[i]
                 << "\" as their first include directive:" << endl;
            for (int j = 0; j < length; ++j) {
                if (i ==  hmap[j]) {
                    error.width(FW);
                    error << (verified[j] ? ARROW : "");
                    error << '"' << stripDir(d_this->d_fileNames[j])
                       << '"' << endl;
                }
            }
            error << endl;
        }
    }

    // Print the non-redundant header / implementation file aliases to
    // the specified output stream.

    for (i = 0; i < length; ++i) {
        if (hmap[i] >= 0 && !verified[i]) {
           // strip off suffix and path from component file name
           idep_AliasDepString c(d_this->d_fileNames[i]);
           removeSuffix(c);
           out << uniqueHeaders[hmap[i]] << ' ' << c << endl;
        }
    }

    return status == GOOD ? errorCount : status;
}

