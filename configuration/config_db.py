'''
Created on 06.09.2010

@author: SIGIESEC
'''
from configuration.revengtools_config import RevEngToolsConfigParser
from commons.database_if import DatabaseConfiguration, ConnectionFactory

config_factory_class = ConnectionFactory

class RevEngToolsDatabaseConfiguration(DatabaseConfiguration):
    def __init__(self):
        DatabaseConfiguration.__init__(self)
        self.__adaptee = RevEngToolsConfigParser()

    def get_connection_factory(self):
        return config_factory_class(self)

    def get_host(self):
        return self.__adaptee.get("DBHOST")

    def get_user(self):
        return self.__adaptee.get("DBUSER")

    def get_password(self):
        return self.__adaptee.get("DBPWD")

    def get_database(self):
        return self.__adaptee.get("KBNAME")
    
    
