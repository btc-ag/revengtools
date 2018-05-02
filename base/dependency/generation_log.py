# -*- coding: UTF-8 -*-
'''
Created on 23.10.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.dependency.dependency_if import GraphDescription
from base.dependency.generation_log_if import (GenerationLogGenerator, 
    GenerationLogSupply)
from commons.core_if import EnumerationItem, Enumeration
from commons.core_util import IterTools, List
from commons.document.basic_if import Link
from commons.document.renderers.html import HTMLText
from commons.document.table_if import TableModel
from commons.os_util import FileTools
from commons.v26compat_util import compatrelpath
from itertools import ifilter
import csv
import logging
import os.path
import urllib
import weakref

config_basic = BasicConfig()

class GenerationLogColumn(EnumerationItem):
    pass

class GenerationLogColumns(Enumeration):
    _type = GenerationLogColumn
    SECTION = GenerationLogColumn()
    CATEGORY = GenerationLogColumn()
    DESCRIPTION = GenerationLogColumn()
    EXTRA = GenerationLogColumn()
    FILENAME = GenerationLogColumn()
    
class NullGenerationLogGenerator(GenerationLogGenerator):

    def add_generated_file(self, description, filename=None):
        pass

class CSVGenerationLogConstants(object):

    FILENAME = 'generated_graphs.csv'

    @staticmethod
    def get_generation_log_filename():
        return os.path.join(config_basic.get_results_directory(),
                            CSVGenerationLogConstants.FILENAME)

class CSVGenerationLogGenerator(GenerationLogGenerator):
    """
    A generation log generator implementation which stores its data in a CSV file.
    
    @attention: Do not run concurrent processes that try to write to the same 
      CSV file. This cannot be guaranteed to be synchronized correctly. 
    """

    def __init__(self, *args, **kwargs):
        GenerationLogGenerator.__init__(self, *args, **kwargs)
        self.__log = None
        self.__logger = logging.getLogger(self.__class__.__module__)

    def __open_log(self):
        # TODO check if the object returned by csv.writer is thread-safe
        
        log_filename = CSVGenerationLogConstants.get_generation_log_filename()
        self.__log = csv.writer(open(log_filename, "ab"))

    def add_generated_file(self, description, filename=None):
        if description == None:
            self.__logger.warning("Description is None")
            return
        assert isinstance(description, GraphDescription), description
        if filename == None:
            filename = description.get_filename()

        if not self.__log:
            self.__open_log()

        relative_path = compatrelpath(filename, config_basic.get_results_directory())
        self.__log.writerow([description.get_section(),
                             description.get_category(),
                             description.get_description(),
                             description.get_extra(),
                             relative_path])

class CSVGenerationLogSupply(GenerationLogSupply):
    def __init__(self):
        self.__generation_log = lambda: None
        self.__logger = logging.getLogger(self.__class__.__module__)

    def __read_generation_log(self):
        generation_log = List(FileTools.create_csv_dict_reader(
                                          filename=CSVGenerationLogConstants.get_generation_log_filename(),
                                          what="graph generation log",
                                          fieldnames=(GenerationLogColumns.SECTION,
                                                      GenerationLogColumns.CATEGORY,
                                                      GenerationLogColumns.DESCRIPTION,
                                                      GenerationLogColumns.EXTRA,
                                                      GenerationLogColumns.FILENAME),
                                          allow_missing=True,
                                          )
                                    )
        self.__generation_log = weakref.ref(generation_log, 
                           lambda _x: self.__logger.debug("generation log got garbage collected"))
        return generation_log

    def get_generation_log_iter(self):
        generation_log = self.__generation_log()
        if generation_log == None:
            generation_log = self.__read_generation_log()
        return iter(generation_log)

class GenerationLogTableModel(TableModel):

    def __init__(self, entries, *args, **kwargs):
        TableModel.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__entries = entries

    def _get_entry(self, entry, typestr=None):
        if typestr == None:
            (_basename, ext) = os.path.splitext(entry[GenerationLogColumns.FILENAME])
            typestr = ext.strip('.').upper()

        return Link(link_target=urllib.pathname2url(entry[GenerationLogColumns.FILENAME]),
                    text=typestr)
        
    SKIP_EXTENSIONS = set(['.dot', '.csv', ''])

    def get_cell_content(self, cell_content):
        generation_log_entries = cell_content
        output_content = list()
        for entry in generation_log_entries:
            basename, ext = os.path.splitext(entry[GenerationLogColumns.FILENAME])
            if ext not in self.SKIP_EXTENSIONS:
                typestr = ext.strip('.').upper()
                _basename, ext2 = os.path.splitext(basename.lower())
                if ext2 == '.l' or ext2 == '.p':
                    typestr += ' (%s)' % ext2.strip('.')
                output_content.append(self._get_entry(entry, typestr=typestr))
#                if ext == '.svg': 
#                    # TODO temporarily also write landscape&portrait PDF versions
#                    # this is an implicit dependency to process_hudson.sh
#                    entry[GenerationLogColumns.FILENAME] = 'wide/' + basename + '.pdf'
#                    output_content.append(self._get_entry(entry, typestr='PDF (l)'))
#                    entry[GenerationLogColumns.FILENAME] = 'high/' + basename + '.pdf'
#                    output_content.append(self._get_entry(entry, typestr='PDF (p)'))

        # TODO hm...
        return sorted(set(output_content), key=lambda x: x.get_text())

    def get_row_header_text(self, keyval):
        return "%s %s" % (keyval[0], # == GenerationLogColumns.DESCRIPTION
            keyval[1]) # == GenerationLogColumns.EXTRA

    def __get_column_definitions(self):
        return [("Overview", 'overview'),
                ("Details", ''),
                (HTMLText("Details<br/>(w/o transitive deps.)"), 'tr'),
                ("Report", 'report'),
                ]

    def get_column_headers(self):
        return zip(*self.__get_column_definitions())[0]

    def get_column_categories(self):
        return zip(*self.__get_column_definitions())[1]

    def get_rows(self):
        return IterTools.sort_and_group_dicts([GenerationLogColumns.DESCRIPTION,
                                               GenerationLogColumns.EXTRA], 
                                              self.__entries)

    def get_data_columns(self, row_entries_iter):
        # iterator must be materialized since it is consumed multiple types. could be changed by 
        # using sort_and_group_dicts
        row_entries = list(row_entries_iter)
        return (ifilter(lambda x:x[GenerationLogColumns.CATEGORY] == category, row_entries)
                for category in self.get_column_categories())

    def has_row_headers(self):
        return True
    
    @staticmethod
    def generation_log_group_models_factory(generation_log):
        key_column = GenerationLogColumns.SECTION
        groups = IterTools.sort_and_group_dicts(key_column, generation_log)
        return ((key, GenerationLogTableModel(group)) 
                for (key, group) in groups) 
    

