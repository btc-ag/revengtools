#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Implementations of the commons.config_extension_if.Configuration interface
that are based on shell/environment variables and bash-parsable files containing
shell/environment variable definitions. 
"""

from commons.config_extension_if import Configuration
from string import Template
import csv
import logging
import os
import warnings

class ConfigurationNotFoundWarning(Exception):
    pass

class EnvironmentConfiguration(Configuration):
    def __init__(self):
        Configuration.__init__(self)
        self.__configDict = dict()
        self.__configDict_combined = None

    def _combined_dict(self):
        if self.__configDict_combined == None:
            self.__configDict_combined = self.__configDict.copy()
            self.__configDict_combined.update(os.environ)
        return self.__configDict_combined

    def get(self, key, default=None):
        rawString = self._combined_dict().get(key, default)
        # TODO: Template-Ersetzung müsste ggf. wiederholt angewendet 
        #      werden, bis keine Ersetzung mehr stattfindet
        if rawString != None:
            return Template(rawString).substitute(self._combined_dict())
        else:
            return None

    def put(self, key, value):
        """
        >>> parser = EnvironmentConfiguration()
        >>> parser.has('foo')
        False
        >>> parser.put('foo', 'bar')
        >>> parser.has('foo')
        True
        >>> parser.get('foo')
        'bar'
        """
        self.__configDict.update({key: value})
        self.__configDict_combined = None

    def has(self, key):
        return self._combined_dict().has_key(key)
        

class BashConfigParser(EnvironmentConfiguration):
    """
    Implementation of commons.config_extension_if.Configuration that parses 
    bash-style scripts that contain definitions of shell/environment variables 
    """
    
    # TODO this should not inherited from EnvironmentConfiguration, but should
    # be replaced by a class only parsing the files plus a factory method 
    # creating a combined EnvironmentConfiguration/BashConfigParser
    
    COMMENT_LINE_SIGN = '#'
    
    KEY_FIELD = 'key'
    VALUE_FIELD = 'value'

    def __init__(self, config_file=None):
        EnvironmentConfiguration.__init__(self)
        self.__config_basepath = os.curdir
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.setLevel(logging.WARNING) #TODO
        if config_file != None:
            self.read(config_file)
            
    def set_config_basepath(self, basepath):
        self.__config_basepath = basepath
        
    def get_config_basepath(self):
        return self.__config_basepath
            
    def add(self, key, value):
        warnings.warn("use put instead", DeprecationWarning)
        self.put(key, value)

    def __create_csv_reader(self, config_file):
        return csv.DictReader(config_file, delimiter='=', 
            fieldnames=[self.KEY_FIELD, self.VALUE_FIELD])

    def __open_bash_file(self, config_path):
        if not os.path.exists(config_path):
            raise ConfigurationNotFoundWarning("Configuration file %s does not exist" % config_path)
        else:
            config_file = open(config_path, "r")
            return self.__create_csv_reader(config_file)

    def __process_line(self, line, config_rel_to_basepath):
        if line[self.VALUE_FIELD] != None:
            self.put(line[self.KEY_FIELD], line[self.VALUE_FIELD])
        elif line[self.KEY_FIELD].startswith('.') or line[self.KEY_FIELD].startswith('source'):
            # TODO use posixpath instead
            pathParts = line[self.KEY_FIELD].rpartition('/')
            # TODO das funktioniert so nur, wenn die Datei direkt in configuration liegt
            sub_config = pathParts[len(pathParts) - 1]
            self.read(sub_config)
        else:
            self.__logger.debug("Invalid config line in file %s: %s", config_rel_to_basepath, line)

    def __process_lines(self, config_lines, config_rel_to_basepath = None):
        for line in config_lines:
            self.__logger.debug("Processing config line %s", line)
            if not line[self.KEY_FIELD].startswith(self.COMMENT_LINE_SIGN):
                self.__process_line(line, config_rel_to_basepath)
    
    def read_list(self, config_lines):
        """
        >>> parser = BashConfigParser()
        >>> lines = ['foo=bar', '#bar=foo']
        >>> parser.read_list(lines)
        >>> parser.get('foo')
        'bar'
        >>> parser.has('bar')
        False
        """
        config_lines = self.__create_csv_reader(config_lines)
        self.__process_lines(config_lines)        

    def read(self, config_rel_to_basepath_or_abspath):
        self.__logger.debug("Processing config file %s", config_rel_to_basepath_or_abspath)
        if os.path.isabs(config_rel_to_basepath_or_abspath):
            config_path_rel_to_curdir = config_rel_to_basepath_or_abspath
        else:
            config_path_rel_to_curdir = os.path.join(self.__config_basepath, config_rel_to_basepath_or_abspath)
        config_lines = self.__open_bash_file(config_path_rel_to_curdir)
        self.__process_lines(config_lines, config_rel_to_basepath_or_abspath)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
