#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 07.09.2010

@author: SIGIESEC
'''
from base.basic_config_base import BasicConfigBase
from commons.os_util import PathTools
from configuration.revengtools_config import RevEngToolsConfigParser
import os.path
import warnings

class RevEngToolsBasicConfig(BasicConfigBase):
    def __init__(self):
        BasicConfigBase.__init__(self)
        self.__adaptee = RevEngToolsConfigParser()

    def get_revengtools_basedir(self):
        return RevEngToolsConfigParser.revengtools_basepath()

    def get_results_directory(self):
        return self.get_path(self.__adaptee, "RESULTS_DIR", BasicConfigBase.get_results_directory(self))

    @staticmethod
    def get_path(configparser, configvar, default=None):
        raw_directory = configparser.get(configvar, default)
        if PathTools.is_cygwin_directory(raw_directory):
            return PathTools.cygwin_to_cmd_path(raw_directory)
        else:
            return os.path.normcase(os.path.normpath(os.path.normcase(raw_directory)))
    
    def get_local_source_base_dir(self):
        return self.get_path(self.__adaptee, "LOCAL_SOURCE_BASE_DIR", BasicConfigBase.get_local_source_base_dir(self))
    
    def get_local_source_base_dir_subset(self):
        return self.__adaptee.get("LOCAL_SOURCE_BASE_DIR_SUBSET", ".").split(",")

    def get_local_binary_dir(self):
        return self.get_path(self.__adaptee, "LOCAL_BINARY_DIR", BasicConfigBase.get_local_binary_dir(self))

    def get_server_source_base_dir(self):
        """
        
        >>> RevEngToolsConfigParser().put("SERVER_SOURCE_BASE_DIR", "/cygdrive/D/SOURCE/test")
        >>> RevEngToolsBasicConfig().get_server_source_base_dir()
        'd:\\\\source\\\\test'
        """
        # TODO das sollte auch für mehrere Versionen funktionieren
        if self.__adaptee.has("SERVER_SOURCE_BASE_DIR"):
            return self.get_path(self.__adaptee, "SERVER_SOURCE_BASE_DIR")
        elif self.__adaptee.has("SOURCEBASEDIR"):
            warnings.warn("SERVER_SOURCE_BASE_DIR not defined, using deprecated SOURCEBASEDIR instead", DeprecationWarning)
            return self.get_path(self.__adaptee, "SOURCEBASEDIR")

    def _get_results_basedir(self):
        return self.get_path(self.__adaptee, "RESULTS_BASE_DIR", BasicConfigBase._get_results_basedir(self))
    
    def get_version(self):
        return self.__adaptee.get("VERSION")

    def get_system(self):
        return self.__adaptee.get("SYSTEM")
    
    def get_section_prefix(self):
        return self.__adaptee.get("SECTION_PREFIX", "")
    

