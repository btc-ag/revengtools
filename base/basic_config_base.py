'''
A base implementation of base.basic_config_if.

Created on 28.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.os_util import FixedBaseDirPathResolver
import os.path
import sys

class BasicConfigBase(BasicConfig):
    def get_local_source_resolver(self):
        return FixedBaseDirPathResolver(self.get_local_source_base_dir())        

    def get_local_binary_resolver(self):
        return FixedBaseDirPathResolver(self.get_local_binary_dir())        

    def get_revengtools_basedir(self):
        return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(sys.modules[BasicConfigBase.__module__].__file__)), os.path.pardir))

    def _get_results_basedir(self):
        return os.path.normpath(os.path.join(self.get_revengtools_basedir(), os.path.pardir, "Results"))
    
    def get_config_dir(self):
        return os.path.join(self.get_revengtools_basedir(), "configuration")    

    def get_results_directory(self):
        return os.path.join(self._get_results_basedir(), self.get_version())
    
    def get_version_specific_config_path(self, basename):
        return os.path.join(self.get_config_dir(), "config.%s.%s.%s" % (self.get_system(), self.get_version(), basename))
