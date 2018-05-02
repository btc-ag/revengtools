// idep_fdepitr.c
#include "idep_filedepiter.h"

#include <cctype>      // isspace()
#include <cstring>     // strcspn()
#include <fstream>    // ifstream
#include <cassert>

using namespace std;

// -*-*-*- static functions -*-*-*-

enum { MAX_LINE_LENGTH  = 2048 };       // Arbitrary maximum length for
                                        // line containing an include
                                        // directive.  Note that other
                                        // lines may be longer.

static int loadBuf(istream& in, char *buf, int bufSize)
{
    enum { END_OF_INPUT = -1, SUCCESS = 0, OVERFLOW = 1 };

    // The getline (istream) method returns the line as a string but extracts
    // the trailing '\n'  only if there is space to spare in the buffer.  We
    // need to test for this condition by placing a non-null character in the
    // last position of the array before loading it.  If the last character is
    // null after the read then the newline was NOT extracted.

    int nearEnd = bufSize - 1;

    buf[nearEnd] = '\n'; // anything but '\0'

    if (in.getline(buf, bufSize).fail()) {
        return END_OF_INPUT;    // nothing left
    }

    if ('\0' == buf[nearEnd]) { // line was too long
        char c;
        while (in && !in.get(c).eof() && c != '\n') {
            // skip to next line
        }
        return OVERFLOW;        // buffer contains null-terminated string
    }

    return SUCCESS;
}

const char *extractDependency(char *buffer)
{
    // We assume we have a null terminated string that possibly contains a
    // valid include directive.  We will assume that such a directive has
    // the following syntax:
    //
    // ^#[ \t]*"include"[ \t ]*[<"][ \t]*{filename}[>" \t\n]
    //                                   ~~~~~~~~~~
    // i.e.,                             ^want this
    //  1. The first character on the line MUST be a '#'
    //  2. This character may be followed by any number of spaces or tabs.
    //  3. The next non-whitespace char must be an 'i' followed by "nclude".
    //  4. This string may be followed by any number of spaces or tabs.
    //  5. The next character must be either a '<' or a '"'.
    //  6. This character may be followed by any number of spaces or tabs.
    //  7. The {filename} follows and is terminated by whitespace, '>', or '"'.
    //
    // If an include directive is found, the buffer is modified and a pointer
    // to the included filename is returned; otherwise 0 is returned.

    if ('#' != buffer[0]) {                             // 1.
        return 0;
    }

    char *p = buffer;
    while (isspace(*++p)) {                             // 2.
    }

    if ('i' != *p) {                                    // 3a.
        return 0;
    }

    static char KEY[] = "include";
    if (0 != strncmp(p, "include", sizeof KEY - 1)) {   // 3b.
        return 0;
    }
    p += sizeof KEY - 1;        // advance over KEY

    while (isspace(*p)) {                               // 4.
        ++p;
    }

    if ('<' != *p && '"' != *p) {                       // 5.
        return 0;
    }
    ++p;

    while (isspace(*p)) {                               // 6.
        ++p;
    }

    // At this point, p points to the start of the file name
    // all we need to do is detect the end of the string.

    int length = strcspn(p, " \t\">");
    p[length] = 0;                                      // 7.

    return p;
}

                // -*-*-*- idep_FileDepIter_i -*-*-*-

struct idep_FileDepIter_i {
    ifstream d_file;
    char d_buf[MAX_LINE_LENGTH];
    const char *d_header_p;
    int d_isValidFile;

    idep_FileDepIter_i(const char *fileName);
};

idep_FileDepIter_i::idep_FileDepIter_i(const char *fileName)
: d_file(fileName)
, d_header_p(d_buf)             // buffer is not yet initialized
{
    d_isValidFile = !!d_file;   // depends on result of initialization
}

                // -*-*-*- idep_FileDepIter -*-*-*-

idep_FileDepIter::idep_FileDepIter(const char *fileName)
: d_this(new idep_FileDepIter_i(fileName))
{
    if (!isValidFile()) {
        d_this->d_header_p = 0; // iteration state is invalid
    }
    ++*this; // load first occurrence
}

idep_FileDepIter::~idep_FileDepIter()
{
    delete d_this;
}

void idep_FileDepIter::reset()
{
    if (isValidFile()) {
        d_this->d_file.seekg(ios::beg); // rewind to beginning of file
        d_this->d_file.clear(d_this->d_file.rdstate() & ios::badbit);
        d_this->d_header_p = d_this->d_buf;
    }
    ++*this; // load first occurrence
}

void idep_FileDepIter::operator++()
{
    d_this->d_header_p = 0;
    while (loadBuf(d_this->d_file, d_this->d_buf, sizeof d_this->d_buf) >= 0) {
        if (d_this->d_header_p = extractDependency(d_this->d_buf)) { // `=' ok
            break;
        }
    };
}

int idep_FileDepIter::isValidFile() const
{
    return d_this->d_isValidFile;
}

idep_FileDepIter::operator const void *() const
{
    return d_this->d_header_p ? this : 0;
}

const char *idep_FileDepIter::operator ()() const
{
    return d_this->d_header_p;
}

