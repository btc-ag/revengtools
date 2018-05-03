// idep_tokitr.c
#include "idep_tokeniter.h"

#include <cctype>      // isspace()
#include <cstring>     // memcpy()
#include <iostream>
#include <cassert>

using namespace std;

                // -*-*-*- static functions -*-*-*-

enum { START_SIZE = 1, GROW_FACTOR = 2 };

const char NEWLINE_CHAR = '\n';
const char NULL_CHAR = '\0';

                // -*-*-*- idep_TokenIter_i -*-*-*-

struct idep_TokenIter_i {
    istream& d_in;
    char *d_buf_p;
    int d_size;
    int d_length;
    int d_newlineFlag;
    
    idep_TokenIter_i(istream& in);
    ~idep_TokenIter_i();
    void grow();
    void addChar(char ch);
    void advance();
};

idep_TokenIter_i::idep_TokenIter_i(istream& in)
: d_in(in)
, d_buf_p(new char[START_SIZE])
, d_size(START_SIZE)
, d_length(0)
, d_newlineFlag(0)
{
    assert(d_buf_p);
}

idep_TokenIter_i::~idep_TokenIter_i()
{
    delete d_buf_p;
}

void idep_TokenIter_i::grow()
{
    int newSize = d_size * GROW_FACTOR;
    char *tmp = d_buf_p;
    d_buf_p = new char[newSize];
    assert(d_buf_p);
    memcpy(d_buf_p, tmp, d_size);
    d_size = newSize;
    delete [] tmp;
}

void idep_TokenIter_i::addChar(char ch)
{
    if (d_length >= d_size) {
        grow();
    }
    assert(d_length < d_size);
    d_buf_p[d_length++] = ch;
}

                // -*-*-*- idep_TokenIter -*-*-*-

idep_TokenIter::idep_TokenIter(istream& in)
: d_this(new idep_TokenIter_i(in))
{
    ++*this; // load first occurrence
}

idep_TokenIter::~idep_TokenIter()
{
    delete d_this;
}

void idep_TokenIter::operator++() 
{ 
    assert(*this);

    d_this->d_length = 0;

    if (d_this->d_newlineFlag) {                   // left over newline
        d_this->d_newlineFlag = 0;
        d_this->addChar(NEWLINE_CHAR);
    }
    else {
        char c;
        while (d_this->d_in && !d_this->d_in.get(c).eof()) {
            if (d_this->d_length > 0) {            // "word" in progress
                if (isspace(c)) {
                    if (NEWLINE_CHAR == c) {
                        d_this->d_newlineFlag = 1; // note newline for later
                    }
                    break;                         // end of "word" in any case
                }
                d_this->addChar(c);                // start of "word"
            }
            else {                                 // nothing found yet
                if (isspace(c)) {
                    if (NEWLINE_CHAR == c) {
                        d_this->addChar(NEWLINE_CHAR);
                        break;                     // found a newline
                    }
                    continue;                      // found an ordinary space
                }
                d_this->addChar(c);                // add character to "word"
            }
        }
    }

    if (d_this->d_length > 0) {
        d_this->addChar(NULL_CHAR);                // always append a null char
    }
    else { 
        d_this->d_length = -1;                     // or make iterator invalid
    }
}    


idep_TokenIter::operator const void *() const 
{ 
    return d_this->d_length >= 0 ? this : 0;
}

const char *idep_TokenIter::operator()() const 
{ 
    return d_this->d_buf_p;
}


