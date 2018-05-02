# -*- coding: UTF-8 -*-
'''
Created on 26.10.2010

@author: SIGIESEC
'''
from base.dependency.generation_log import GenerationLogTableModel
from commons.document.renderers.html import HTMLTableWriter, HTMLHelper
from datetime import datetime
import logging

class HTMLGeneratedGraphOverviewWriter(object):
    def __init__(self, output_file, generation_log, analysis_info):
        self.__output_file = output_file
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__analysis_info = analysis_info
        self.__generation_log = generation_log

    def _write_header(self):
        title = "Overview of BTC RevEngTools Results for %s" % self.__analysis_info[0]
        charset = "iso-8859-1"
        stylesheet = "styles.css"

        print >>self.__output_file, HTMLHelper.get_html_head(title, charset, stylesheet)

    def _get_output_file(self):
        return self.__output_file

    def _write_preamble(self):
        print >>self.__output_file, HTMLHelper.get_preamble()
        print >>self.__output_file, """
        <img src="images/btclogo.png" alt="BTC-Logo" align="right" width="200px"/>
        """
        print >>self.__output_file, """
        <h1>Overview of BTC RevEngTools Results</h1>
        <h2>System: %s, Version: %s, Repository revision: %s</h2>
        <h2>Analyzed repository subdirectories: %s</h2>
        <h2>Analysis time: %s</h2>
        
        <p>In case of any questions, please contact 
        <a href="mailto:simon.giesecke@btc-ag.com">Simon Giesecke</a>
        or create a bug report or feature proposal in the 
        <a href="http://ejra.e-konzern.de:8080/browse/BTCEPMARCH">TG Architektur JIRA project</a>. 
        Please choose Architekturmanagement-Werkzeuge: Python as the component.
        </p>
        
        <p>Note: The PDF versions may be empty for large graphs due to a bug in the 
        graph layouter GraphViz. Refer to the SVG version in these cases. The SVG 
        versions contain additional information as node and edge tooltips. <b>Google Chrome</b> 
        is not optimal, but the best currently known option to view SVGs. <b>Firefox</b> can be used,
        but is a bit fiddly regarding tooltips. <b>Internet Explorer</b> is not suited to view SVGs.</p>
        
        <p>Please refer to this <a href="GraphIntroduction.pdf">description of the graph notation</a>.</p>

        """ % (self.__analysis_info[0], self.__analysis_info[1], self.__analysis_info[2],
               ", ".join(self.__analysis_info[3]),
               datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))

    def section_description(self, section):
        # TODO replace by a dict
        if section == "":
            return "Full graphs"
        elif section == "focused":
            return "Subgraphs focused on specific node groups"
        elif section == "ifonly":
            return "Subgraphs showing interface modules only"
        elif section == "wraponly":
            return "Subgraphs showing container wrapper modules only"
        elif section == "testonly":
            return "Subgraphs showing container test modules only"
        elif section == "toplevel":
            return "CAB-style top-level module groups considering ALL modules"
        else:
            return section

    def _write_generation_log(self):
        group_models = GenerationLogTableModel.generation_log_group_models_factory(self.__generation_log)
        for (section, group_model) in group_models:
            print >>self.__output_file, "<h2>%s</h2>" % self.section_description(section)
            HTMLTableWriter(output_file=self.__output_file,
                            table_model=group_model).write_table()
            print >>self.__output_file, "<hr/>"


    def _write_postamble(self):
        print >>self.__output_file, HTMLHelper.get_postamble()

    def _write_tail(self):
        print >>self.__output_file, HTMLHelper.get_html_tail()

    def write(self):
        self._write_header()
        self._write_preamble()
        self._write_generation_log()
        self._write_postamble()
        self._write_tail()
