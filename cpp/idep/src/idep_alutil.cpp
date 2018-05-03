// idep_alutil.c
#include "idep_aliasutil.h"
#include "idep_aliastable.h"
#include "idep_tokeniter.h"
#include "idep_string.h"

#include <fstream>   // ifstream
#include <iostream>
#include <cassert>

using namespace std;

                // -*-*-*- static functions -*-*-*-

static ostream& warning(ostream& error, const char *file, int lineno)
{
    return error << "Warning in " << file << '(' << lineno << "): ";
}

static ostream& err(ostream& error, const char *file, int lineno)
{
    return error << "Error in " << file << '(' << lineno << "): ";
}

static int tryToAlias(idep_AliasTable *table, ostream& error,
                      const char *inputName, int lineno,
                      const char *componentName, const char *alias)
{
    if (table->add(alias, componentName) < 0) {
        const char *previousName = table->lookup(alias);
        err(error, inputName, lineno) << "two names for alias \""
            << alias << "\":" << endl << "    \"" << previousName
            << "\" and \"" << componentName << "\"" << endl;
        return 1;
    }
    return 0;
}

                // -*-*-*- idep_AliasUtil -*-*-*-

int idep_AliasUtil::readAliases(idep_AliasTable *table, ostream& error,
                                        istream& in, const char *inputName)
{
    // The following is a state-machine description of the alias language:

    enum State {
        START,          // starting a new alias
        CONTINUE_0,     // continue - no previous identifiers
        IDENT_0,        //    ident - no previous identifiers
        CONTINUE_1,     // continue - one previous identifier
        CONTINUE_NL,    // continue - newline terminated
        IDENT_NL,       //    ident - newline terminated
        NEWLINE_BL,     //  newline - blank line terminated
        CONTINUE_BL,    // continue - blank line terminated
        IDENT_BL,       //    ident - blank line terminated
        NUM_STATES      // must be last entry
    } state = START;

    enum Input {
        CONTINUE,       // continuation character by it self
        NEWLINE,        // end of line
        IDENT,          // indentifier (not the previous two)
        NUM_INPUTS      // must be last entry
    } input;

    enum Action {
        NOP,            // do nothing
        BEG_CUR,        // set component name to current token
        BEG_PRE,        // set component name to previous token
        BEG_PRE_CUR,    // set component name to previous and try current token
        TRY_CUR,        // try to alias current token to component name
        TRY_PRE,        // try to alias previous token to component name
        TRY_PRE_CUR,    // try to alias both tokens to component name
        END,            // unset component name
        NUM_ACTIONS     // must be last entry
    };

    static State nextStateTable[NUM_STATES][NUM_INPUTS] = {
        //CONTINUE      NEWLINE         IDENT
        { CONTINUE_0,   START,          IDENT_0         }, // START
        { CONTINUE_1,   START,          IDENT_NL        }, // CONTINUE_0
        { CONTINUE_1,   NEWLINE_BL,     IDENT_NL        }, // IDENT_0
        { CONTINUE_NL,  IDENT_0,        IDENT_NL        }, // CONTINUE_1
        { CONTINUE_NL,  IDENT_NL,       IDENT_NL        }, // CONTINUE_NL
        { CONTINUE_NL,  START,          IDENT_NL        }, // IDENT_NL
        { CONTINUE_BL,  START,          IDENT_BL        }, // NEWLINE_BL
        { CONTINUE_BL,  IDENT_BL,       IDENT_BL        }, // CONTINUE_BL
        { CONTINUE_BL,  NEWLINE_BL,     IDENT_BL        }  // IDENT_BL
    };

    static Action actionTable[NUM_STATES][NUM_INPUTS] = {
        //CONTINUE      NEWLINE         IDENT
        { NOP,          NOP,            BEG_CUR         }, // START
        { BEG_PRE,      NOP,            BEG_PRE_CUR     }, // CONTINUE_0
        { NOP,          NOP,            TRY_CUR         }, // IDENT_0
        { TRY_PRE,      NOP,            TRY_PRE_CUR     }, // CONTINUE_1
        { TRY_PRE,      NOP,            TRY_PRE_CUR     }, // CONTINUE_NL
        { NOP,          END,            TRY_CUR         }, // IDENT_NL
        { NOP,          END,            TRY_CUR         }, // NEWLINE_BL
        { TRY_PRE,      NOP,            TRY_PRE_CUR     }, // CONTINUE_BL
        { NOP,          NOP,            TRY_CUR         }  // IDENT_BL
    };

    const char *const EMPTY_NAME = "";
    const char NULL_CHAR = *EMPTY_NAME;
    const char COMMENT_CHAR = '#';
    const char CONTINUE_CHAR = '\\';
    const char NEWLINE_CHAR = '\n';

    int numBadAliases = 0;
    int lineno = 1;

    idep_String componentName = EMPTY_NAME;
    idep_String lastToken = EMPTY_NAME;
    Input lastInput = IDENT;

    for (idep_TokenIter it(in); it; ++it) {
        if (*it() == COMMENT_CHAR) {
            while (*it() != NEWLINE_CHAR) {
                ++it;                   // ignore all tokens until newline
            }
        }

        // Determine the input type:

        switch (*it()) {
          case CONTINUE_CHAR: {
            input = NULL_CHAR == it()[1] ? CONTINUE : IDENT;
          } break;
          case NEWLINE_CHAR: {
            input = NEWLINE;
          } break;
          default: {
            input = IDENT;
          } break;
        };

        // Perform the selected action:

        switch (actionTable[state][input]) {
          case NOP: {
          } break;
          case BEG_CUR: {
            componentName = it();
          } break;
          case BEG_PRE: {
            componentName = lastToken;
            warning(error, inputName, lineno) << '"' << lastToken
                << "\" << used as component name." << endl;
          } break;
          case BEG_PRE_CUR: {
            componentName = lastToken;
            numBadAliases += tryToAlias(table, error, inputName, lineno,
                                                        componentName, it());
            warning(error, inputName, lineno) << '"' << lastToken
                << "\" << used as component name." << endl;
          } break;
          case TRY_CUR: {
            numBadAliases += tryToAlias(table, error, inputName, lineno,
                                                        componentName, it());
          } break;
          case TRY_PRE: {
            numBadAliases += tryToAlias(table, error, inputName, lineno,
                                                   componentName, lastToken);
            warning(error, inputName, lineno) << '"' << lastToken
                << "\" << used as alias name." << endl;
          } break;
          case TRY_PRE_CUR: {
            numBadAliases += tryToAlias(table, error, inputName, lineno,
                                                   componentName, lastToken);
            numBadAliases += tryToAlias(table, error, inputName, lineno,
                                                        componentName, it());
            warning(error, inputName, lineno) << '"' << lastToken
                << "\" << used as alias name." << endl;
          } break;
          case END: {
            componentName = EMPTY_NAME;
          } break;
          default:
          case NUM_ACTIONS: {
            assert(0);
          }
        };

        // Advance to the next state:

        if (NEWLINE == input) {
            ++lineno;                           // end of line
        }

        lastToken = it();
        lastInput = input;

        state = nextStateTable[state][input];
    }

    return numBadAliases;                       // 0 on success
}


int idep_AliasUtil::readAliases(idep_AliasTable *table, ostream& error,
                                                        const char *fileName)
{
    enum { IOERROR = -1 };
    ifstream in(fileName);
    if (!in) {
        return IOERROR;
    }
    return readAliases(table, error, in, fileName);
}

