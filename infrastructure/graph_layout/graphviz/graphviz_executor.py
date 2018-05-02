# -*- coding: UTF-8 -*-
'''
Created on 03.11.2010

@author: SIGIESEC
'''

from base.basic_config_if import BasicConfig
from commons.graph.output_if import RenderExecutor
from commons.v26compat_util import compatrelpath
from infrastructure.graph_layout.graphviz.graphviz_config import (
    GraphvizConfiguration)
from threading import Thread
import datetime
import logging
import os.path
import subprocess
import threading
import urllib
import time
import sys

config_graphviz = GraphvizConfiguration()

class BaseGraphvizRenderExecutor(RenderExecutor):
    def __init__(self, configuration):
        self.__configuration = configuration

    def _configuration(self):
        return self.__configuration

    @staticmethod
    def __get_dot_binary():
        return os.path.join(config_graphviz.get_graphviz_bin_dir(), "dot")

    def get_cmdline(self, input_filename, output_filename):
        return filter(None, [self.__get_dot_binary(),
                "-T%s" % self._configuration().get_output_format(),
                "-Gratio=%s" % self._configuration().get_aspect_ratio(),
                "-o%s" % output_filename if output_filename else None,
                input_filename if input_filename else None])

class SimpleGraphvizRenderExecutor(BaseGraphvizRenderExecutor):
    def __init__(self, *args, **kwargs):
        BaseGraphvizRenderExecutor.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__process = None
        self.__outfile = None

    def __del__(self):
        self.__logger.debug("destructor called for %s", self.__outfile.name if self.__outfile else None)
        if self.__process and self.__process.poll() == None:
            self.__logger.info("Graphviz process for %s is not done, waiting for it to finish", self.__outfile.name if self.__outfile else None)
            self.__process.wait()
            self.__logger.info("...done")

    def create_renderer(self, output_file, on_success=None):
        if on_success != None:
            self.__logger.warning("%s does not support success hook, executing regardless of success",
                                  self.__class__)
            on_success()
        cmdline = " ".join(self.get_cmdline(None, None))
        self.__outfile = output_file
        self.__process = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=output_file)
        return self.__process.stdin

# TODO das gehört hier nicht her
config_basic = BasicConfig()

class PipeGraphvizRenderExecutor(BaseGraphvizRenderExecutor):
    def __init__(self, *args, **kwargs):
        BaseGraphvizRenderExecutor.__init__(self, *args, **kwargs)
        self.__process = None
        self.__outfile = None
        self.__thread = None
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__on_success = None
        self.__starttime = None

    def __del__(self):
        self.__logger.debug("destructor called for %s", self.__outfile.name if self.__outfile else None)
        if self.__process and self.__process.poll() == None:
            self.__logger.info("Graphviz process for %s is not done, waiting for it to finish", self.__outfile.name if self.__outfile else None)
            self.__process.wait()
            self.__logger.info("...done")
        if self.__thread and self.__thread != threading.currentThread() and self.__thread.isAlive():
            self.__logger.info("Graphviz spool thread for %s is not done, waiting for it to finish", self.__outfile.name if self.__outfile else None)
            self.__thread.join()
            self.__logger.info("...done")
        

    def _create_process(self, cmdline):
        if self.__process:
            raise RuntimeError("Process already created")
        self.__starttime = datetime.datetime.now()
        self.__logger.debug("Trying to create subprocess with cmdline = %s" % (cmdline, ))
        try:
            self.__process = subprocess.Popen(cmdline,
                                          bufsize=-1,
                                          stdout=subprocess.PIPE,
                                          stdin=subprocess.PIPE)
        except EnvironmentError, e:
            raise EnvironmentError("creating subprocees with cmdline = %s failed, cause = %s" % (cmdline, e, ))

    def _get_out_pipe(self):
        if not self.__process:
            raise RuntimeError("Process not yet created")
        return self.__process.stdout

    def _get_in_pipe(self):
        if not self.__process:
            raise RuntimeError("Process not yet created")
        return self.__process.stdin

    def _output_file(self):
        return self.__outfile

    def create_renderer(self, output_file, on_success=None):
        self._create_process(self.get_cmdline(None, None))
        self.__outfile = output_file
        self.__on_success = on_success
        self.__thread = Thread(target=self.__spool_and_cleanup)
        self.__thread.start()
        return self._get_in_pipe()
    
    def __get_time_since_start(self):
        current_time = datetime.datetime.now()
        passed = current_time - self.__starttime
        return passed

    def __cleanup_process(self):
        self.__logger.info("Wait for graphviz for %s to finish" % (self.__outfile.name))
        while True:
            result = self.__process.wait()
            if result != None:
                break
            time.sleep(.5)
        if result == 0:
            self.__logger.info("Graphviz was successful for %s (exec time %s)", 
                               self.__outfile.name,
                               self.__get_time_since_start())
            #Nina wants to have some feedback in the console to see the process is still alive
            print >>sys.stderr, "Graphviz was successful for %s (exec time %s)"%(self.__outfile.name,
                                                                   self.__get_time_since_start())
            if self.__on_success != None:
                self.__on_success()
        else:
            self.__logger.error("Graphviz was not successful for %s (exec time %s)", 
                                self.__outfile.name,
                               self.__get_time_since_start())
        self.__process = None

    def _spool(self):
        try:
            while True:
                buf = os.read(self._get_out_pipe().fileno(), 5000)
                if len(buf) > 0:
                    self.__outfile.write(buf)
                else:
                    break        
        finally:
            self.__outfile.close()
            self._get_out_pipe().close()

    def __spool_and_cleanup(self):
        try:
            self._spool()
        except:
            self.__logger.error("Exception during graphviz execution", exc_info=1)
        finally:
            self.__cleanup_process()


class ScriptInjectingGraphvizRenderExecutor(PipeGraphvizRenderExecutor):
    def __get_scripts_abs(self):
        # TODO this should be configurable
        return [os.path.join(config_basic.get_results_directory(), 'graphviz-tools.js')]

    def __get_scripts_rel_to(self, output_file):
        return (urllib.pathname2url(compatrelpath(script, os.path.dirname(output_file)))
                for script in self.__get_scripts_abs())

    def create_renderer(self, *args, **kwargs):
        if self._configuration().get_output_format() != 'svg':
            raise RuntimeError("ScriptInjectingGraphvizRenderExecutor only supports .svg, not %s",
                               self._configuration().get_output_format())
        return PipeGraphvizRenderExecutor.create_renderer(self, *args, **kwargs)

    def _spool(self):
        SVGScriptInjector(self._get_out_pipe(),
                          self._output_file(),
                          self.__get_scripts_rel_to(self._output_file().name)).inject()

class SVGScriptInjector(object):
    def __init__(self, in_file, out_file, scripts):
        self.__in_file = in_file
        self.__out_file = out_file
        self.__scripts = scripts
        self.__logger = logging.getLogger(self.__class__.__module__)

    def inject(self):
        done = False
        # TODO Hier SAX verwenden...
        for line in self.__in_file:
            if not done and line.startswith("<g "):
                for script in self.__scripts:
                    self.__out_file.write('<script type="application/ecmascript" language="ecmascript" xlink:href="%s"/>\n' % script)
                line = line.replace("<g ", '<g onload="init();" ')
                done = True
            self.__out_file.write(line)
        if not done:
            self.__logger.error("Injection point not found in %s", self.__in_file.name)

