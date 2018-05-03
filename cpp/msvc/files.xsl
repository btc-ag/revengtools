<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="2.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:msbuild="http://schemas.microsoft.com/developer/msbuild/2003"
>

<xsl:output method="text" encoding="ISO-8859-1" />
<xsl:strip-space elements="*"/>

<xsl:param name="relative_vcproj_base_path"/>
<xsl:param name="absolute_source_base_path"/>
<xsl:param name="extension_list"/>
<xsl:param name="base_name"/>

<!-- <xsl:template match="File[matches(@RelativePath, '.h$')]"> -->
<!--
<xsl:template match="File[matches(@RelativePath, '.h$')]">
  <xsl:value-of select="replace(@RelativePath, '^.*[.]([a-z]*)$', '$1')"/>
</xsl:template>
-->
  
<!-- For cmake-generated solution -->
<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1'))) and starts-with(lower-case(replace(@RelativePath, '\\', '/')), lower-case($absolute_source_base_path))]" priority="+2">
  <xsl:value-of select="string-join((/VisualStudioProject/@Name, concat('.', replace(replace(lower-case(replace(@RelativePath, '\\', '/')), lower-case(replace($absolute_source_base_path, '[+]', '[+]')), ''), '^.\\', ''))),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>
 
<!-- For traditional solution -->
<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1'))) and not(matches(@RelativePath, ':'))]" priority="+1">
  <xsl:value-of select="string-join((/VisualStudioProject/@Name, string-join(($relative_vcproj_base_path, replace(@RelativePath, '^.\\', '')),'/')),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<!-- For traditional solution VS2012 -->
<xsl:template match="*/msbuild:ClCompile[exists(index-of(tokenize($extension_list, ','), replace(@Include, '^.*[.]([a-z]*)$', '$1'))) and not(matches(@Include, ':'))]" priority="+1">
  <!-- <xsl:message terminate="no">Matched file <xsl:value-of select="@Include"/>, base dir <xsl:value-of select="$relative_vcproj_base_path"/></xsl:message>  -->
  <xsl:value-of select="string-join((string($base_name), string-join(($relative_vcproj_base_path, replace(@Include, '^.\\', '')),'/')),':')"/>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="File[exists(index-of(tokenize($extension_list, ','), replace(@RelativePath, '^.*[.]([a-z]*)$', '$1')))]">
  <xsl:message>Error, file not matched: <xsl:value-of select="@RelativePath"/>
  </xsl:message>
</xsl:template>

<xsl:template match="//text()"/>

</xsl:stylesheet>
