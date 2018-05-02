'''
Created on 18.02.2012

@author: SIGIESEC
'''
from commons.core_if import EnumerationItem, Enumeration
from commons.progress_if import ProgressListenerSubject

class FileTransformationException(Exception):
    """
    Any situation that requires reverting the processed file.
    """
    pass

class ManualProcessingException(FileTransformationException):
    """
    This exception is raised by a FileNormalizer to indicate that it cannot process the file and
    the include statements should be checked manually.
    """
    pass

class FileTransformer(ProgressListenerSubject):
    def process_files(self, file_paths):
        raise NotImplementedError(self.__class__)
            
    def get_statistics(self):
        raise NotImplementedError(self.__class__)

class FileTransformationMode(EnumerationItem):
    pass

class FileTransformationModes(Enumeration):
    _type=FileTransformationMode
    NormalizeOnly=FileTransformationMode()
    Repair=FileTransformationMode()
    ListIncludes=FileTransformationMode()
