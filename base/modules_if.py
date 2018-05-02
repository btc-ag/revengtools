# -*- coding: UTF-8 -*-

'''
Created on 28.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

class Module(object):
    def __init__(self, name):
        self.__name = name
    
    def name(self):
        return self.__name
    
    def __str__(self):
        return self.name()

class ExternalModule(Module):
    pass

class ModuleListSupplyEx(object):
    def get_module_descriptors(self):
        """
        Gets pairs of known module specification files and module names.
        
        @return: pairs of project-relative filenames of module specification files and module names
        @rtype: collections.Iterable(str, str)
        
        @todo: Return Resource objects instead of project-relative filenames.
        """
        raise NotImplementedError(self.__class__)
    
    def get_module_spec_files(self):
        """
        Returns all the module specification files.
        
        @note: The number of results may differ from get_module_list and get_module_descriptors 
        if there are duplicate module names.
        
        @return: the module specification files
        @rtype: collections.Iterable(Resource)
        """
        raise NotImplementedError(self.__class__)
    
    def get_module_diagnostics(self):
        raise NotImplementedError(self.__class__)

class ModuleListSupply(AutoConfigurable):
    def get_module_list(self):
        """
        Returns an iterable of the names of all modules in the subject system.
        
        @rtype: collections.Iterable, its elements being of type str
        """
        raise NotImplementedError(self.__class__)
    
    def get_files_for_module(self, module):
        """
        Returns the list of source files associated with this module.
        
        @param module: a name of a module
        @precondition: module in self.get_module_list()        
        """        
        raise NotImplementedError(self.__class__)
    
    def is_external_module(self, module):
        """
        Determines whether the module is unknown by this module list supply. 
        
        @param module: a name of a module
        @rtype: bool
        @return: equivalent to module in self.get_module_list()
        """
        raise NotImplementedError(self.__class__)
    
    def get_module_size(self, module):
        """
        Returns the size of a module. The exact meaning of size is implementation-dependent,
        typically this is the number of lines in the source files of the module.
        
        TODO what happens if the size of the module cannot be determined?
        e.g. if some files could not be read
        Throwing an exception is not good, better return an object (or tuple) which contains 
        a partial result with a list of errors. PartialResult could be a generic class.
        
        @param module: a name of a module
        @rtype: an integral type
        @precondition: module in self.get_module_list()        
        """
        raise NotImplementedError(self.__class__)
    
    def get_max_module_size(self):
        """
        Returns the maximum size of all modules known to this module list supply.
        
        @return: equivalent to max(map(self.get_module_size, self.get_module_list()))
        @rtype: an integral type, same as the return type of get_module_size()
        @todo: this might be removed, as it is currently unused
        """
        raise NotImplementedError(self.__class__)

    def get_min_module_size(self):
        """
        Returns the minimum size of all modules known to this module list supply.
        
        @return: equivalent to min(map(self.get_module_size, self.get_module_list()))
        @rtype: an integral type, same as the return type of get_module_size()
        @todo: this might be removed, as it is currently unused
        """
        raise NotImplementedError(self.__class__)


class RuleSupply(AutoConfigurable):
    def get_checked_rules(self):
        raise NotImplementedError(self.__class__)
    
    def set_checked_rules(self, source_file_result):
        raise NotImplementedError(self.__class__)
    
    
class SourceFileSupply(AutoConfigurable):
    def get_source_files(self):
        raise NotImplementedError(self.__class__)
    
    def set_source_file_results(self, source_file_result):
        raise NotImplementedError(self.__class__)
    
    def get_source_file_results(self):
        raise NotImplementedError(self.__class__)

    
class SolutionFileSupply(AutoConfigurable):
    def get_modules_in_solution_files(self):
        raise NotImplementedError(self.__class__)
    
    def set_results(self, global_results):
        raise NotImplementedError(self.__class__)
    
    def get_results(self):
        raise NotImplementedError(self.__class__)
        
    # TODO get_module_size  hat mit der Modulliste eigentlich nichts zu tun, nur mit einem einzelnen,
    # benannten Modul. Eigentlich braucht man eher eine Methode get_files_for_module. get_module_size
    # kann dann, wenn die Dateien lokal zur Verfügung stehen, immer gleich arbeiten.

