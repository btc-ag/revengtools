# -*- coding: UTF-8 -*-
'''
Created on 20.10.2010

@author: SIGIESEC
'''
from commons.os_util import PathTools
from cpp.header_linker_default import DefaultHeaderLinker
import posixpath

class CABHeaderLinker(DefaultHeaderLinker):

    @staticmethod
    def cpp_filename_new(header_filename):
        """
        >>> PRINSTools.cpp_filename_new('processvariable/eventtracerclient/include/client.h')
        'processvariable/eventtracerclient/src/client.cpp'

        >>> PRINSTools.cpp_filename_new('__prio4/_dyn/foo.h') == None
        True
        """
        # TODO assert that header_filename is a posixpath?
        header_dirname = posixpath.dirname(header_filename)
        if posixpath.basename(header_dirname) == 'include':
            return posixpath.join(posixpath.dirname(header_dirname),
                                  'src',
                                  PathTools.replace_extension(posixpath.basename(header_filename), '.cpp')
                                 )
        else:
            return None


    def _implementation_file_candidates_same_module(self, header):
        return DefaultHeaderLinker._implementation_file_candidates_same_module(self, header) + \
            [self.cpp_filename_new(header)]

    def _get_default_module(self, directory):
        # TODO das mit dem "/build"-Suffix ist ok, aber generell für cmake.
        # TODO das mit dem "btc/cab/"-Präfix ist problematisch, da sollte ein allgemeines Mapping stattfinden
        return DefaultHeaderLinker._get_default_module(self, 'btc/cab/' + directory + '/build')
    