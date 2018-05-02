#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 03.09.2010

@author: SIGIESEC
'''
from commons.bashconfig import BashConfigParser, ConfigurationNotFoundWarning
import logging
import os.path

# TODO Irgendwie alle verwendeten Konfigurationsvariablen abfragen

class RevEngToolsConfigParser:
    # Uses singleton implementation from http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/
    __instance = None
    
    @staticmethod
    def revengtools_basepath():
        return RevEngToolsConfigParser.__revengtools_basepath

    def load_config(self, config_basename):
        try:
            RevEngToolsConfigParser.__instance.read(config_basename)
            self.__logger.debug("config %s parse completed" % (config_basename, ))
        except ConfigurationNotFoundWarning:
            self.__logger.warning("config %s does not exist" % (config_basename))

    def __init__(self):        
        if RevEngToolsConfigParser.__instance == None:
            RevEngToolsConfigParser.__logger = logging.getLogger(self.__class__.__module__)
            RevEngToolsConfigParser.__instance = BashConfigParser()
            RevEngToolsConfigParser.__revengtools_basepath = os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))
            RevEngToolsConfigParser.__instance.set_config_basepath(os.path.join(self.revengtools_basepath(), 'configuration')) 
            RevEngToolsConfigParser.__instance.read(RevEngToolsConfigParser.__instance.get('CONFIG', 'config.default'))
            self.load_config('config.language.' + RevEngToolsConfigParser.__instance.get('LANGUAGE'))
            self.load_config('config.local')
            self.load_config('config.local.' + RevEngToolsConfigParser.__instance.get('SYSTEM'))
            self.load_config('config.local.' + RevEngToolsConfigParser.__instance.get('VERSION'))
        self.__dict__['_RevEngToolsConfigParser__instance'] = RevEngToolsConfigParser.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
