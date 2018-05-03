'''
Default implementations of the progress handler interface from commons.progress_if
that have no specific dependencies or write to a console-style output stream. 

Created on 12.10.2010

@author: SIGIESEC
'''
from commons.progress_if import ProgressListener
import sys
import datetime

# TODO split modoule into
# a) the implementation of common.progress_if.ProgressListener
# b) base classes for progress-listener aware implementations

class NullProgressListener(ProgressListener):
    def start(self, total=0):
        pass
    
    def set_total(self, total):
        pass

    def increment(self, increment=1):
        pass

    def done(self):
        pass
    
    def get_sub_listener(self, name):
        return self
    
# TODO Remove duplication between DefaultProgressListener and CountingProgressListener
# TODO introduce parameter for output stream of DefaultProgressListener and CountingProgressListener

class DefaultProgressListener(ProgressListener):
    LINE_LENGTH = 80
    
    def __init__(self, *args, **kwargs):
        ProgressListener.__init__(self, *args, **kwargs)
        self.__total = None
        self.__current = 0
        self.__pos = 0
        self.__outstr = sys.stderr

    def start(self, total=0):
        self.__total = None
        self.set_total(total)

    def set_total(self, total):
        if self.__total == None:
            for _x in range(1, self.LINE_LENGTH):
                self.__outstr.write(".")
            self.__outstr.write("\015")
        self.__outstr.flush()
        self.__total = total


    def current_percentage(self):
        if self.__total == 0:
            return 1
        else:
            return min(float(self.__current) / float(self.__total), 1)

    def increment(self, increment=1):
        if self.__total == None:
            self.__outstr.write(".")
        else:
            self.__current += increment
            if self.__current > self.__total:
                self.__current = self.__total
            new_pos = int(self.current_percentage() * self.LINE_LENGTH)
            while new_pos >= self.__pos:
                self.__outstr.write("O")
                self.__pos += 1
        self.__outstr.flush()

    def done(self):
        if self.__total != None:
            self.__total = None            
        print
         
    def get_sub_listener(self, name):
        if name:
            self.__outstr.write("Task added: %s\n" % name)
        return self

class CountingProgressListener(ProgressListener):
    def __init__(self, *args, **kwargs):
        ProgressListener.__init__(self, *args, **kwargs)
        self.__started = None
        self.__total = None
        self.__outstr = sys.stderr
        self.__current = 0

    def __reset(self):
        self.__total = None            
        self.__started = None
        self.__current = 0
    
    def current_percentage(self):
        if self.__total == 0:
            return 1
        else:
            return min(float(self.__current) / float(self.__total), 1)
            
    def start(self, total=0):
        self.__reset()
        self.__started = datetime.datetime.now()
        self.set_total(total)

    def set_total(self, total):
        self.__total = total

    def __output(self):
        self.__outstr.write("\015")
        if self.__started:
            passed = datetime.datetime.now() - self.__started
            remaining = datetime.timedelta(seconds=int(passed.seconds * (1 / self.current_percentage()) - passed.seconds))
            passed = datetime.timedelta(seconds=passed.seconds)
        else:
            passed = "unknown"
            remaining = "unknown"
        self.__outstr.write("%i/%i (passed: %s, est. remaining: %s)" % (self.__current, self.__total, passed, remaining))
        self.__outstr.flush()
    
    
    def increment(self, increment=1):
        self.__current += increment
        self.__output()

    def done(self):
        self.__reset()
        print
        
    def get_sub_listener(self, name):
        if name:
            self.__outstr.write("Task added: %s\n" % name)
        return self

class SubTask(object):
    def __init__(self, start_func, done_func, name):
        self.__start_func = start_func
        self.__done_func = done_func
        self.__name = name
        
    def get_name(self):
        return self.__name
    
    def start(self):
        self.__start_func(self)
    
    def done(self):
        self.__done_func(self)

class SubProgressListenerAwareMixin(object):
    """
    
    @status: This is experimental and currently unused.
    """
    
    def __init__(self):
        self.__subtasks = set()
    
    def register(self, name):
        subtask = SubTask(self.__start_subtask, self.__done_subtask, name=name)
        self.__subtasks.add(subtask)
        return subtask

class ProgressListenerMixin(object):
    """
    A base class for progress-listener-aware classes.
    
    May be inherited.  
    """
    
    # TODO why does this not implement ProgressListenerSubject?
    
    def __init__(self):
        self.__progress_listener = NullProgressListener()
    
    def _progress_listener(self, task_name=None):
        """
        @return: Always returns a valid object. 
        @rtype: ProgressListener 
        """
        if not task_name:
            return self.__progress_listener.get_sub_listener(task_name)
        else:
            return self.__progress_listener
    
    def attach_progress_listener(self, progress_listener):
        """
        Attaches a progress listener to the object.

        Should only be called by a client, not by self.
        """
        self.__progress_listener = progress_listener
        return self
        
    def detach_progress_listener(self, progress_listener):
        """
        Detaches a progress listener from the object.

        Should only be called by a client, not by self.
        """
        if self.__progress_listener == progress_listener:
            self.__progress_listener = NullProgressListener()

