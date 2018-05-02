<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="2.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:msbuild="http://schemas.microsoft.com/developer/msbuild/2003"
>

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


<xsl:template match="process-files">
     <!-- <xsl:message terminate="no">Processing files for extension list <xsl:value-of select="$extension_list"/></xsl:message> -->
  <xsl:for-each select="tokenize($file_list, ',')">
    <xsl:variable name="thisdoc"><xsl:value-of select="."/></xsl:variable>
    <xsl:if test="$thisdoc != ''">
		<xsl:variable name="dirname"><xsl:call-template name="dirname"><xsl:with-param name="path" select="$thisdoc"/></xsl:call-template></xsl:variable>
        <xsl:variable name="basename" select="replace(replace($thisdoc, concat($dirname, '/'), ''), '.vcxproj', '')"/>
		 <!-- <xsl:message terminate="no">Processing file <xsl:value-of select="$thisdoc"/> in directory <xsl:value-of select="$dirname"/></xsl:message> -->
		
        
		<xsl:apply-templates select="document(concat($projectfile_base_path, '\\', $thisdoc))//msbuild:ClCompile">
			<xsl:with-param name="base_name" select="$basename"/>
			<xsl:with-param name="relative_vcproj_base_path" select="$dirname"/>
		</xsl:apply-templates>
		<xsl:apply-templates select="document(concat($projectfile_base_path, '\\', $thisdoc))//File">
			<xsl:with-param name="relative_vcproj_base_path" select="$dirname"/>
		</xsl:apply-templates>
        <xsl:choose>
            <xsl:when test="document(concat($projectfile_base_path, '\\', $thisdoc))/name() = 'VisualStudioProject'">
                <xsl:apply-templates select="document(concat($projectfile_base_path, '\\', $thisdoc))/VisualStudioProject">
                    <xsl:with-param name="filename" select="$thisdoc"/>
                </xsl:apply-templates>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$basename" />:<xsl:value-of select="$thisdoc"/>
<xsl:text>
</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
     </xsl:if>
  </xsl:for-each>
  
</xsl:template>


<xsl:template match="/VisualStudioProject">
<xsl:param name="filename"/>
<xsl:value-of select="string-join((@Name, $filename), ':')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<!-- <xsl:template match="File[matches(@RelativePath, '.h$')]"> -->
<!--
<xsl:template match="File[matches(@RelativePath, '.h$')]">
  <xsl:value-of select="replace(@RelativePath, '^.*[.]([a-z]*)$', '$1')"/>
</xsl:template>
-->
  
<!-- For cmake-generated solution -->
<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1'))) and starts-with(lower-case(replace(@RelativePath, '\\', '/')), lower-case(replace($absolute_source_base_path, '\\', '/')))]" priority="+2">
<xsl:param name="relative_vcproj_base_path"/>
  <xsl:value-of select="string-join((/VisualStudioProject/@Name, concat('.', replace(replace(replace(@RelativePath, '\\', '/'), replace(replace($absolute_source_base_path, '\\', '/'), '[+]', '[+]'), '', 'i'), '^.\\', ''))),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>
 
<!-- For traditional solution -->
<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1'))) and not(matches(@RelativePath, ':'))]" priority="+1">
<xsl:param name="relative_vcproj_base_path"/>
<!--  <xsl:message terminate="no">Matched file <xsl:value-of select="@RelativePath"/>, base dir <xsl:value-of select="$relative_vcproj_base_path"/></xsl:message> -->
  <xsl:value-of select="string-join((/VisualStudioProject/@Name, string-join(($relative_vcproj_base_path, replace(@RelativePath, '^.\\', '')),'/')),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1')))]">
  <xsl:message>Error, file not matched: <xsl:value-of select="@RelativePath"/>
  </xsl:message>
</xsl:template>

<!-- For traditional solution VS2012 -->
<xsl:template match="*/msbuild:ClCompile[exists(index-of(tokenize($extension_list, ','), replace(@Include, '^.*[.]([a-z]*)$', '$1'))) and not(matches(@Include, ':'))]" priority="+1">
  <xsl:param name="relative_vcproj_base_path"/>
  <xsl:param name="base_name"/>
  <!-- <xsl:message terminate="no">Matched file <xsl:value-of select="@Include"/>, base dir <xsl:value-of select="$relative_vcproj_base_path"/></xsl:message>  -->
  <xsl:value-of select="string-join((string($base_name), string-join(($relative_vcproj_base_path, replace(@Include, '^.\\', '')),'/')),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="//text()"/>

</xsl:stylesheet>
