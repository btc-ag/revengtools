// string.c
#include "idep_string.h"

#include <string.h>     // strlen() strcmp()
#include <memory.h>     // memcpy()

                // -*-*-*- static functions -*-*-*-

static char *init (const char *str) 
{
    int size = strlen(str) + 1;
    char *string = new char[size];
    memcpy(string, str, size);
    return string;
}

                // -*-*-*- idep_String -*-*-*-

// CREATORS
idep_String::idep_String() 
: d_string_p(init(""))
{ 
}

idep_String::idep_String(const idep_String& string) 
: d_string_p(init(string.d_string_p))
{ 
}

idep_String::idep_String(const char* str) 
: d_string_p(init(str))
{ 
}

idep_String::~idep_String() 
{
    delete d_string_p;
}

// MANIPULATORS
idep_String& idep_String::operator=(const idep_String& string) 
{
    if (this != &string) {
        delete d_string_p;
        d_string_p = init(string.d_string_p);
    }
    return *this;
}

idep_String& idep_String::operator=(const char* str) 
{
    char *tmp = d_string_p;     // string could be a substring of itself
    d_string_p = init(str);
    delete tmp;
    return *this;
}

idep_String& idep_String::operator+=(const idep_String& string) 
{
    return *this += string.d_string_p;
}
    
idep_String& idep_String::operator+=(const char* str) 
{
    char *tmp = d_string_p;     
    int len = length();
    int size = strlen(str) + 1;
    d_string_p = new char[len + size];
    memcpy(d_string_p, tmp, len);
    memcpy(d_string_p + len, str, size);
    delete tmp;
    return *this;
}

// ACCESSORS
idep_String::operator const char *() const 
{
    return d_string_p;
}

int idep_String::length() const 
{
    return strlen(d_string_p);
}    

// FREE OPERATORS
idep_String operator+(const idep_String& left, const idep_String& right) 
{
    return idep_String(left) += right;
}

idep_String operator+(const char* str, const idep_String& string) 
{
    return idep_String(str) += string;
}

idep_String operator+(const idep_String& string, const char* str) 
{
    return idep_String(string) += str;
}

int operator==(const idep_String& left, const idep_String& right) 
{
    return strcmp(left, right) == 0;
}

int operator!=(const idep_String& left, const idep_String& right) 
{
    return strcmp(left, right) != 0;
}

int operator<(const idep_String& left, const idep_String& right) 
{
    return strcmp(left, right) <  0;
}

int operator<=(const idep_String& left, const idep_String& right) 
{
    return strcmp(left, right) <= 0;
}

int operator>(const idep_String& left, const idep_String& right) 
{
    return strcmp(left, right) >  0;
}

int operator>=(const idep_String& left, const idep_String& right) 
{
    return strcmp(left, right) >= 0;
}


int operator==(const char* str, const idep_String& string) 
{
    return strcmp(str, string) == 0;
}

int operator!=(const char* str, const idep_String& string) 
{
    return strcmp(str, string) != 0;
}

int operator<(const char* str, const idep_String& string) 
{
    return strcmp(str, string) <  0;
}

int operator<=(const char* str, const idep_String& string) 
{
    return strcmp(str, string) <= 0;
}

int operator>(const char* str, const idep_String& string) 
{
    return strcmp(str, string) >  0;
}

int operator>=(const char* str, const idep_String& string) 
{
    return strcmp(str, string) >= 0;
}


int operator==(const idep_String& string, const char *str) 
{
    return strcmp(str, string) == 0;
}

int operator!=(const idep_String& string, const char *str) 
{
    return strcmp(string, str) != 0;
}

int operator<(const idep_String& string, const char *str) 
{
    return strcmp(string, str) <  0;
}

int operator<=(const idep_String& string, const char *str) 
{
    return strcmp(string, str) <= 0;
}

int operator>(const idep_String& string, const char *str) 
{
    return strcmp(string, str) >  0;
}

int operator>=(const idep_String& string, const char *str) 
{
    return strcmp(string, str) >= 0;
}

