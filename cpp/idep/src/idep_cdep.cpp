// idep_cdep.c
#include "idep_compiledep.h"
#include "idep_namearray.h"
#include "idep_nameindexmap.h"
#include "idep_binrel.h"
#include "idep_string.h"
#include "idep_filedepiter.h"
#include "idep_tokeniter.h"

#include <cctype>      // isascii() isspace()
#include <cstring>     // strlen()
#include <fstream>    // ifstream
#include <iostream>
#include <cassert>

using namespace std;

                // -*-*-*- static functions -*-*-*-

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

static int isAbsolutePath(const char *originalPath)
{
    return '/' == *originalPath;
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

typedef void (idep_CompileDep::*Func)(const char *);
static void loadFromStream(istream& in, idep_CompileDep *dep, Func add)
{
    assert(in);
    char str[400];
       while(in){
          in.getline(str, 400);      // Delimiter defaults to newline
          (dep->*add)(str);
       }
    /*
    for (idep_TokenIter it(in); it; ++it) {
        if ('#' == *it()) {                     // strip comment if any
             while (it && '\n' != *it()) {
                ++it;
            }
            continue;                           // either !it error '\n'
        }
        if ('\n' != *it()) {
            (dep->*add)(it());
        }
    }
    */
}

static int loadFromFile(const char *file, idep_CompileDep *dep, Func add)
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

static const char *search(idep_String *s, const char *includeDir,
                                                            const char *file)
{
    assert(!isAbsolutePath(file));
    (*s = includeDir) += file;
    const char *dirFile = stripDotSlash(*s);
    return ifstream(dirFile) ? dirFile : 0;
}

static const char *search(idep_String *s, const idep_NameArray& a,
                                                            const char *file)
{
    if (isAbsolutePath(file)) {
        *s = file;
        const char *absFile = *s;
        return ifstream(absFile) ? absFile : 0;
    }

    const char *dirFile = 0;
    for (int i = 0; i < a.length(); ++i) {
        dirFile = search(s, a[i], file);
        if (dirFile) {
            break;
        }
    }

    return dirFile;
}

                // -*-*-*- static recursive functions -*-*-*-

// The following temporary, file-scope pointer variables are used
// only during the recursive calls of a single static function, getDep()
// in errorder to avoid the unnecessary time and space costs of passing
// several invariant arguments on the program stack.

static idep_BinRel *s_dependencies_p;   // set just before first call to getDep
static idep_NameIndexMap *s_files_p;    // set just before first call to getDep
static idep_NameArray *s_includes_p;    // set just before first call to getDep
static int s_recurse;                   // set just before first call to getDep
static ostream *s_err_p;                // set just before first call to getDep

static int getDep (int index)
{
    enum { BAD = -1, GOOD = 0 } status = GOOD;

    idep_String buffer; // string buffer, do not use directly
    idep_FileDepIter it((*s_files_p)[index]);
    for (; it; ++it) {
        const char *dirFile = search(&buffer, *s_includes_p, it());
        if (!dirFile) {
            err(*s_err_p) << "include directory for file \""
                 << it() << "\" not specified." << endl;
            status = BAD;
            continue;
        }

        int length = s_files_p->length();
        int otherIndex = s_files_p->entry(dirFile);

        if (s_files_p->length() > length) {
            // first time looking at this file
            s_dependencies_p->appendEntry();

            if (s_recurse && getDep(otherIndex)) {
                status = BAD;
            }
        }

        s_dependencies_p->set(index, otherIndex, 1);
    }

    if (!it.isValidFile()) {
       err(*s_err_p) << "unable to open file \""
         << (*s_files_p)[index] << "\" for read access." << endl;
        status = BAD;
    }

    return status;
}

                // -*-*-*- idep_CompileDep_i -*-*-*-

struct idep_CompileDep_i {
    idep_NameArray d_includeDirectories;      // e.g., ".", "/usr/include"
    idep_NameArray d_rootFiles;               // files to be analyzed

    idep_NameIndexMap *d_fileNames_p;         // keys for relation
    idep_BinRel *d_dependencies_p;            // compile-time dependencies
    int d_numRootFiles;                       // number of roots in relation

    idep_CompileDep_i();
    ~idep_CompileDep_i();
};

idep_CompileDep_i::idep_CompileDep_i()
: d_fileNames_p(0)
, d_dependencies_p(0)
, d_numRootFiles(-1)
{
}

idep_CompileDep_i::~idep_CompileDep_i()
{
    delete d_fileNames_p;
    delete d_dependencies_p;
}

                // -*-*-*- idep_CompileDep -*-*-*-

idep_CompileDep::idep_CompileDep()
: d_this(new idep_CompileDep_i)
{
}

idep_CompileDep::~idep_CompileDep()
{
    delete d_this;
}

void idep_CompileDep::addIncludeDirectory(const char *dirName)
{
    if (*dirName) {
        int len = strlen(dirName);
        if ('/' == dirName[len-1]) {            // already ends in '/'
            d_this->d_includeDirectories.append(dirName);
        }
        else {                                  // add trailing '/'
            char *buf = new char[len+2];
            memcpy(buf, dirName, len);
            buf[len] = '/';
            buf[len+1] = '\0';
            d_this->d_includeDirectories.append(buf);
            delete [] buf;
        }
    }
}

int idep_CompileDep::readIncludeDirectories(const char *file)
{
    return loadFromFile(file, this, &idep_CompileDep::addIncludeDirectory);
}

void idep_CompileDep::addRootFile(const char *fileName)
{
    d_this->d_rootFiles.append(fileName);
}

int idep_CompileDep::readRootFiles(const char *file)
{
    return loadFromFile(file, this, &idep_CompileDep::addRootFile);
}

void idep_CompileDep::inputRootFiles()
{
    if (cin) {
        loadFromStream(cin, this, &idep_CompileDep::addRootFile);
        cin.clear(ios::goodbit);             // reset eof for standard input
    }
}

int idep_CompileDep::calculate(ostream& error, int recursionFlag)
{
    enum { BAD = -1, GOOD = 0 } status = GOOD;

    // clean up any previous calculation artifacts
    delete d_this->d_fileNames_p;
    delete d_this->d_dependencies_p;

    // allocate new data structures for this calculation
    d_this->d_fileNames_p = new idep_NameIndexMap;
    d_this->d_dependencies_p = new idep_BinRel;
    d_this->d_numRootFiles = 0;


    // place all root files at the start of the relation
    int i;
    for (i = 0; i < d_this->d_rootFiles.length(); ++i) {
        idep_String s;
        const char *file = d_this->d_rootFiles[i];
        const char *dirFile = search(&s, d_this->d_includeDirectories, file);

        if (!dirFile) {
            err(error) << "root file \"" << file
                    << "\" not found." << endl;
            status = BAD;
        }
        else if (d_this->d_fileNames_p->add(dirFile) < 0) {
            err(error) << "root file \"" << file
                    << "\" redundantly specified." << endl;
            status = BAD;
        }
        else {
            ++d_this->d_numRootFiles;
            d_this->d_dependencies_p->appendEntry();
        }
    }

    // We must now investigate the compile-time dependencies for each
    // translation unit recursively.  First we will set up several
    // file-scope pointers to reduce recursive overhead.

    s_dependencies_p = d_this->d_dependencies_p;
    s_files_p = d_this->d_fileNames_p;
    s_includes_p = &d_this->d_includeDirectories;
    s_recurse = recursionFlag;
    s_err_p = &error;

    // Each translation unit forms the root of a tree of dependencies.
    // We will visit each node only once, recording the results as we go.
    // Initially, only the translation units are present in the relation.

    for (i = 0; i < d_this->d_numRootFiles; ++i) {
        const char *name = (*d_this->d_fileNames_p)[i];
        if (getDep(i)) {
            err(error) << "could not determine all dependencies for \""
                    << name << "\"." << endl;
            status = BAD;
        }
    }

    if (recursionFlag) {
        d_this->d_dependencies_p->makeTransitive();
    }

    return status;
}

                // -*-*-*- free operators -*-*-*-

/*
ostream &operator<<(ostream& o, const idep_CompileDep&(dep))
{
    const char *INDENT = "    ";
    for (idep_RootFileIter rit(dep); rit; ++rit) {
        idep_NameArray a;
        o << rit() << endl;
        for (idep_HeaderFileIter hit(rit); hit; ++hit) {
            if (isAbsolutePath(hit())) {
                a.append(hit());
            }
            else {
                o << INDENT << hit() << endl;
            }
        }
        for (int i = 0; i < a.length(); ++i) {
           o << INDENT << a[i] << endl;
        }
        o << endl;
    }
    return o;
}
*/

ostream &operator<<(ostream& o, const idep_CompileDep&(dep))
{
    const char *INDENT = "    ";
    for (idep_RootFileIter rit(dep); rit; ++rit) {
        idep_NameArray a;
        //o << rit() << endl;
        for (idep_HeaderFileIter hit(rit); hit; ++hit) {
            if (isAbsolutePath(hit())) {
                a.append(hit());
            }
            else {
                o << rit() << "," << hit() << endl;
            }
        }
        for (int i = 0; i < a.length(); ++i) {
           o << rit() << "," << a[i] << endl;
        }
        // o << endl;
    }
    return o;
}

                // -*-*-*- idep_RootFileIter_i -*-*-*-

struct idep_RootFileIter_i {
    const idep_CompileDep_i& d_dep;
    int d_index;

    idep_RootFileIter_i(const idep_CompileDep_i& dep);
};

idep_RootFileIter_i::idep_RootFileIter_i(const idep_CompileDep_i& dep)
: d_dep(dep)
, d_index(0)
{
}

                // -*-*-*- idep_RootFileIter -*-*-*-

idep_RootFileIter::idep_RootFileIter(const idep_CompileDep& dep)
: d_this(new idep_RootFileIter_i(*dep.d_this))
{
}

idep_RootFileIter::~idep_RootFileIter()
{
    delete d_this;
}

void idep_RootFileIter::operator++()
{
    assert(*this);
    ++d_this->d_index;
}

idep_RootFileIter::operator const void *() const
{
    return d_this->d_index < d_this->d_dep.d_numRootFiles ? this : 0;
}

const char *idep_RootFileIter::operator()() const
{
    return (*d_this->d_dep.d_fileNames_p)[d_this->d_index];
}

                // -*-*-*- idep_HeaderFileIter_i -*-*-*-

struct idep_HeaderFileIter_i {
    const idep_RootFileIter_i& d_iter;
    int d_index;

    idep_HeaderFileIter_i(const idep_RootFileIter_i& iter);
};

idep_HeaderFileIter_i::idep_HeaderFileIter_i(const idep_RootFileIter_i& iter)
: d_iter(iter)
, d_index(-1)
{
}

                // -*-*-*- idep_HeaderFileIter -*-*-*-

idep_HeaderFileIter::idep_HeaderFileIter(const idep_RootFileIter& iter)
: d_this(new idep_HeaderFileIter_i(*iter.d_this))
{
    ++*this;
}

idep_HeaderFileIter::~idep_HeaderFileIter()
{
    delete d_this;
}


void idep_HeaderFileIter::operator++()
{
    assert(*this);
    idep_BinRel *rel = d_this->d_iter.d_dep.d_dependencies_p;

    do {
        ++d_this->d_index;
    }
    while (   d_this->d_index < rel->length()
           && !rel->get(d_this->d_iter.d_index, d_this->d_index)
    );
}

idep_HeaderFileIter::operator const void *() const
{
    idep_BinRel *rel = d_this->d_iter.d_dep.d_dependencies_p;
    return d_this->d_index < rel->length() ? this : 0;
}

const char *idep_HeaderFileIter::operator()() const
{
    return (*d_this->d_iter.d_dep.d_fileNames_p)[d_this->d_index];
}

