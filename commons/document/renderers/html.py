# -*- coding: UTF-8 -*-
'''
Created on 26.10.2010

@author: SIGIESEC
'''
from commons.document.basic_if import Link
from commons.document.table_if import TableWriter, TableModel
from htmlentitydefs import codepoint2name
from itertools import ifilter
from string import Template
import posixpath

class HTMLHelper(object):
    JAVASCRIPT_BIB = Template("""
    <script type="text/javascript" src="${dirname}/jquery-latest.js"></script> 
    <script type="text/javascript" src="${dirname}/jquery.tablesorter.js"></script> 
    """)

    @staticmethod
    def get_html_head(title, charset, stylesheet, more=""):
        if stylesheet:
            stylesheet_html = '<link href="%s" rel="stylesheet" type="text/css" />' % stylesheet
        else:
            stylesheet_html = ""
        if stylesheet:
            stylesheet_dir = posixpath.dirname(stylesheet)
            if stylesheet_dir == "":
                stylesheet_dir = "."
            javascript_html = HTMLHelper.JAVASCRIPT_BIB.substitute({'dirname': stylesheet_dir})
            more += javascript_html
        return """
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=%s" />
            <title>%s</title>
            %s
            %s
            </head>
            """ % (charset,
                    title,
                    stylesheet_html,
                    more,
                    )

    @staticmethod
    def get_preamble():
        return "<body>"

    @staticmethod
    def get_postamble():
        return "</body>"

    @staticmethod
    def get_html_tail():
        return """
        </body>
        </html>
        """

    @staticmethod
    def render_html(string):
        """
        >>> [ord(c) for c in u"<"]
        [60]
        >>> HTMLHelper.render_html(u"<")
        u'&lt;'
        """
        unicode_string_in = unicode(string)
        unicode_string_out = u"".join("&%s;" % codepoint2name[ord(c)]
                                       if ord(c) in codepoint2name else c
                                       for c in unicode_string_in)        
        return unicode_string_out.replace("{b}", "<span style=\"background-color: #FFFF00\">").replace("{/b}", "</span>")

    @staticmethod
    def _render_content_iter(content):
        if content == None:
            raise StopIteration
        for element in content:
            if isinstance(element, Link):
                yield HTMLHelper._render_link(element)
            elif isinstance(element, HTMLText):
                yield element.text()
            else:
                yield HTMLHelper.render_html(str(element))

    @staticmethod
    def _render_link(link):
        assert isinstance(link, Link)
        return '<a href="%s">%s</a>' % (link.get_link_target(),
                                        HTMLHelper.render_content(link.get_text(), sep=" "))

    @staticmethod
    def render_content(content, sep):
        if content == None:
            return ""
        else:
            if isinstance(content, basestring) or not hasattr(content, '__iter__'):
                content = (content,)
            return sep.join(ifilter(lambda x: x != None and len(x) > 0, HTMLHelper._render_content_iter(content)))

class HTMLText(object):
    def __init__(self, text):
        self.__text = text

    def text(self):
        return self.__text

    def __str__(self):
        return self.__text

class HTMLTableWriter(TableWriter):
    HORIZONTAL_SEP = " "
    VERTICAL_SEP = "<br/>"
    UNORDERED_LIST_SEP = "</li><li>"
    
    UNORDERED_LIST_PRE = "<ul><li>"
    UNORDERED_LIST_POST = "</li></ul>"

    def __init__(self, output_file, table_model, example=False, sep=None, *args, **kwargs):
        TableWriter.__init__(self, output_file, table_model, *args, **kwargs)
        self.__output_file = output_file
        assert isinstance(table_model, TableModel)
        self.__table_model = table_model
        if sep == None:
            sep = HTMLTableWriter.HORIZONTAL_SEP
        self.__sep = sep
        self.__example = example

    def _write_cell(self, tm_column_data):
        """
        TODO: Add to the css:
        td.example {
            border-right: 1px solid #C1DAD7;
            border-bottom: 1px solid #C1DAD7;
            background: #E6EAE9;
            padding: 6px 6px 6px 12px;
            color: #4f6b72;
        }
        
        """
        print >>self.__output_file, "<td%s>"%(" class=example" if self.__example else "")
        output_content = self.__table_model.get_cell_content(tm_column_data)
        output_string = HTMLHelper.render_content(output_content, self.__sep)
        if self.__sep == self.UNORDERED_LIST_SEP and self.__sep in output_string:
            output_string = "%s%s%s" % (self.UNORDERED_LIST_PRE, output_string, self.UNORDERED_LIST_POST)
        if len(output_string) > 0:
            print >>self.__output_file, output_string
        else:
            print >>self.__output_file, "&nbsp;"
        print >>self.__output_file, "</td>"

    def _write_row_data_columns(self, tm_row_data):
        for tm_column_data in self.__table_model.get_data_columns(tm_row_data):
            self._write_cell(tm_column_data)


    def _write_header_row(self):
        print >>self.__output_file, """<thead>
        <tr>"""
        if self.__table_model.has_row_headers():
            print >>self.__output_file, '<th scope="col" class="nobg">&nbsp;</th>'

        for header in self.__table_model.get_column_headers():
            print >>self.__output_file, '<th scope="col">%s</th>' % (HTMLHelper.render_content(header, HTMLTableWriter.VERTICAL_SEP),)

        print >>self.__output_file, "</tr></thead>"

    def write_table(self, sortable=False):
        if sortable:
            print >>self.__output_file, """<script type="text/javascript" id="js">$(document).ready(function() {
                // call the tablesorter plugin
                $("#table%i").tablesorter();
            }); </script>""" % id(self)
        
        print >>self.__output_file, '<table%s>' % (' id="table%i" class="tablesorter"' % id(self) if sortable else "")
        self._write_header_row()

        print >>self.__output_file, "<tbody>"
        rows = self.__table_model.get_rows()
        for (row_number, (keyval, row_iter)) in enumerate(rows):
            print >>self.__output_file, "<tr>"
            if self.__table_model.has_row_headers():
                print >>self.__output_file, """
                <th scope="row" class="spec%s">%s</th>
                """ % ("alt" if (row_number % 2) else "",
                       HTMLHelper.render_content(self.__table_model.get_row_header_text(keyval), 
                                                 self.VERTICAL_SEP),
                       )
            self._write_row_data_columns(row_iter)
            print >>self.__output_file, """
            </tr>
            """

        print >>self.__output_file, "</tbody></table>"

if __name__ == "__main__":
    import doctest
    doctest.testmod()
