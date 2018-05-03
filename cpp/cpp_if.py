#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 22.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.core_if import EnumerationItem, Enumeration

class HeaderListSupply(AutoConfigurable):
    def get_header_list(self):
        raise NotImplementedError(self.__class__)
    
class CppLiterals(object):
    LINE_COMMENT_PREFIX = '//'

class CppFileConfiguration(AutoConfigurable):
    def get_header_file_extensions(self):
        raise NotImplementedError(self.__class__)

    def get_implementation_file_extensions(self):
        raise NotImplementedError(self.__class__)

    def is_header_file(self, path):
        raise NotImplementedError(self.__class__)

    def is_implementation_file(self, path):
        raise NotImplementedError(self.__class__)

class _CppFileType(EnumerationItem):
    pass

class CppFileTypes(Enumeration):
    _type = _CppFileType
    ImplementationFile = _CppFileType()
    HeaderFile = _CppFileType()
    HeaderImplementationFile = _CppFileType()

class CppDataSupply(AutoConfigurable):
    # TODO Semantik, wann werden Collections, wann nur (einmal verwendbare) Iterables zurück geliefert 
    # -> Üblicherweise Iterables, außer wenn dies explizit anders gesagt ist

    """
    @rtype: Iterable(str)
    """
    def get_header_list(self):
        # TODO remove from this class, moved to HeaderListSupply
        raise NotImplementedError(self.__class__)

    def get_module_rootdirs(self):
        """
        Returns a dictionary module name -> root dir (rel to main root).
        """
        raise NotImplementedError(self.__class__)

class FileToModuleMapSupply(AutoConfigurable):
    def get_module_to_header_file_map(self):
        raise NotImplementedError(self.__class__)

    def get_module_to_implementation_file_map(self):
        raise NotImplementedError(self.__class__)

    def get_module_to_header_file_map_final(self):
        raise NotImplementedError(self.__class__)

    def get_header_file_map_exceptions(self):
        raise NotImplementedError(self.__class__)

    def get_implementation_file_map_exceptions(self):
        raise NotImplementedError(self.__class__)

    def get_header_file_to_module_map(self, use_exceptions=True):
        raise NotImplementedError(self.__class__)

    def get_implementation_file_to_module_map(self, use_exceptions=True):
        raise NotImplementedError(self.__class__)

    def generate_file_to_module_map(self, use_exceptions=True):
        raise NotImplementedError(self.__class__)

    def generate_module_to_file_map(self, use_exceptions=True):
        raise NotImplementedError(self.__class__)

class CppPaths(AutoConfigurable):
    """
    @todo: move and rename CppPaths. It is not specific to Cpp, but rather to the Microsoft toolchain 
        around VisualStudio, independent of the programming language. Other toolchains may also have
        module specifications, but their format and semantics will be different.
    """
    def get_module_spec_basedir(self):
        raise NotImplementedError(self.__class__)

    def get_solution_file(self):
        raise NotImplementedError(self.__class__)

class _VirtualModuleType(EnumerationItem):
    def __init__(self, suffix):
        self.__suffix = suffix

    def suffix(self):
        return self.__suffix

class VirtualModuleTypes(Enumeration):
    _type = _VirtualModuleType
    DeclarationModule = _VirtualModuleType("_decl")
    HeaderModule = _VirtualModuleType("_inc")
    CombinedModule = _VirtualModuleType("_INC")
    ExtensionSubmodule = _VirtualModuleType("_ext")
    suffixes = None

    @staticmethod
    def remove_suffixes(module):
        if VirtualModuleTypes.suffixes == None:
            VirtualModuleTypes.suffixes = [value.suffix() for value in VirtualModuleTypes.values()]
        for suffix in VirtualModuleTypes.suffixes:
            module = module.replace(suffix, '')
        return module

