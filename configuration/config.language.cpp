OBJECTTYPES_FUNCTION="'C/C++ Function', 'C/C++ Function Template', 'C/C++ Function Specialization'"
OBJECTTYPES_FUNCTION_LIKE="$OBJECTTYPES_FUNCTION, 'C++ Method', 'C++ Method Template', 'C++ Constructor', 'C++ Destructor'"
OBJECTTYPES_CLASS="'C++ Class', 'C++ Class Template'"
OBJECTTYPES_PROJECT="'C++ Project'"
OBJECTTYPES_FILE="'C/C++ File'"
OBJECTTYPES_GV="'C/C++ Global Variable'"
OBJECTTYPES_STRUCT="'C/C++ Struct', 'C/C++ Union'"
OBJECTTYPES_MACRO="'C/C++ Macro', 'C/C++ Enum', 'C/C++ Enum Item'"

# deprecated:
OBJECTTYPES_CLASSES="$OBJECTTYPES_CLASS"

LINKTYPE_FUNCTION_CALL="' Access(exec)'"
LINKTYPES_FUNCTION_CALL="' Access(exec)', ' Access(exec) Inherit(override)'"
LINKTYPES_METHOD_OVERRIDE="' Inherit(override)', ' Access(exec) Inherit(override)', ' Access(read) Inherit(override)'"
LINKTYPE_CLASS_INHERIT_BASIC="' Inherit()'"
LINKTYPES_CLASS_INHERIT="$LINKTYPE_CLASS_INHERIT_BASIC, ' Inherit() Friend'"
LINKTYPE_VARIABLE_READ="' Access(read)'"
LINKTYPE_VARIABLE_WRITE="' Access(write)'"
LINKTYPES_VARIABLE_ACCESS="$LINKTYPE_VARIABLE_READ, $LINKTYPE_VARIABLE_WRITE"
LINKTYPES_VARIABLE_ALL="' Access(exec)', ' Access(read,array)', ' Access(read,write)', ' Access(read)', ' Access(write)', ' Access(read,write,array)', ' Access(write,array)', ' Access(read,write,exec)', ' Access(read,exec)', ' Access(write,exec)', ' Access(read,exec,array)'"
LINKTYPES_STRUCT_ALL="' Rely on ()', ' Rely on () Access(member)', ' Access(member)'"
LINKTYPES_MACRO="' Access(exec)'"
# was ist mit read/write?
LINKTYPE_HEADER_INCLUDE="' Include'"


FormatObjectNameGraphviz() {
  local TABLE=$1
  local TABLEPREFIX=""
  if [ "$TABLE" != "" ] ; then TABLEPREFIX="$TABLE." ; fi

  echo "(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(${TABLEPREFIX}OBJECT_TYPE_STR, ' ', ''),'(',''),')',''),'.','DOT'),'#','sharp'),'/',''),'+','plus'),'-',''))"
}
