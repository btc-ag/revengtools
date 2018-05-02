<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="2.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:msbuild="http://schemas.microsoft.com/developer/msbuild/2003">

<xsl:output method="text" encoding="ISO-8859-1" />
<xsl:strip-space elements="*"/>

<xsl:param name="absolute_source_base_path"/>
<xsl:param name="extension_list"/>
<xsl:param name="file_list"/>
<!-- <xsl:param name="relative_vcproj_base_path">default</xsl:param> -->
<xsl:param name="projectfile_base_path"/>

<xsl:template name="dirname">
  <xsl:param name="path" />
  <xsl:if test="contains($path, '/')">
	<xsl:choose>
	<xsl:when test="contains(substring-after($path, '/'), '/')">
		<xsl:value-of select="concat(substring-before($path, '/'), '/')" />
		<xsl:call-template name="dirname">
		  <xsl:with-param name="path"
			select="substring-after($path, '/')" />
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
	<xsl:value-of select="substring-before($path, '/')" />
	</xsl:otherwise>
	</xsl:choose>
  </xsl:if>
</xsl:template>

<xsl:template name="normpath">
  <xsl:param name="path"/>
  <xsl:choose>
    <xsl:when test="contains($path, '/..')">
		<xsl:call-template name="normpath">
		  <xsl:with-param name="path" select="replace($path, '[^./][^/]*/[.][.]([/]|$)', '')"/>
        </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="replace($path, '/$', '')"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="process-files">
     <!-- <xsl:message terminate="no">Processing files for extension list <xsl:value-of select="$extension_list"/></xsl:message> -->
  <xsl:for-each select="tokenize($file_list, ',')">
    <xsl:variable name="thisdoc"><xsl:value-of select="."/></xsl:variable>
    <xsl:if test="$thisdoc != ''">
		<xsl:variable name="dirname"><xsl:call-template name="dirname"><xsl:with-param name="path" select="$thisdoc"/></xsl:call-template></xsl:variable>
		  <xsl:message terminate="no">Processing file <xsl:value-of select="$thisdoc"/> in directory <xsl:value-of select="$dirname"/></xsl:message>  

		<!-- CONTAINED SOURCE FILES -->
		<!-- for vcproj -->
		<xsl:apply-templates select="document(concat($projectfile_base_path, '/', $thisdoc))//File">
			<xsl:with-param name="relative_vcproj_base_path" select="$dirname"/>
		</xsl:apply-templates>
		<xsl:apply-templates select="document(concat($projectfile_base_path, '/', $thisdoc))/VisualStudioProject">
			<xsl:with-param name="filename" select="$thisdoc"/>
		</xsl:apply-templates>
		
		<!-- for csproj -->
		<xsl:apply-templates select="document(concat($projectfile_base_path, '/', $thisdoc))//msbuild:Compile">
			<xsl:with-param name="relative_csproj_base_path" select="$dirname"/>
		</xsl:apply-templates>
		<xsl:apply-templates select="document(concat($projectfile_base_path, '/', $thisdoc))//msbuild:AssemblyName">
			<xsl:with-param name="filename" select="$thisdoc"/>
		</xsl:apply-templates>
		
		<!-- REFERENCED ASSEMBLIES -->
		<xsl:apply-templates select="document(concat($projectfile_base_path, '/', $thisdoc))//msbuild:Reference">
			<xsl:with-param name="relative_csproj_base_path" select="$dirname"/>
			<xsl:with-param name="filename" select="$thisdoc"/>
		</xsl:apply-templates>
		<xsl:apply-templates select="document(concat($projectfile_base_path, '/', $thisdoc))//msbuild:ProjectReference">
			<xsl:with-param name="relative_csproj_base_path" select="$dirname"/>
			<xsl:with-param name="filename" select="$thisdoc"/>
		</xsl:apply-templates>
        
  <xsl:variable name="normprojdirname"><xsl:call-template name="normpath"><xsl:with-param name="path" select="replace(string-join(($projectfile_base_path, $dirname, '..'), '/'), '\\', '/')"/></xsl:call-template></xsl:variable>
  <xsl:value-of select="string-join((document(concat($projectfile_base_path, '/', $thisdoc))/msbuild:Project/msbuild:PropertyGroup/msbuild:AssemblyName/text(), $normprojdirname),'=')"/>
<xsl:text>
</xsl:text>		
		
	</xsl:if>
  </xsl:for-each>
  
</xsl:template>


<xsl:template match="/VisualStudioProject">
<xsl:param name="filename"/>
<xsl:value-of select="string-join((@Name, $filename), ':')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="msbuild:AssemblyName"> 
<xsl:param name="filename"/>
<xsl:value-of select="string-join((text(), $filename), ':')"/> 
<xsl:text>
</xsl:text>
</xsl:template>

