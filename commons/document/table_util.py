'''
Created on 17.05.2012

@author: SIGIESEC
'''
from itertools import izip,repeat
from commons.document.table_if import TableModel

class SimpleTableModel(TableModel):
    def __init__(self, column_names, data, *args, **kwargs):
        TableModel.__init__(self, *args, **kwargs)
        self.__column_names = list(column_names)
        self.__data = data

    def get_cell_content(self, cell_content):
        return cell_content

    def get_data_columns(self, row_entries):
        return row_entries

    def get_column_headers(self):
        return self.__column_names

    def get_rows(self):
        return izip(repeat(None), self.__data)

    def has_row_headers(self):
        return False
