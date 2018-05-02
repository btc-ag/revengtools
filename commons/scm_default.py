# -*- coding: UTF-8 -*-
'''
Created on 19.10.2010

@author: SIGIESEC
'''
from commons.scm_if import VersionDescriber
import datetime
import logging

class FaultFreeVersionDescriber(VersionDescriber):
    pass

class NullVersionDescriber(FaultFreeVersionDescriber):
    """
    Never throws an exception on any operation.
    """

    def describe_local_version(self, basepath, detailed=True):
        return (datetime.datetime.now(), 0, 'unknown version')

    def update_to_date(self, basepath, date):
        pass

class FallbackVersionDescriber(FaultFreeVersionDescriber):
    def __init__(self, first_decriber, fallback_describer=NullVersionDescriber()):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__describers = list()
        self.__describers.append(first_decriber)
        self.__describers.append(fallback_describer)
    
    def describe_local_version(self, basepath, detailed=True):
        for desc in self.__describers:
            try:
                return desc.describe_local_version(basepath, detailed)
            except Exception:
                self.__logger.warning("SCM Describer %s failed, using fallback", desc.__class__, exc_info=1)

    def update_to_date(self, basepath, date):
        for desc in self.__describers:
            try:
                return desc.update_to_date(basepath, date)
            except Exception:
                self.__logger.warning("SCM Describer %s failed, using fallback", desc.__class__, exc_info=1)
