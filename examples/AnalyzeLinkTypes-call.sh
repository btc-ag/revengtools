#!/bin/sh
TYPELIST="'C++ Project', 'C/C++ File', 'C/C++ Function', 'C++ Class', 'C++ Method'" CONFIG=config.prins.277 SHOW_CONTAIN_LINKS=1 SHOW_PARENT_LINKS=1 SHOW_TYPED_LINKS=1 ./AnalyzeLinkTypes.sh
TYPELIST="'ABAP Class', 'ABAP Module', 'ABAP Package', 'ABAP Include', 'ABAP Class Pool', 'ABAP Program', 'ABAP Function', 'ABAP Function Pool'"  CONFIG=config.easy SHOW_CONTAIN_LINKS=1 SHOW_PARENT_LINKS=1 SHOW_TYPED_LINKS=1 ./AnalyzeLinkTypes.sh
