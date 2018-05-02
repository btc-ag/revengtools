'''
An implementation of base.dependency.dependency_if_deprecated.DependencyParser that 
imports the output of BTC.CAB.Depends

Created on 31.03.2011

@author: SIGIESEC

@todo: This should be moved to the infrastructure package.
'''
from __future__ import with_statement
from base.dependency.dependency_if_deprecated import DependencyParser
from commons.configurator import ConfigurationError
from commons.core_util import StringTools
from commons.thread_util import Worker, ThreadPool
from subprocess import CalledProcessError
from threading import Lock
import logging
import os.path
import subprocess
import threading

class BinaryUtil(object):
    def is_binary(self, filename):
        raise NotImplementedError()

class WindowsBinaryUtil(BinaryUtil):
    @staticmethod
    def get_binary_extensions():
        return (".exe", ".dll") 

    def is_binary(self, filename):
        return filename.lower().endswith(WindowsBinaryUtil.get_binary_extensions())

class CABDependsWorker(Worker):
    def __init__(self, *args, **kwargs):
        Worker.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)

    def __process_data(self, filename, result, resultlock, mapper, stream):
        targets = set()
        source_name = mapper(filename)
        for target in stream:
            target_name = mapper(target)
            if source_name != target_name:
                targets.add(target_name)
        
        with resultlock: # With GIL, the lock is unnecessary, since the operation is guaranteed to be atomic
            result[source_name] = targets

    def _do_task(self, executable, filename, result, resultlock, binary_util):
        self.__logger.debug("Worker %s processes file %s", threading.currentThread().name, filename)
        cmdline = (executable, filename)
        process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, bufsize=1)
        mapper = lambda filename: StringTools.strip_suffixes(os.path.basename(filename.strip()), binary_util.get_binary_extensions(), ignore_case=True)
        self.__process_data(filename, result, resultlock, mapper, stream=process.stdout)
        process.wait()
        self.__logger.debug("%s: return value is %x", threading.currentThread().name, process.returncode)
        if process.returncode not in [0,255]:
            raise CalledProcessError(process.returncode, cmdline)
        self.__logger.debug("Worker %s finished processing directory %s", threading.currentThread().name, filename)
        self.__logger.debug("Remaining threads: %s", threading.enumerate())

class CABDependsDependencyParser(DependencyParser):
    NUM_THREADS=2
    # TODO: This depends on the environment. It could be retrieved by cab-get.
    CAB_BINARY_PATH = r'D:\PRINS-Analyse\CoreAssetBase\trunk-build\cab_win32_msvs9_vs_release_full\dst\Release'
    CAB_DEPENDS_BINARY_NAME = "BTC.CAB.Depends.EXE.exe"
    
    @staticmethod
    def __find_depends_executable():        
        depends_executable = os.path.join(CABDependsDependencyParser.CAB_BINARY_PATH, 
                                          CABDependsDependencyParser.CAB_DEPENDS_BINARY_NAME) #TODO
        if not os.path.exists(depends_executable):
            raise ConfigurationError("CAB Depends executable not found at %s" % depends_executable)
        return depends_executable

    def __init__(self, basic_config):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__dependencies = dict()
        self.__dependencies_lock = Lock()
        self.__depends_executable = self.__find_depends_executable()
        self.__binary_util = WindowsBinaryUtil()
        self.__binary_dir_resolver = basic_config.get_local_binary_resolver()
        
    def __walk(self, tp, dirname, filenames):
        for filename in filenames:
            if self.__binary_util.is_binary(filename): 
                tp.add_task(executable=self.__depends_executable, 
                            filename=os.path.join(dirname, filename), 
                            result=self.__dependencies, 
                            resultlock=self.__dependencies_lock,
                            binary_util=self.__binary_util)                    
    
    def process(self):
        dirs = self.__binary_dir_resolver.get_base_paths()
        self.__logger.info("Parsing binaries in %s" % dir)
        tp = ThreadPool(self.NUM_THREADS, CABDependsWorker)
        for dir in dirs:
            os.path.walk(dir, self.__walk, tp)
        tp.shutdown()
        tp.wait_completion()
    
    def __get_dependencies(self):
        return self.__dependencies.iteritems()

    def output(self, outputter):
        for (source, targets) in self.__get_dependencies():
            for target in targets:
                outputter.dependency(source, target) 
        outputter.postamble()
    
# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
