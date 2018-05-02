'''
Created on 12.10.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class ProgressListener(AutoConfigurable):
    """
    A progress listener interface.
    """
    
    # TODO introduce named sub progress listeners
    # TODO multiple sub progress listeners may be created
    # TODO incrementation should only be done between start and done (implicit start by increment?)
    # TODO when a progress listeners has sub-listeners, is it legal to call increment on it? or does 
    #   this happen implicitly when the sub-listeners are done?
    
    def start(self, total=0):
        raise NotImplementedError(self.__class__)
    
    def set_total(self, total):
        raise NotImplementedError(self.__class__)
    
    def increment(self, increment=1):
        raise NotImplementedError(self.__class__)
    
    def done(self):
        raise NotImplementedError(self.__class__)
    
    def get_sub_listener(self, name):
        raise NotImplementedError(self.__class__)
        
    
class progress_listener_attached_to(object):
    """
    Used to execute some operation under supervision of a progress listener.
    
    Use like:
        with progress_listener_attached_to(progress_listener_subject, progress_listener):
            progress_listener_subject.long_running_operation()

    Uses outside a with statement are not encouraged.
    """
    
    def __init__(self, target, progress_listener):
        """
        
        @param target: The object to attach the progress listener to.
        @type target: ProgressListenerSubject
        @param progress_listener: The progress listener.
        @type progress_listener: ProgressListener
        """
        self.__target = target
        self.__progress_listener = progress_listener
        
    def __enter__(self):
        if hasattr(self.__target, "attach_progress_listener"):
            return self.__target.attach_progress_listener(self.__progress_listener)
        else:
            return self.__target
        
    def __exit__(self, type, value, traceback):
        if hasattr(self.__target, "detach_progress_listener"):
            self.__target.detach_progress_listener(self.__progress_listener)
        return False

class ProgressListenerSubject(object):
    def attach_progress_listener(self, progress_listener):
        raise NotImplementedError(self.__class__)
        
    def detach_progress_listener(self, progress_listener):
        raise NotImplementedError(self.__class__)

