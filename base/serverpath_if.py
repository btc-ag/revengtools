#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 20.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

# TODO dies sollte weitegehend ersetzt werden durch eine passende Konfiguration von ResourceResolvern

class ServerPath(AutoConfigurable):
    @staticmethod
    def is_server_path(server_path):
        raise NotImplementedError        
    
    @staticmethod
    def server_path_to_basename(server_path):
        raise NotImplementedError

    @staticmethod
    def relative_to_server_path(relative_path):
        raise NotImplementedError
    
    @staticmethod
    def server_to_relative_path(server_path):
        raise NotImplementedError
    
    @staticmethod
    def server_to_local_path(server_path):
        raise NotImplementedError
    
