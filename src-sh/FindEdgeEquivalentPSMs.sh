#!/bin/bash 
if [ "$1" = "" ] ; then
  DOTFILE=module_deps.OR.rwsm.dot
else
  DOTFILE="$1"
fi
echo "Using inputfile: $DOTFILE"

DOTINCLUDEFILE=tmp.$$
SEDFILE=tmpsed.$$
rm $DOTINCLUDEFILE $SEDFILE

MergePSMS() {
  if [ $# -gt 1 ] ; then
    echo Merge $*
	for a in $* ; do echo "s/[ 	]$a[ 	]/ $1 /" >>$SEDFILE; done
	echo "$1 [ label=\"$*\" ];" | sed 's/\([A-Za-z]\) \([A-Za-z]\)/\1\\n\2/g' >>$DOTINCLUDEFILE # TODO hier noch Leerzeichen durch \n ersetzen
  fi
}

Process() {
PREVIOUS="INVALID" 
PSMS=""
while read PSM2 REST ; do
  if [ "$REST" = "$PREVIOUS" ] ; then 
    PSMS="$PSMS $PSM2"
  else
     if [ "$PREVIOUS" != "INVALID" ] ; then
	   MergePSMS $PSMS
	 fi
	   PREVIOUS="$REST"
	   PSMS="$PSM2"
  fi
done; MergePSMS $PSMS
}

SEDCMD=""
grep ".*PSM" $DOTFILE | cut -d " " -f 3 | sort | uniq >PSM_NAMES
for PSM1 in `cat PSM_NAMES` ; do echo -n "$PSM1 " ; grep " $PSM1" $DOTFILE | cut -d " " -f 1 | tr "\n" " "  ; echo ; done | sort -k 2 | Process
cat $SEDFILE

INSERTMARK="INSERTPSMNODESMARK"
if grep "$INSERTMARK" $DOTFILE ; then
  sed -f $SEDFILE <$DOTFILE |	sed "/$INSERTMARK/ r $DOTINCLUDEFILE" >$(basename $DOTFILE .dot).merged.dot
else
  echo "}" >>$DOTINCLUDEFILE
  sed -f $SEDFILE <$DOTFILE |	sed -n -e "/^[}]/ r$DOTINCLUDEFILE" -e "/^[^}]/ p" >$(basename $DOTFILE .dot).merged.dot
fi

#rm $DOTINCLUDEFILE $SEDFILE
