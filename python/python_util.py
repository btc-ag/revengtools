'''
Contains static utility methods concerned with Python modules and packages. 

Created on 28.09.2010

@author: SIGIESEC
'''
import os.path

class PythonTools(object):
    @staticmethod
    def get_package_name(module):
        """
        >>> PythonTools.get_package_name('foo')
        ''
        >>> PythonTools.get_package_name('bar.foo')
        'bar'
        """
        prefix = ''
        if module != None:
            end_index = module.rfind('.')
            if end_index != -1:
                prefix = module[:end_index]
        return prefix

    @staticmethod
    def get_filename_for_module(modulename):
        """
        >>> PythonTools.get_filename_for_module('commons.test')
        'commons\\\\test.py'
        """
        return "%s.py" % (modulename.replace(".", os.path.sep),)
    
    @staticmethod
    def get_module_for_filename(filename):
        """
        >>> PythonTools.get_module_for_filename('commons/test.py')
        'commons.test'
        """
        
        return os.path.normpath(filename).replace(".py", "").replace(os.path.sep, ".")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
