"""
Created on 12.09.2012

@author: chbest
"""
from commons.document.renderers.html import HTMLHelper, HTMLTableWriter
from commons.document.renderers.xml import XMLHelper
from commons.document.table_util import SimpleTableModel
from datetime import datetime
from base.modules_if import SolutionFileSupply, SourceFileSupply, RuleSupply
from base.diagnostics_if import DiagnosticSubjectTypeParameterKeys
import logging
import types


class HTMLRuleListerOutputType(object):
    RESULTS_PER_RULE = "Results per Rule"
    RESULTS_PER_SUBJECT = "Results per Subject"
    RULE_OVERVIEW = "Rule Overview"


class XMLRuleListerOutputType(object):
    CHECKSTYLE_XML = "checkstyle xml"
    REVENGTOOLS_XML = "RevEngTools xml"

class XMLRuleLister(object):
    def __init__(self, output_file, module_list_supply, output_type):
        self.__output_file = output_file
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__module_list_supply = module_list_supply
        self.__output_type = output_type
        self.__logger.info("xml rule lister with output type: %s"%output_type)

    def _get_output_file(self):
        return self.__output_file
    
    def _write_header(self):
        print >>self.__output_file, XMLHelper.get_xml_head()
        
    def _write_preamble(self):
        if self.__output_type == XMLRuleListerOutputType.CHECKSTYLE_XML:
            self.__output_file.write( """<checkstyle version="5.5"> \n""")
        if self.__output_type == XMLRuleListerOutputType.REVENGTOOLS_XML:
            self.__output_file.write("""<revengtools version="0.1">""")
        
    def _write_tail(self):
        if self.__output_type == XMLRuleListerOutputType.CHECKSTYLE_XML:
            self.__output_file.write("""</checkstyle> \n""")
        if self.__output_type == XMLRuleListerOutputType.REVENGTOOLS_XML:
            self.__output_file.write("""</revengtools> \n""")

    def _write_diagnostics(self, diagnostics):
        if self.__output_type == XMLRuleListerOutputType.REVENGTOOLS_XML:
            self.__output_file.write("""<results>""")
        result_per_subjects = dict()
        for result in diagnostics:
            subject = result.get_subject()
            if isinstance(subject, types.StringTypes):
                self.__append_subject_to_subject_dict(subject, result_per_subjects, result)
            else:
                for single_subject in subject:
                    self.__append_subject_to_subject_dict(single_subject, result_per_subjects, result)     
        for subject in result_per_subjects:
            if self.__output_type == XMLRuleListerOutputType.CHECKSTYLE_XML:
                self.__write_one_checkstyle_result(subject, result_per_subjects[subject])
            if self.__output_type == XMLRuleListerOutputType.REVENGTOOLS_XML:
                self.__write_one_revengtools_result(subject, result_per_subjects[subject])
        if self.__output_type == XMLRuleListerOutputType.REVENGTOOLS_XML:
            self.__output_file.write("""</results>""")
            
    def __append_subject_to_subject_dict(self, subject, result_per_subjects, result):           
        try:
            result_per_subjects[subject].append(result)
        except KeyError:
            result_per_subjects[subject] = [result,]  
            
    # TODO transform {b}/{/b} into something sensible for XML output 
                  
    def __write_one_revengtools_result(self, subject, results_for_subject):
        self.__output_file.write("""<diagnosticResults subject="%s"> """%subject)
        for result in results_for_subject:
            severity = self.__level_string(result.get_level())
            dynamic_ID = result.get_diagnostic_description().get_dynamic_ID()
            message = result.get_message()
            subject_type = result.get_subject_type()
            self.__output_file.write("""<diagnosticResult severity="%s" message="%s" ruleID="%s" subjectType="%s"/> \n"""%(severity, message, dynamic_ID, subject_type))
        self.__output_file.write("""</diagnosticResults>""") 
                 
    def __write_one_checkstyle_result(self, subject, results_for_subject):
        self.__output_file.write("""<file name="%s"> \n """%subject)
        for result in results_for_subject:
            diagnostics_result = self.__level_string(result.get_level()),result.get_diagnostic_description().get_dynamic_ID(),result.get_message()
            (severity, dynamic_ID, message) = diagnostics_result
            self.__output_file.write("""<error line="0" severity="%s" message="%s" source="%s"/> \n"""%(severity, message, dynamic_ID))
        self.__output_file.write("""</file> \n""")        

    def _write_result_description(self, rules):
        self.__output_file.write("""<ruleDescriptions>""")
        for rule in rules:
            self.__output_file.write("""<rule id="%s" """%(rule.get_dynamic_ID()))           
            self.__output_file.write(""" description="%s" """ %rule.get_description())
            self.__output_file.write(""" severity="%s" />""" %self.__level_string(rule.get_severity()))
        self.__output_file.write("""</ruleDescriptions>""")
            
    @staticmethod
    def __level_string(level):
        return logging.getLevelName(level).lower()
    
    def write(self):
        if hasattr(self.__module_list_supply, "get_module_descriptors"):
            self._write_header()
            self._write_preamble()
            results = self.__module_list_supply.get_results()
            if self.__output_type == XMLRuleListerOutputType.REVENGTOOLS_XML:
                self._write_result_description(self.__module_list_supply.get_checked_rules())
            self._write_diagnostics(results)
            self._write_tail()
            return True
        else:
            return False
            

