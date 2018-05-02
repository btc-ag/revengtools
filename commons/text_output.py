'''
Created on 07.07.2010

@author: mamigasi
'''

class PrettyTablePrinter(object):
    """
    Generates a more readable output of a table returned by execute
    method of a cursor 
    """
    # TODO: Calculate max column size per column!!
    
    def __init__(self, cursor):
        self.__cursor = cursor
        self.__descriptions = self.__cursor.description
        self.__max_col_len = None
        self.__pretty_table_new = None
        self.__rows_count = 0
        self.__generate()

    def __generate(self):    
        cell_values = self.__obtain_cell_values()
        self.__calculate_max_column_len(cell_values)
        headline = self.__create_table_headline()
        
        start = 0
        end = len(cell_values)
        step = self.__column_number()
        
        self.__pretty_table_new = [headline]
        for i in range(start, end, step) :
            for j in range(step) :
                self.__pretty_table_new.append(cell_values[ i + j ].ljust(self.__get_max_column_len()))
            
        self.__rows_count = (len(cell_values) / step) 

    def print_table(self):
        if self.__pretty_table_new == None:
            print "Error: Call __generate first"
        else:
            if self.__rows_count > 0:
                for line in self.__pretty_table_new:
                    print line
            print "Rows: %d" % self.__rows_count

    def __create_table_headline(self):
        headline = ""
        for description in self.__descriptions :
            headline += (description[ 0 ]).ljust(self.__get_max_column_len())
        return headline
            
    def __obtain_cell_values(self):
        results = []
        col_number = self.__column_number()
        
        for row in self.__cursor:
            for col in range(col_number):
                results.append(str(row[ col ]))
        return results

    def __get_max_column_len(self):
        if self.__max_col_len == None:
            self.__calculate_max_column_len(self.__obtain_cell_values())
        return self.__max_col_len

    def __calculate_max_column_len(self, _list):
        if len(_list) > 0:
            self.__max_col_len = max(map(len, _list)) + 1
        else:
            self.__max_col_len = 0

    def __column_number(self):
        return len(self.__cursor.description)

        
