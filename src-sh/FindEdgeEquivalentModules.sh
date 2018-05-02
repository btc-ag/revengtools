#!/bin/bash 
export INEQUIVFILE=tmpinequiv.$$
export OUTEQUIVFILE=tmpoutequiv.$$
export DOTINCLUDEFILE=tmpinclude.$$
export SEDFILE=tmpsed.$$
export NODENAMESFILE=tmpnodes.$$

MergeNodes() {
	if [ $# -gt 1 ] ; then
	echo Merge $*
	# for a in $* ; do echo "s/$a/$1/" >>$SEDFILE; done
	# echo "$1 [ label=\"$*\" ];" >>$DOTINCLUDEFILE # TODO hier noch Leerzeichen durch \n ersetzen
	echo "$*" >>$MERGEFILE
	fi
}

ProcessNodelist() {
	PREVIOUS="INVALID" 
	NODES=""
	while read NODE2 REST ; do
	  if [ "$REST" = "$PREVIOUS" ] ; then 
		NODES="$NODES $NODE2"
	  else
		 if [ "$NODES" != "" ] ; then
		   MergeNodes $NODES
		 fi
		   PREVIOUS="$REST"
		   NODES="$NODE2"
	  fi
	done; MergeNodes $NODES
}

ProcessDotfile() {
	local DOTFILE=$1
	local MERGEFILE
	rm $INEQUIVFILE $OUTEQUIVFILE $DOTINCLUDEFILE $SEDFILE $NODENAMESFILE
	touch $SEDFILE
	touch $DOTINCLUDEFILE

	SEDCMD=""
	grep "[-]" $DOTFILE | grep -v NODE | cut -d " " -f 1 | sort | uniq >$NODENAMESFILE
	# Für eingehende und ausgehende Kanten berechnen, dann Schnittmenge bilden
	MERGEFILE=$INEQUIVFILE
	for NODE1 in `cat $NODENAMESFILE` ; do echo -n "${NODE1} " ; grep "[-].*${NODE1}" $DOTFILE | cut -d " " -f 1 | tr "\n" " "  ; echo ; done | sort -k 2 | ProcessNodelist
	MERGEFILE=$OUTEQUIVFILE
	for NODE1 in `cat $NODENAMESFILE` ; do echo -n "${NODE1} " ; grep "${NODE1}.*[-]" $DOTFILE | cut -d " " -f 3 | tr "\n" " "  ; echo ; done | sort -k 2 | ProcessNodelist
	
	
		# for a in $NODES ; do echo "s/$a/$1/" >>$SEDFILE; done
		# echo "$NODES [ label=\"$*\" ];" >>$DOTINCLUDEFILE # TODO hier noch Leerzeichen durch \n ersetzen

	#cat $SEDFILE
	sed -f $SEDFILE <$DOTFILE |	sed "/INSERTNODESMARK/ r $DOTINCLUDEFILE" >$(basename $DOTFILE .dot).merged.dot

	#rm $DOTINCLUDEFILE $SEDFILE $MERGEFILE $NODENAMESFILE
}

DOTFILES=module_deps.DR.exec.dot
for DOTFILE in $DOTFILES; do
	ProcessDotfile $DOTFILE
done
