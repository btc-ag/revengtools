# -*- coding: UTF-8 -*-
'''
Created on 13.10.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class SCMClientError(Exception):
    pass

class VersionDescriber(AutoConfigurable):
    def describe_local_version(self, basepath, detailed=True):
        """
        Returns a 3-tuple describing the version of the code in the directory basepath.
        The tuple has the following elements: 
        1. last modification time (an instance of datetime.datetime),
        2. a revision number (either as a number or a string),
        3. a string describing the version (e.g. repository version number).
        
        @param basepath: a path processable by os.path
        @param detailed: If detailed is true, the returned information is requested to be more 
            accurate and detailed. However, it may take longer to obtain the information, because 
            the whole directory tree might be scanned.
            
        @raise SCMClientError: If an error occurs during a SCM operation
        """
        raise NotImplementedError

    def update_to_date(self, basepath, date):
        raise NotImplementedError
    