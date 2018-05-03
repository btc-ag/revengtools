'''
The interface for the basic configuration options used throughout the RevEngTools.

Created on 06.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.os_util import ResourceResolver, LocalPathResolver #@UnusedImport: return type
import os.path
import sys

# TODO Do not provide default implementations of the methods here (especially not such that refer to Simon's notebook)

# TODO perhaps the interface (not necessarily its implementation) could be split up further.

class BasicConfig(AutoConfigurable):
    """
    @todo: Replace all methods returning directory paths by methods returning resolvers, and 
        those returning file paths by methods returning Resources 
    """
    def get_local_source_base_dir(self):
        """
        @deprecated: use get_local_source_resolver.get_base_paths instead
        """        
        return "D:\\Dev\\src"

    def get_local_source_base_dir_subset(self):
        raise NotImplementedError(self.__class__)

    def get_local_source_resolver(self):
        """
        @rtype: commons.os_util.LocalPathResolver
        @todo: the return type could be changed to URIResolver
        @todo: currently, this returns a resolver corresponding only to get_local_source_base_dir, and 
            is indifferent to get_local_source_base_dir_subset. This could be improved. 
        """
        raise NotImplementedError(self.__class__)        

    def get_local_binary_dir(self):
        """
        @deprecated: Use get_local_binary_resolver
        """
        return r'D:\Dev\cab_win32_msvs9_vs_release_full\dst\Release'
    
    def get_local_binary_resolver(self):
        raise NotImplementedError(self.__class__)        

    def get_version(self):
        return "PRINS-PrinsAnalyse278"
    
    def get_revengtools_basedir(self):
        return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(sys.modules[BasicConfig.__module__].__file__)), os.path.pardir))

    def get_config_dir(self):
        return os.path.join(self.get_revengtools_basedir(), "configuration")    

    def get_results_directory(self):
        raise NotImplementedError(self.__class__)

    def get_system(self):
        return "prins"
    
    def get_version_specific_config_path(self, basename):
        return os.path.join(self.get_config_dir(), "config.%s.%s.%s" % (self.get_system(), self.get_version(), basename))

    def get_section_prefix(self):
        return ""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
