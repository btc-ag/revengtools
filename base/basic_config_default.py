'''
A very specific implementation of base.basic_config_if containing absolute local paths.

@deprecated: This should not be used and removed.

Created on 28.09.2010

@author: SIGIESEC
'''
from base.basic_config_base import BasicConfigBase

# TODO This does not make sense. is this used at all??? 

class BasicConfigDefault(BasicConfigBase):
    """
    >>> BasicConfigDefault().get_revengtools_basedir()
    'D:\\\\PRINS-Analyse\\\\workspace\\\\RevEngTools'
    >>> BasicConfigDefault().get_version_specific_config_path("test")
    'D:\\\\PRINS-Analyse\\\\workspace\\\\RevEngTools\\\\configuration\\\\config.prins.PRINS-PrinsAnalyse278.test'
    >>> BasicConfigDefault().get_version_specific_config_path("test")
    'D:\\\\PRINS-Analyse\\\\workspace\\\\RevEngTools\\\\configuration\\\\config.prins.PRINS-PrinsAnalyse278.test'
    >>> BasicConfigDefault().get_revengtools_basedir()
    'D:\\\\PRINS-Analyse\\\\workspace\\\\RevEngTools'
    """
        
    def get_local_source_base_dir(self):
        raise DeprecationWarning
        return "D:\\Dev\\src"

    def get_version(self):
        raise DeprecationWarning
        return "PRINS-PrinsAnalyse278"

    def get_system(self):
        raise DeprecationWarning
        return "prins"

if __name__ == "__main__":
    import doctest
    doctest.testmod()
