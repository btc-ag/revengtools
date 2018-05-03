#!/bin/bash

# Gibt zu einer Eingabe der Form 
#   Datei	Zeilennummer	Weiteres
# zusätzlich den Inhalt dieser Zeile aus. 

. $(dirname $0)/../Generator/tools.lib.sh
IFS="	"

while read -r FILE LINE REST ; do
  echo -nE "$FILE"
  echo -ne "\t$LINE\t"
  echo -E "$REST"
  UNIXFILE=$(to_unix_path $FILE)
  sed -e "${LINE}q;d" <$UNIXFILE
done



