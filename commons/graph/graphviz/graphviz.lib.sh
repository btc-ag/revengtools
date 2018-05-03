source $CONFIG_DIR/graphStyle.config


GraphvizHeadBasic() {
if [ "$RANKDIR" = "" ] ; then local RANKDIR="RL" ; fi
echo "
digraph G  {
    rankdir = ${RANKDIR};
    node [fontname=\"Lucida Sans\", fontsize=30];
	edge [fontname=\"Lucida Sans\", fontsize=20,arrowsize=${ARROWHEADFACTOR}];
	fontname=\"Lucida Sans\";
	fontsize=16;
"
}

GraphvizHead() {
GraphvizHeadBasic
SQLQuery "
SET NOCOUNT ON

select 'label = ~$2 ' + cast(min(JOBBEGINDATE) as varchar) + ' $VARIANT~;'
  from AnaJob
 where JobNam in ( $1 )  
" | tr "~" "\""
}

GraphvizTail() {
echo "
}
"
}
	

RenderDOTFile() {
	local DOTFILE=$1
	$GRAPHVIZ_BIN_DIR/dot -T$IMGTYPE -O $(to_cmd_path $DOTFILE)
}

ShowDOTFile() {
    local DOTFILE=$1
	
    RenderDOTFile $DOTFILE && cmd /c "start $(to_cmd_path $DOTFILE.$IMGTYPE)"
    #"rundll32.exe" C:\\WINDOWS\\system32\\shimgvw.dll,ImageView_Fullscreen $(to_cmd_path $DOTFILE.emf)
}
