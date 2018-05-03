# -*- coding: UTF-8 -*-
'''
Utilities around threads and the Python threading module.

Created on 06.11.2010

@author: SIGIESEC
'''
from __future__ import with_statement
from Queue import Queue, Empty
from itertools import ifilter
from threading import Thread, Lock
import logging
import os
import threading

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.__tasks = tasks
        self.daemon = True
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__shutdown = False
        self.start()
    
    def shutdown(self):
        self.__shutdown = True
        
    def _do_task(self, *args, **kwargs):
        """
        Subclasses should implement _do_task, which will be called for the execution of 
        each individual task.         
        """        
        raise NotImplementedError(self.__class__)
        
    def run(self):
        while not self.__shutdown or not self.__tasks.empty():
            try:
                args, kargs = self.__tasks.get(timeout=2)
                try: 
                    self._do_task(*args, **kargs)
                except Exception, e: 
                    self.__logger.error("Exception in worker thread: %s", e)
                self.__tasks.task_done()
            except Empty:
                self.__logger.info("Worker %s timed out", threading.currentThread().name)

class ThreadPool(object):
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads, worker_class, name=None):
        self.__lock = Lock()
        self.__tasks = Queue()
        self.__workers = [worker_class(self.__tasks) for _ in range(num_threads)] 
        self.__in_shutdown = False
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__name = name
        
    def __del__(self):
        self.__logger.info("ThreadPool %s destructor called" % str(self.__name))
        self.shutdown()
        self.wait_completion()

    def add_task(self, *args, **kargs):
        """Add a task to the queue"""
        with self.__lock:            
            if not self.__in_shutdown:
                self.__tasks.put((args, kargs))
            else:
                raise RuntimeError("Cannot add task to a ThreadPool that is being shut down")

    def wait_completion(self):
        """
        After shutdown, wait for completion of all the tasks in the queue.
        This will not return before shutdown has been called. 
        """
        self.__tasks.join()
        
    def shutdown(self):
        """
        Initiates the shutdown of the ThreadPool by shutting down all workers. 
        """
        with self.__lock:
            if not self.__in_shutdown:
                self.__in_shutdown = True
                for worker in self.__workers:
                    worker.shutdown()

    def get_workers(self):
        return iter(self.__workers)

class UnTeeWorkerBase(Worker):
    def __init__(self, *args, **kwargs):
        self.__pipe_write_fd = None
        self.__logger = logging.getLogger(self.__class__.__module__)
        Worker.__init__(self, *args, **kwargs)

    def _get_write_fd(self):
        return self.__pipe_write_fd

    def _write(self, line):
        os.write(self.__pipe_write_fd, line)
                            
    def run(self):
        Worker.run(self)
        self.__logger.info("Worker %s is done", threading.currentThread().name)
        os.close(self.__pipe_write_fd)
    
    def set_write_pipe(self, fd):
        self.__pipe_write_fd = fd
        
class Tee(object):
    BUFFER_SIZE=5000
    
    def __init__(self, out_files):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__out_files = out_files
        (pipe_in, pipe_out) = os.pipe()
        self.__pipe_out = os.fdopen(pipe_out, "wb")
        self.__thread = Thread(target=self.__spool, args=(pipe_in, self.__out_files))
        self.__thread.start()
        
    def __del__(self):
        if self.__thread:
            self.__logger.debug("Joining spool thread")
            self.__thread.join()
        if self.__pipe_out:
            self.__logger.debug("Closing output pipe")
            self.__pipe_out.close()

    @staticmethod
    def __spool(pipe_in, out_files):
        try:
            while True:
                buf = os.read(pipe_in, Tee.BUFFER_SIZE)
                if len(buf) > 0:
                    for out_file in out_files:
                        out_file.write(buf)
                else:
                    break
        # TODO eigentlich sollten die Dateien hier nicht geschlossen werden. Ist das überhaupt nötig?
        finally:
            for out_file in out_files:
                out_file.close()
            os.close(pipe_in)

    def stdin(self):
        return self.__pipe_out

    def close(self):
        self.__pipe_out.flush()
        self.__pipe_out.close()


class UnTee(Thread):
    def __init__(self, in_files, out_file):
        Thread.__init__(self)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__in_files = in_files
        self.__pipe_write  = out_file
        self.start()
    
    def run(self):
        lines_read = 1
        while lines_read > 0:
            lines = ifilter(None, (in_file.readline() for in_file in self.__in_files))
            lines_read = 0
            for line in lines:
                lines_read += 1
                self.__pipe_write.write(line)
        self.__logger.info("UnTee ended")
        for in_file in self.__in_files:
            in_file.close()
        self.__pipe_write.close()

class UnTeeHelper(object):
    @staticmethod
    def setup_untee(threadpool_size, worker_class, out_file):
        tp = ThreadPool(threadpool_size, worker_class)
        pipes = list()
        for worker in tp.get_workers():
            fds = os.pipe()
            worker.set_write_pipe(fds[1])
            pipes.append(os.fdopen(fds[0], "rb"))
        untee = UnTee(pipes, out_file)
        return (tp, untee)
