PROJECT(idep)

CMAKE_MINIMUM_REQUIRED(VERSION 2.6)


SET(IDEP_SRC
    idep_adep.cpp
    idep_altab.cpp
    idep_alutil.cpp
    idep_binrel.cpp
    idep_cdep.cpp
    idep_fdepitr.cpp
    idep_ldep.cpp
    idep_namea.cpp
    idep_nimap.cpp
    idep_string.cpp
    idep_tokitr.cpp
)

FOREACH(p a c l)
    SET( ${p}_SRC ${IDEP_SRC} ${p}dep.cpp )
    ADD_EXECUTABLE( ${p}dep ${${p}_SRC} )
ENDFOREACH(p a c l)
