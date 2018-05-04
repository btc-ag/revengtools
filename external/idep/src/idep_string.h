// idep_string.h
#ifndef INCLUDED_IDEP_STRING
#define INCLUDED_IDEP_STRING

// This leaf component defines 1 class:
//   idep_String: managed character string 

// Note: the behavior resulting from passing a null pointer as an argument
// to any function in this component is undefined.

class idep_String {
    char *d_string_p;

  public:
    // CREATORS
    idep_String();
    idep_String(const idep_String& idep_string);
    idep_String(const char *str);
    ~idep_String();

    // MANIPUALTORS
    idep_String &operator=(const idep_String& idep_string);
    idep_String &operator=(const char* str);

    idep_String& operator+=(const idep_String& idep_string);
    idep_String& operator+=(const char* str);
        // Concatenate to this string object.

    // ACCESSORS
    operator const char*() const;
        // Return a pointer to the fundamental null-terminated string 
        // representation.  Note: this pointer is valid only until this 
        // object is modified or destroyed.

    int length() const;
        // Return the length of the current string.  Note that the use of this 
        // function enables clients to efficiently exploit a wider variety of 
        // implementation alternatives for this class.
};

// FREE OPERATORS

idep_String operator+(const idep_String& idep_string, const char *str);
idep_String operator+(const char* str, const idep_String& idep_string);
idep_String operator+(const idep_String& left, const idep_String& right);
    // Concatenation: three variations to avoid ambiguity and for efficiency.

int operator==(const idep_String& left, const idep_String& right);
int operator!=(const idep_String& left, const idep_String& right);
int operator> (const idep_String& left, const idep_String& right);
int operator>=(const idep_String& left, const idep_String& right);
int operator< (const idep_String& left, const idep_String& right);
int operator<=(const idep_String& left, const idep_String& right);
    // Lexicographic comparison: (const idep_String&) and (const idep_String&).

int operator==(const idep_String& idep_string, const char *str);
int operator!=(const idep_String& idep_string, const char *str);
int operator> (const idep_String& idep_string, const char *str);
int operator>=(const idep_String& idep_string, const char *str);
int operator< (const idep_String& idep_string, const char *str);
int operator<=(const idep_String& idep_string, const char *str);
    // Lexicographic comparison: (const idep_String&) and (const char *).

int operator==(const char* str, const idep_String& idep_string);
int operator!=(const char* str, const idep_String& idep_string);
int operator> (const char* str, const idep_String& idep_string);
int operator>=(const char* str, const idep_String& idep_string);
int operator< (const char* str, const idep_String& idep_string);
int operator<=(const char* str, const idep_String& idep_string);
    // Lexicographic comparison: (const char *) and (const idep_String&).

# endif

