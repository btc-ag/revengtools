# -*- coding: UTF-8 -*-
'''
Created on 26.10.2010

@author: SIGIESEC
'''
from commons.document.basic_if import DocumentModel

class TableModel(DocumentModel):
    def get_cell_content(self, cell_content):
        raise NotImplementedError

    def get_row_header_text(self, keyval):
        raise NotImplementedError

    def get_data_columns(self, row_entries):
        """
        
        @param row_entries:
        """
        raise NotImplementedError

    def get_column_headers(self):
        raise NotImplementedError

    def get_rows(self):
        raise NotImplementedError
    
    def has_row_headers(self):
        raise NotImplementedError
        

class TableWriter(object):
    def __init__(self, output_file, table_model):
        """
        Creates a TableWriter object.
        
        @param output_file: a file
        @param table_model: a TableModel
        """
        pass

    def write_table(self, sortable=False):
        raise NotImplementedError

