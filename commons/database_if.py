#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 07.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class DatabaseConfiguration(AutoConfigurable):
    def __init__(self):
        self.__connection = None
    
    def get_host(self):
        raise NotImplementedError(self.__class__)
    
    def get_user(self):
        raise NotImplementedError(self.__class__)
        
    def get_password(self):
        raise NotImplementedError(self.__class__)

    def get_database(self):
        raise NotImplementedError(self.__class__)
    
    def get_connection_factory(self):
        raise NotImplementedError(self.__class__)
    
    def get_connection(self):
        # TODO use global connection pool
        if self.__connection == None:
            self.__connection = self.get_connection_factory().get_connection()            
        return self.__connection
    
class ConnectionFactory(AutoConfigurable):
    def get_connection(self):
        raise NotImplementedError(self.__class__)
                
class SimpleSQLExecutor(object):
    # TODO das Interface ist nicht gut. Nur um ein SQL-Statement auszuführen, muss man eine Methode überschreiben. 
    # Es sollte lediglich eine Methode geben, die als Parameter das SQL-Kommando übergeben bekommt und als Ergebnis 
    # den Cursor liefert. 
    
    def __init__(self, config_database):
        self.__connection = None
        self._sql_query = None
        self._cursor = None 
        self.__initialize_db(config_database)
    
    def __del__(self):
        #self.__connection.close()
        pass
    
    def __initialize_db(self, config_database):
        self.__connection = config_database.get_connection()
        self._cursor = self.__connection.cursor()

    def _create_sql_statement(self,
                            object_types_accessors,
                            object_types_variable,
                            link_types,
                            object_name):
        raise NotImplementedError(self.__class__)

    def prepare_sql_statement(self, object_name):
        """
        Override this method and pass the correct arguments to _create_sql_statement
        """
        raise NotImplementedError(self.__class__)
    
    def run(self, object_name):
        self.prepare_sql_statement(object_name)
        self._cursor.execute(self._sql_query)
        
    def get_result(self):
        return self._cursor
    
    