<!-- For cmake-generated solution (with absolute paths) -->
<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1'))) and starts-with(lower-case(replace(@RelativePath, '\\', '/')), lower-case(replace($absolute_source_base_path, '\\', '/')))]" priority="+2">
<xsl:param name="relative_vcproj_base_path"/>
  <xsl:value-of select="string-join((/VisualStudioProject/@Name, concat('.', replace(replace(lower-case(replace(@RelativePath, '\\', '/')), lower-case(replace(replace($absolute_source_base_path, '\\', '/'), '[+]', '[+]')), ''), '^.\\', ''))),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>
 
<!-- For traditional solution (e.g. PRINS) -->
<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1'))) and not(matches(@RelativePath, ':'))]" priority="+1">
<xsl:param name="relative_vcproj_base_path"/>
<!--  <xsl:message terminate="no">Matched file <xsl:value-of select="@RelativePath"/>, base dir <xsl:value-of select="$relative_vcproj_base_path"/></xsl:message> -->
  <xsl:value-of select="string-join((/VisualStudioProject/@Name, string-join(($relative_vcproj_base_path, replace(@RelativePath, '^.\\', '')),'/')),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<!-- For C# solution (csproj) -->
<xsl:template match="msbuild:Compile[exists(index-of(tokenize($extension_list, ','), replace(@Include, '^.*[.]([a-z]*)$', '$1'))) and not(matches(@Include, ':'))]" priority="+1">
<xsl:param name="relative_csproj_base_path"/>
  <!-- <xsl:message terminate="no">Matched file <xsl:value-of select="@Include"/>, base dir <xsl:value-of select="$relative_csproj_base_path"/></xsl:message> -->	 
  <xsl:value-of select="string-join((/msbuild:Project/msbuild:PropertyGroup/msbuild:AssemblyName/text(), string-join(($relative_csproj_base_path, replace(@Include, '^.\\', '')),'/')),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>


<xsl:template match="msbuild:Reference[msbuild:HintPath/text()]" priority="+1">
  <xsl:param name="relative_csproj_base_path"/>
  <!-- <xsl:message terminate="no">Matched file <xsl:value-of select="@Include"/>, base dir <xsl:value-of select="$relative_csproj_base_path"/></xsl:message> -->	 
  <!--<xsl:value-of select="string-join((/msbuild:Project/msbuild:PropertyGroup/msbuild:AssemblyName/text(), tokenize(@Include, ',')[1]),':')"/>-->
  <xsl:variable name="normdllname"><xsl:call-template name="normpath"><xsl:with-param name="path" select="replace(string-join(($projectfile_base_path, $relative_csproj_base_path, ./msbuild:HintPath/text()), '/'), '\\', '/')"/></xsl:call-template></xsl:variable>
  <xsl:value-of select="string-join((/msbuild:Project/msbuild:PropertyGroup/msbuild:AssemblyName/text(), $normdllname),'=')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="msbuild:ProjectReference" priority="+1">
  <xsl:param name="relative_csproj_base_path"/>
  <xsl:message terminate="no">Matched project reference to file <xsl:value-of select="@Include"/>, base dir <xsl:value-of select="$relative_csproj_base_path"/></xsl:message>
  <!--<xsl:value-of select="string-join((/msbuild:Project/msbuild:PropertyGroup/msbuild:AssemblyName/text(), tokenize(@Include, ',')[1]),':')"/>-->
  <xsl:variable name="srcdirname"><xsl:call-template name="dirname"><xsl:with-param name="path" select="replace(@Include, '\\', '/')"/></xsl:call-template></xsl:variable>
  <xsl:variable name="normsrcdirname"><xsl:call-template name="normpath"><xsl:with-param name="path" select="replace(string-join(($projectfile_base_path, $relative_csproj_base_path, $srcdirname, '..'), '/'), '\\', '/')"/></xsl:call-template></xsl:variable>
 <xsl:value-of select="string-join((/msbuild:Project/msbuild:PropertyGroup/msbuild:AssemblyName/text(), $normsrcdirname),'=')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<!-- Error handling, these should not occur -->

<xsl:template match="msbuild:Compile[exists(index-of(tokenize($extension_list, ','), replace(@Include, '^.*[.]([a-z]*)$', '$1')))]">
  <xsl:message>Error, file not matched: <xsl:value-of select="@Include"/>
  </xsl:message>
</xsl:template>

<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1')))]">
  <xsl:message>Error, file not matched: <xsl:value-of select="@RelativePath"/>
  </xsl:message>
</xsl:template>


<xsl:template match="msbuild:Compile">
  <xsl:message>Error, file not matched: <xsl:value-of select="@Include"/>
  </xsl:message>
</xsl:template>

</xsl:stylesheet>
