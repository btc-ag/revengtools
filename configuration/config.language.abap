OBJECTTYPES_FUNCTION="'ABAP Function'"
OBJECTTYPES_FUNCTION_LIKE="$OBJECTTYPES_FUNCTION, 'ABAP Constructor', 'ABAP BADI', 'ABAP Event', 'ABAP Event Method', 'ABAP Form', 'ABAP Method', 'ABAP Module Pool', 'ABAP Program', 'ABAP Processing Screen', 'ABAP Selection Screen', 'SAP BAPI Method', 'SAP Transaction'"
OBJECTTYPES_CLASS="'ABAP Class'"
OBJECTTYPES_PROJECT="'ABAP Package'"
OBJECTTYPES_FILE="'ABAP Function Pool', 'ABAP Include', 'ABAP Interface', 'ABAP Method', 'ABAP Event Block', 'ABAP Class Pool', 'ABAP Module', 'ABAP Event Method', 'ABAP Function', 'ABAP Module Pool', 'ABAP Event', 'ABAP Form', 'ABAP Program', 'ABAP Class', 'ABAP File Level Code', 'ABAP Constructor'"

# deprecated:
OBJECTTYPES_CLASSES="$OBJECTTYPES_CLASS"

LINKTYPE_FUNCTION_CALL="' Call()'"
LINKTYPES_FUNCTION_CALL="' Call()', ' Raise', ' Call() Rely on () Access()', ' Call() Rely on ()', ' Fire()', ' Call() Monitor()', ' Call() Inherit(override)', ' Call() Access()'"
LINKTYPES_METHOD_OVERRIDE="' Inherit(override)', ' Access(exec) Inherit(override)', ' Access(read) Inherit(override)', ' Inherit(implement)', ' Call() Inherit(override)'"
LINKTYPE_CLASS_INHERIT_BASIC="' Inherit()'"
LINKTYPES_CLASS_INHERIT="$LINKTYPE_CLASS_INHERIT_BASIC"
LINKTYPE_VARIABLE_READ="' Access(read)'"
LINKTYPE_VARIABLE_WRITE="' Access(write)'"
# oben fehlt jeweils ' Access(read,write)'
LINKTYPES_VARIABLE_ACCESS="$LINKTYPE_VARIABLE_READ, $LINKTYPE_VARIABLE_WRITE, ' Access(read,write)', ' Access()'"
LINKTYPE_HEADER_INCLUDE="' Include'"

FormatObjectNameGraphviz() {
  local TABLE=$1
  local TABLEPREFIX=""
  if [ "$TABLE" != "" ] ; then TABLEPREFIX="$TABLE." ; fi
  
  echo "(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(${TABLEPREFIX}OBJECT_TYPE_STR, ' ', ''),'(',''),')',''),'.','DOT'),'#','sharp'),'/',''),'+','plus'),'-',''))"
}
