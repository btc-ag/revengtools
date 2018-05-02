'''
Created on 17.05.2012

@author: SIGIESEC
'''
from commons.document.renderers.html import HTMLHelper, HTMLTableWriter
from commons.document.table_util import SimpleTableModel
from datetime import datetime
import logging

class HTMLModuleLister(object):
    def __init__(self, output_file, analysis_info, module_list_supply):
        self.__output_file = output_file
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__analysis_info = analysis_info
        self.__module_list_supply = module_list_supply

    def _write_header(self):
        title = "Module list for %s" % self.__analysis_info[0]
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
        <h1>Module Overview</h1>
        <h2>System: %s, Version: %s, Repository revision: %s</h2>
        <h2>Analysis time: %s</h2>
        
        """ % (self.__analysis_info[0], self.__analysis_info[1], self.__analysis_info[2],
               datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))

    def _write_postamble(self):
        print >>self.__output_file, HTMLHelper.get_postamble()

    def _write_tail(self):
        print >>self.__output_file, HTMLHelper.get_html_tail()        
           
    def _write_modules(self, module_list):
        print >>self.__output_file, "<h2>List of all modules (%s)</h2>"%len(module_list) 
        HTMLTableWriter(output_file=self.__output_file,
                        table_model=SimpleTableModel(column_names=["Module specification file", "Module name"], data=module_list)).write_table()
        print >>self.__output_file, "<hr/>"
           
    @staticmethod
    def __level_string(level):
        return logging.getLevelName(level)
            
    def _write_diagnostics(self, diagnostics):
        diagnostics_list = sorted((((module_file,), ("%s: %s" % (self.__level_string(result.get_level()), result.get_message()) 
                                                     for result in diagnostics_items)))
                                  for (module_file, diagnostics_items) in diagnostics if len(diagnostics_items))
        if len(diagnostics_list):
            print >>self.__output_file, "<h2>Module diagnostics</h2>" 
            HTMLTableWriter(sep=HTMLTableWriter.UNORDERED_LIST_SEP, 
                            output_file=self.__output_file,
                            table_model=SimpleTableModel(column_names=["Module specification file", "Module diagnostics"], data=diagnostics_list)).write_table()
            print >>self.__output_file, "<hr/>"
    
    def write(self):
        if hasattr(self.__module_list_supply, "get_module_descriptors"):
            module_list = sorted(self.__module_list_supply.get_module_descriptors())
            self._write_header()
            self._write_preamble()
            self._write_modules(module_list)
            self._write_postamble()
            self._write_tail()
            return True
        else:
            return False
