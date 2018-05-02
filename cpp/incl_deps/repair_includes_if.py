'''
Created on 20.12.2011

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class FileNormalizer(AutoConfigurable):
    """
    A file normalizer normalizes a C/C++ file by replacing its #include statements 
    by a given list of files to include. It is not the responsibility of the file normalizer
    to modify this list, e.g. by checking if the are actually needed. This is 
    assumed to have happened before. 
    """
    
    def process(self, repair_path, included_files, in_file, out_file):
        """
        TODO
        
        @param repair_path:
        @type repair_path: string (rel_to_root_path_unix) 
        @param included_paths: the normalized include list
        @type included_paths: list of strings (rel_to_root_path_unix or <...> for external headers) 
        @param input_file: the file to be normalized
        @type input_file: an object similar to a file open for reading, i.e. an iterator of strings
        @param output_file: the result of the normalization
        @type output_file: an object similar to a file open for writing, i.e. an object with a write(string) method
        
        @raise FileTransformationException: if a situation occurs that requires reverting the modified file, 
            e.g. because it has been specified by the user that a manual check should be done. 
        """
        raise NotImplementedError

class HeaderLister(AutoConfigurable):
    def map_symbol_ids_to_headers(self, object_ids, project_file):
        """^
        @param object_ids: input objects
        @type: an iterable of objects
        
        @param project_file:
        @type project_file: base.project_if.ProjectFile
        
        @rtype: an iterable of base.project_if.ProjectFile
        """
        raise NotImplementedError(self.__class__)

class UsedSymbolsLister(AutoConfigurable):
    def get_symbol_candidates(self, project_file):
        """
        TODO: depending on the implementation, it might be necessary to know an implementation 
        file that successfully includes the project_file in order to determine candidates 
        for ambiguous symbols! 
        
        @param project_file: The project file for which to determine the used symbols.
        @type project_file: base.project_if.ProjectFile
        
        @return: a dictionary that maps symbol ids to their simple names
        @rtype: dict of value-type object to string
        """
        raise NotImplementedError(self.__class__)

class SymbolScanner(AutoConfigurable):
    def scan_for_symbols(self, lines, search_keywords):
        """
        Scans an iterator of strings (typically a file) for symbols in an id:symbol dictionary. 
        Returns a set of the ids of which symbols were found.
        
        @type lines: iterator of string
        @type search_keywords: dict of value-type object to string
        """
        raise NotImplementedError(self.__class__)
    
class RequiredIncludeFilesCalculator(AutoConfigurable):
    def __init__(self, is_implementation_file_func, resource_resolver):
        """
        TODO
        
        Implementations of this interface must ensure to accept the parameters declared here.
        
        @param is_implementation_file_func: TODO
        @param resource_resolver: TODO
        """
    
    def calculate_required_include_files(self, project_file):
        """
        Calculates the include files required by project_file.
        
        @param project_file: a project file
        @type project_file: base.project_if.ProjectFile
        
        @rtype: iterable of include specifications (paths relative to project root or <filename> for external include files)
            TODO change this to a safer construct 
        """
        raise NotImplementedError(self.__class__)