class HTMLRuleLister(object):
    def __init__(self, output_file, analysis_info, module_list_supply, output_type):
        self.__output_file = output_file
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__analysis_info = analysis_info
        self.__module_list_supply = module_list_supply
        self.__output_type = output_type
        self.__logger.info("html rule lister with output type: %s"%output_type)

    def _write_header(self):
        title = self.__output_type    
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
        <h1>%s</h1>
        <h2>System: %s, Version: %s, Repository revision: %s</h2>
        <h2>Analysis time: %s</h2>
        
        """ % (self.__output_type, self.__analysis_info[0], self.__analysis_info[1], self.__analysis_info[2],
               datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))

    def _write_postamble(self):
        print >>self.__output_file, HTMLHelper.get_postamble()

    def _write_tail(self):
        print >>self.__output_file, HTMLHelper.get_html_tail()
    
    def _write_rule_overview(self, rules):
        for rule in rules:
            self.__output_file.write("<h2>rule for %s</h2>"%rule.get_view_name())        
            self.__output_file.write("<p><em>Rule description: </em>%s</p>" %rule.get_description())
            self.__output_file.write("<p><em>Example: </em></p>")
            HTMLTableWriter(output_file=self.__output_file,
                     table_model=SimpleTableModel(column_names=["%s name"%rule.get_subject_type(), "%s diagnostic"%rule.get_subject_type()], data=rule.get_example()),example=False).write_table()
            self.__output_file.write("<p><em>Rule class name:</em> %s; <em>Rule severity:</em> %s</p>" %(rule.get_dynamic_ID(), self.__level_string(rule.get_severity())))
            self.__output_file.write("<hr/>")  
    
    def _write_per_rule(self, diagnostics):
        if len(diagnostics):
            number_of_results = len(diagnostics)
        result_types_descriptions = dict()
        for result in diagnostics:
            result_types_descriptions[result.get_diagnostic_description().get_view_name()] = result.get_diagnostic_description()
        for result_type in result_types_descriptions:
            result_description = result_types_descriptions[result_type]
            diagnostics_list = sorted(((result.get_subject()),("%s: %s" %(self.__level_string(result.get_level()),result.get_message()))) for result in diagnostics if result.get_diagnostic_description().get_view_name()==result_description.get_view_name())
            diagnostics_list = list((subject if isinstance(subject, types.StringTypes) else ', '.join(subject), message) for subject, message in diagnostics_list)
            if diagnostics_list:
                print >>self.__output_file, "<h2>List of %s </em>(%s of %s diagnostic results)</h2>"%(result_description.get_view_name(), len(diagnostics_list), number_of_results)           
                print >>self.__output_file, "<p><em>Rule description: </em>%s</p>" %result_description.get_description()
                print >>self.__output_file, "<p><em>Rule class name:</em> %s; <em>Rule severity:</em> %s</p>" %(result_description.get_dynamic_ID(), self.__level_string(result_description.get_severity()))
                HTMLTableWriter(output_file=self.__output_file,
                        table_model=SimpleTableModel(column_names=["%s name"%result_description.get_subject_type(), "%s diagnostic"%result_description.get_subject_type()], data=diagnostics_list)).write_table()
                print >>self.__output_file, "<hr/>"          
          
    @staticmethod
    def __level_string(level):
        return logging.getLevelName(level)

    @staticmethod
    def _get_subject_string(subject):
        if isinstance(subject, types.StringTypes):
                return subject
        else:
            return ", ".join(subject)
            
    def _write_per_subject(self, diagnostics):
        #if len(diagnostics):
        #    number_of_results = len(diagnostics)
        result_subjects = set()
        subject_mapped_results = dict()
        for result in diagnostics:
            if isinstance(result.get_subject(), types.StringTypes):
                result_subjects.add((result.get_subject_type(), result.get_subject()))
                try:
                    subject_mapped_results[result.get_subject()].append(result)
                except KeyError:
                    subject_mapped_results[result.get_subject()] = [result]
            else:
                for subject in result.get_subject():
                    result_subjects.add((result.get_subject_type(), subject))
                    try:
                        subject_mapped_results[subject].append(result)
                    except KeyError:
                        subject_mapped_results[subject] = [result]
        result_subjects = sorted(result_subjects)
        for (subject_type, result_subject) in result_subjects:
            diagnostics_list = sorted(((result.get_subject()),("%s: %s" %(self.__level_string(result.get_level()),result.get_message()))) for result in subject_mapped_results[result_subject])
            diagnostics_list = list((subject if isinstance(subject, types.StringTypes) else ', '.join(subject), message) for subject, message in diagnostics_list)
            if diagnostics_list:
                self.__output_file.write( """<h2>diagnostics for the %s %s</h2> \n"""%(subject_type, result_subject))           
                HTMLTableWriter(output_file=self.__output_file,
                        table_model=SimpleTableModel(column_names=["%s name"%subject_type, "%s diagnostic"%subject_type], data=diagnostics_list)).write_table()
                self.__output_file.write("""<hr/> \n""")  
    
    def write(self):
        if hasattr(self.__module_list_supply, "get_module_descriptors"):
            self._write_header()
            self._write_preamble()
            results = self.__module_list_supply.get_results()
            if self.__output_type==HTMLRuleListerOutputType.RESULTS_PER_RULE:
                self._write_per_rule(results)
            if self.__output_type==HTMLRuleListerOutputType.RESULTS_PER_SUBJECT:
                self._write_per_subject(results)
            if self.__output_type==HTMLRuleListerOutputType.RULE_OVERVIEW:
                self._write_rule_overview(self.__module_list_supply.get_checked_rules())
            self._write_postamble()
            self._write_tail()
            return True
        else:
            return False
