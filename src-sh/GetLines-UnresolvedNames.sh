#!/bin/bash

# Gibt zu einer Eingabe der Form 
#   Datei	Zeilennummer	Symbol	Weiteres
# (Ausgabe von ScanLogFilesForUnresolvedNames.sh) zusätzlich den Inhalt dieser Zeile aus und markiert darin das Symbol. 

. $(dirname $0)/../Generator/tools.lib.sh
IFS="	"

while read -r FILE LINE SYMBOL REST ; do
  echo -nE "$FILE"
  echo -ne "\t$LINE\t"
#  echo -nE "$SYMBOL"
#  echo -ne "\t"
  UNIXFILE=$(to_unix_path $FILE)
  # get line number $LINE, delete BOTH leading and trailing whitespace and output without trailing newline
  sed -e "${LINE}q;d" <$UNIXFILE | sed \
      -e 's/^[ \t]*//;s/[ \t]*$//' \
	  -e "s/\($SYMBOL\)/~~~\1~~~/" \
       | tr -d "\n\r"
  echo -ne "\t"	
  echo -E "$REST"
done


