# -*- coding: UTF-8 -*-

'''
Created on 27.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.dependency.dependency_if_deprecated import DependencyParser
from base.modules_if import ModuleListSupply
from python.depgraph2dot import pydepgraphdot
from python.py2depgraph import mymf
from python.python_util import PythonTools
import imp
import logging
import os.path
import pprint
import sys

config_basic = BasicConfig()

def parent(fqname):
    parts = fqname.split('.')
    return '.'.join(parts[0:len(parts) - 2])
    
class Dummy(object):
    def __init__(self, fqname):
        self.__fqname = fqname
        
    def read(self):
        return "import %s" % self.__fqname
        
class PydepProcessor(object):
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__mf = None
        self.__start = None
        
    def types(self):
        return self.__mf._types
    
    def valid_path(self, path):
        return path.find("-") == -1


    def is_valid_module_name(self, fqname):
        # TODO this is just a workaround, check how to check for valid module name
        return not " " in fqname
    
    
    def process(self, paths):
        path = sys.path[:]
        debug = 0
        exclude = []
        self.__mf = mymf(path, debug, exclude)
        self.__start = []
        for path in filter(self.valid_path, paths):
            self.__logger.info("Processing %s" % path)
            if os.path.exists(path):
                if os.path.split(os.path.normpath(path))[0] != '':
                    name, ext = os.path.splitext(os.path.normpath(path))
                    name = name.replace(os.path.sep, ".")
                    fqname = name.replace(".%s" % os.path.sep, "")
                    if not self.is_valid_module_name(fqname):
                        self.__logger.warning("Invalid module name %s, skipping" % fqname)
                    else:
                        self.__start.append(fqname)
                        #fp = open(path, READ_MODE)
                        stuff = ext, "r", imp.PY_SOURCE #mf.load_package(parent(fqname), os.path.dirname(path))
                        m = self.__mf.load_module("dummy", Dummy(fqname), "dummy.py", stuff)
                        #logging.info("Found module %s" % m.__name__)
                else:
                    self.__mf.load_file(path)
                    name, ext = os.path.splitext(os.path.normpath(path))
                    self.__start.append(name)
                    self.__logger.info("Found file %s" % path)
            else:
                self.__logger.error("not found")
        
        self.__logger.debug(pprint.pformat(self.__mf._depgraph))


    def output(self, filter):
        pydepgraphdot(self.__mf._depgraph, self.__mf._types, filter=filter).render(self.__start)

config_module_list_supply = ModuleListSupply()

class PythonDependencyParser(DependencyParser):
    def __init__(self):
        self.__runner = None
        self.__logger = logging.getLogger(self.__class__.__module__)

    def process(self):
        module_list = config_module_list_supply.get_module_list()
        os.chdir(config_basic.get_local_source_base_dir())
        self.__logger.debug("current dir is %s" % (os.getcwd(), ))
        self.__runner = PydepProcessor()
        self.__runner.process(paths=[PythonTools.get_filename_for_module(modulename) 
                                     for modulename in module_list])

    def output(self, outputter):
        # TODO Basismodule und Module ohne Package sollten unterschieden werden
        self.__runner.output(filter=outputter)




if __name__ == "__main__":
    import doctest
    doctest.testmod()
