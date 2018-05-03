# -*- coding: UTF-8 -*-
'''
Created on 22.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.os_util import PathTools
from commons.progress_if import ProgressListener
from commons.thread_util import UnTeeWorkerBase, UnTeeHelper
from cpp.cpp_if import CppDataSupply, FileToModuleMapSupply
from cpp.cpp_util_wrap import get_default_include_path_mapping
from cpp.incl_deps.include_deps_if import IncludeDependencyGenerator
from itertools import chain
from subprocess import CalledProcessError
from tempfile import mkstemp
import logging
import os.path
import posixpath
import subprocess
import sys
import threading

config_basic = BasicConfig()
config_cpp_data_supply = CppDataSupply
config_file_to_module_map_supply = FileToModuleMapSupply
config_progress_listener = ProgressListener

class CdepUnTeeWorker(UnTeeWorkerBase):
    def __init__(self, *args, **kwargs):
        UnTeeWorkerBase.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def _do_task(self, directory, tcidp):
        self.__logger.debug("Worker %s processes directory %s", threading.currentThread().name, directory)
        tcidp.generate_dir(directory, self._get_write_fd())
        #os.write(self._get_write_fd(), "bla")
        self.__logger.debug("Worker %s finished processing directory %s", threading.currentThread().name, directory)
        self.__logger.debug("Remaining threads: %s", threading.enumerate())
        

class ThreadedCdepIncludeDependencyGenerator(IncludeDependencyGenerator):
    NUM_THREADS = 80
    
    def __init__(self):
        IncludeDependencyGenerator.__init__(self)
        self.__cdep_path = os.path.join(config_basic.get_revengtools_basedir(), 
                                        "cpp", "idep", "cdep.exe")
        self.__directory_to_file_map = None
        self.__file_count = 0
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__include_path_temp_filename = None
        self.__progress_listener = config_progress_listener()

    def __del__(self):
        self.__remove_include_path_temp_file()
        
    def __remove_include_path_temp_file(self):
        if self.__include_path_temp_filename != None:
            if os.path.exists(self.__include_path_temp_filename):
                os.unlink(self.__include_path_temp_filename)
            self.__include_path_temp_filename = None
        
    def __generate_include_path_temp_file(self):
        (tmpfile_handle, self.__include_path_temp_filename) = mkstemp() 
        # TODO wenn man mkstemp(text=True) verwendet, werden die Zeilenumbrüche anders geschrieben und
        # idep kommt damit nicht zurecht!
        tmpfile = os.fdopen(tmpfile_handle, "w")
        for directory in get_default_include_path_mapping().get_include_directories():
            self.__logger.debug("Adding include directory %s" % (directory, ))
            print >>tmpfile, directory
        tmpfile.close()

    def generate(self):
        self.__generate_include_path_temp_file()
        os.chdir(config_basic.get_local_source_base_dir())
        directories = self.__get_directories()
        self.__progress_listener.set_total(len(directories))

        (tp, untee) = UnTeeHelper.setup_untee(self.NUM_THREADS, CdepUnTeeWorker, sys.stdout)
        for directory in directories:
            tp.add_task(directory=directory, tcidp=self)
        tp.shutdown()
        #tp.wait_completion()
        untee.join()

        # TODO:   self.__progress_listener.increment(1)
        self.__remove_include_path_temp_file()

    def get_include_path(self, directory):
        # TODO das ist zum Teil CAB/PRINS-Spezifisch, schadet aber vermutlich i.d.R. auch nicht. 
        return ['.',
                directory,
                os.path.normpath(os.path.join(directory, os.path.pardir, 'include'))]


    def _get_cmdline(self, directory, input_files):
        """
        >>> DirwiseCdepIncludeDependencyGenerator()._get_cmdline('_dyn', ['_dyn/foo.c'])
        'D:\\\\PRINS-Analyse\\\\workspace\\\\RevEngTools\\\\cpp\\\\idep\\\\cdep.exe -I. -I_dyn -Iinclude -iNone _dyn/foo.c -x'
        """
        include_path = self.get_include_path(directory)
        cmdline = \
                    chain((self.__cdep_path,),
                     ("-I%s" % include_dir for include_dir in include_path),
                     ("-i%s" % self.__include_path_temp_filename, ),
                     input_files,
                     ("-x",)
                    )
        return list(cmdline)


    @staticmethod
    def split_into_two_halves(input_files):
        """
        >>> input_files=[1,2,3]
        >>> two_halves = DirwiseCdepIncludeDependencyGenerator.split_into_two_halves(input_files)
        >>> list(two_halves[0] + two_halves[1]) == input_files
        True
        >>> list(two_halves[0])
        [1]
        """
        split_point = len(input_files) / 2
        two_halves = input_files[:split_point], input_files[split_point:]
        return two_halves

    def generate_for_input_files_in_dir(self, directory, input_files, outfile):
        input_files = list(input_files)
        if len(input_files) == 0:
            self.__logger.warning("No input files for directory %s", directory)
            return
        cmdline = self._get_cmdline(directory, input_files)
        if len(cmdline) + sum(map(len, cmdline)) > 8190:
            self.__logger.info("cmdline too long, splitting for directory %s" % (directory, ))
            two_halves = self.split_into_two_halves(input_files)
            for portion in two_halves:
                self.generate_for_input_files_in_dir(directory, portion, outfile)
        else:
            self.__logger.debug("%s: calling %s", threading.currentThread().name, cmdline)
            if False:
                cmdline = ['D:\\cygwin\\bin\\bash.exe', "--login", 
                           "-c", "cd %s" % (posixpath.join(config_basic.get_local_source_base_dir().replace("\\", "/"), directory)), 
                           "-c", " ".join(PathTools.native_to_posix(x) for x in cmdline)]
            retval = subprocess.call(cmdline, stdout=outfile)
            self.__logger.debug("%s: return value is %x", threading.currentThread().name, retval)
            if retval not in [0,255]:
                raise CalledProcessError(retval, cmdline)

    def generate_dir(self, directory, outfile): 
        input_files = self.__get_files(directory)
        self.__logger.debug("Generating include deps for %i files in directory %s" % (len(input_files), directory))
        
        if len(input_files) > 0:
            self.generate_for_input_files_in_dir(directory, input_files, outfile)

    def __add_path(self, path):
        dirname = os.path.dirname(path)
        if dirname not in self.__directory_to_file_map:
            self.__directory_to_file_map[dirname] = set()
        self.__directory_to_file_map[dirname].add(path)
        self.__file_count += 1

    def __generate_directory_to_file_map(self):
        self.__logger.debug("Generating directory to file map")
        self.__directory_to_file_map = dict()
        # read headerlist
        header_files = config_cpp_data_supply().get_header_list()
        for path_line in header_files:
            self.__add_path(path_line[0])
            
        # read vcproj_to_implementation_files
        implementation_files = config_file_to_module_map_supply().get_module_to_implementation_file_map()
        for path_line in implementation_files:
            self.__add_path(path_line[1])
            
        self.__logger.info("%i input files (incl. duplicates) specified in %i directories" % (self.__file_count, len(self.__directory_to_file_map.keys())))
        
    def __get_directories(self):
        if self.__directory_to_file_map == None:
            self.__generate_directory_to_file_map()
        return self.__directory_to_file_map.keys()
    
    def __get_files(self, directory):
        return self.__directory_to_file_map[directory]

    def incremental_generate(self):
        pass
        # TODO
        # if solution_file_changed:
        #    generate for new projects
        #    remove for removed projects
        # if vcproj_changed:
        #    generate for new files
        #    remove for removed files
        # for all changed files:
        #    regenerate
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
