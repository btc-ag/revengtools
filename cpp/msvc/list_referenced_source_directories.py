'''
Created on 01.04.2011

@author: SIGIESEC
'''
import csv
import os.path
import sys

class InputListParser(object):
    def __init__(self, deps_iter, csproj_to_base_dir):
        self.__csproj_to_base_dir = csproj_to_base_dir
        self.__module_to_directory_map = dict()
        self.__module_dependencies = dict()
        self.__parse(deps_iter)        
        
    def __parse(self, deps_iter):
        for (source, target) in deps_iter:
            if target.lower().endswith('.csproj'):
                self.__module_to_directory_map[source] = self.__csproj_to_base_dir(target)
            else:
                pass
            
    def get_module_to_directory_items(self):
        return self.__module_to_directory_map.iteritems()
    
    def get_module_directory_iter(self):
        raise NotImplementedError(self.__class__)
            
    def get_module_dependencies_iter(self):
        return iter(self.__module_dependencies)

class InputStreamParser(object):
    def __init__(self, stream, csproj_to_base_dir):
        reader = csv.reader(stream, delimiter=":")
        self.__parser = InputListParser(reader, csproj_to_base_dir)
        
    def __getattr__(self, attrib):
        return getattr(self.__parser, attrib)
        
        

def main():
    # TODO !!!
    basedir = r"D:\PRINS-Analyse\CoreAssetBase.Net\BTC\TimeSeries\build"
    parser = InputStreamParser(sys.stdin, lambda x: os.path.normpath(os.path.join(basedir, os.path.dirname(x), "..")))
    for (module, directory) in parser.get_module_to_directory_items():
        print module, directory

if __name__ == "__main__":
    main()
