# -*- coding: UTF-8 -*-
'''
Created on 22.09.2010

@author: SIGIESEC
'''

from base.basic_config_if import BasicConfig
from cpp.incl_deps.include_deps_if import IncludeDependencyGenerator
import os
import os.path

config_basic = BasicConfig()

class CdepIncludeDependencyGeneratorBase(IncludeDependencyGenerator):
    def __init__(self):
        IncludeDependencyGenerator.__init__(self)
        # TODO remove the fallback
        self.__cdep_path = os.environ.get("CDEP_PROGRAM")
        if self.__cdep_path is None:
          self.__cdep_path = os.path.join(config_basic.get_revengtools_basedir(), 
                                          "cpp", "idep", "cdep.exe")
        self.__include_path_temp_filename = None

    def _remove_include_path_temp_file(self):
        if self.__include_path_temp_filename != None:
            if os.path.exists(self.__include_path_temp_filename):
                os.unlink(self.__include_path_temp_filename)
            self.__include_path_temp_filename = None
        
    def _generate_include_path_temp_file(self):
        (tmpfile_handle, self.__include_path_temp_filename) = mkstemp() 
        # TODO wenn man mkstemp(text=True) verwendet, werden die Zeilenumbrüche anders geschrieben und
        # idep kommt damit nicht zurecht!
        tmpfile = os.fdopen(tmpfile_handle, "w")
        for directory in get_default_include_path_mapping().get_include_directories():
            self.__logger.debug("Adding include directory %s" % (directory, ))
            print >>tmpfile, directory
        tmpfile.close()

    def get_include_path(self, directory):
        # TODO das ist zum Teil CAB/PRINS-Spezifisch, schadet aber vermutlich i.d.R. auch nicht. 
        return ['.',
                directory,
                #os.path.normpath(os.path.join(directory, os.path.pardir, 'include')),
                ]

    def _get_cdep_program(self):
        return self.__cdep_path

    def _get_cmdline(self, directory, input_files):
        """
        >>> gen = CdepIncludeDependencyGeneratorBase()
        >>> gen._get_cmdline('_dyn', ['_dyn/foo.c']).replace(gen._get_cdep_program(), "$CDEP")
        '$CDEP -I. -I_dyn -iNone _dyn/foo.c -x'
        """
        include_path = self.get_include_path(directory)
        cmdline = "%s %s -i%s %s -x" % \
                    (self.__cdep_path,
                     " ".join("-I%s" % include_dir for include_dir in include_path),
                     self.__include_path_temp_filename,
                     " ".join(input_files),
                    )
        return cmdline

    def __del__(self):
        self.__remove_include_path_temp_file()
        

