<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format"
    version="1.1"
>

<xsl:include href="body_elements.xsl"/>
<xsl:include href="page.xsl"/>
<xsl:include href = "parameters.xsl"/>




    <xsl:output method="xml" encoding="UTF-8"/>

    <xsl:template match="/">
        <xsl:element name="fo:root">
            <xsl:call-template name="make-pages">
                <xsl:with-param name="page-layout" select="$page-layout"/>
            </xsl:call-template>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>


    <xsl:template match="*">
        <xsl:message>
            <xsl:text>no match for </xsl:text>
            <xsl:value-of select="name(.)"/>
        </xsl:message>
    </xsl:template>


</xsl:stylesheet>

