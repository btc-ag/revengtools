'''
Implementations of cpp.incl_deps.file_transform_if for normalizing include directives
by canonicalizing include paths.

Created on 18.02.2012

@author: SIGIESEC
'''
from base.project_default import DefaultProjectFile
from commons.core_util import DictTools
from commons.os_util import PathTools, FileListsManager
from commons.resource_util import LineByLineProcessor
from cpp.cpp_util import CommentFilter
from cpp.incl_deps.file_transform_base import IndividualCppFileTransformer
from cpp.incl_deps.include_resolver_util import (IncludeDirectiveNormalizer, 
    FileMapFactory)
from itertools import imap, ifilter
import os
import logging

class NormalizingIndividualFileTransformerBase(object):
    def __init__(self, local_source_resource_resolver, generation_strategy,
                 is_implementation_file_func,
                 header_extensions,
                 include_canonicalizer_factory,
                 cache_storage_dir,
                 invalidate=False):
        self._local_source_resource_resolver = local_source_resource_resolver
        self._include_canonicalizer_factory = include_canonicalizer_factory
        
        prepare_func = lambda repair_path_rel_to_root_unix, input_resource: []
        
        process_func = self._process_normalizing
        # TODO allow to guess target of an include directive if it cannot be resolved exactly
    
        self.__processor = IndividualCppFileTransformer(local_source_resource_resolver=local_source_resource_resolver,
                                             generation_strategy=generation_strategy,
                                             prepare_func=prepare_func,
                                             process_func=process_func)
        self.__filelists = FileListsManager(cache_storage_dir=cache_storage_dir, extensions=header_extensions)
        if invalidate:
            self.__filelists.invalidate_all()
        self._filemap_factory = FileMapFactory(self.__filelists)

    def _process_normalizing(self, repair_path, intermediate_result, input_file, output_file):
        """
        
        @param repair_path:
        @param intermediate_result:
        @param input_file:
        @param output_file:
        @return: a tuple of an iterator of included files found (relative to project base directory) and a statistics dictionary
        @rtype: tuple(iter(str), dict(str, int))
        """
        raise NotImplementedError(self.__class__)

    def __getattr__(self, attr):
        """ Delegate access to dictionary """
        return getattr(self.__processor, attr)
    
class NormalizingIndividualFileTransformer(NormalizingIndividualFileTransformerBase):
    def __init__(self, *args, **kwargs):
        NormalizingIndividualFileTransformerBase.__init__(self, *args, **kwargs)        
    
    def _process_normalizing(self, repair_path, intermediate_result, input_file, output_file):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix=repair_path, 
                local_repository_root=self._local_source_resource_resolver.get_base_paths()[0]), 
                                                self._include_canonicalizer_factory,
                                                filemap_factory_func=self._filemap_factory.get_filemap)
        LineByLineProcessor(transform_func=normalizer.normalize).process_file(input_file, output_file)
        return (normalizer.get_included_files(), normalizer.get_statistics_dict())
    
class ListIncludePrinterProcessor(NormalizingIndividualFileTransformerBase):
    # TODO this is currentlyunused
    
    def __init__(self, output_file, skip_comments=True, *args, **kwargs):
        NormalizingIndividualFileTransformerBase.__init__(self, *args, **kwargs)
        self.__output_file = output_file
    
    def _process_normalizing(self, repair_path, intermediate_result, input_file, output_file):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix=repair_path, 
                local_repository_root=self._local_source_resource_resolver.get_base_paths()[0]), 
                                                self._include_canonicalizer_factory,
                                                filemap_factory_func=self._filemap_factory.get_filemap)
        comment_filter = CommentFilter()
        if self.__skip_comments:
            filtered_input_file = comment_filter.filter(input_file)
        else:
            filtered_input_file = input_file
        for line in filtered_input_file:
            include_spec = normalizer.get_include_specification(line)
            if include_spec:
                (_include_spec_type, included_resource) = include_spec
                # TODO output rel_to_root if under root
                print >>self.__output_file, "%s,%s" % (repair_path, included_resource.name())
        return (normalizer.get_included_files(), normalizer.get_statistics_dict())

class IncludeCollectorProcessor(NormalizingIndividualFileTransformerBase):
    # TODO this is not optimal, since there is no need to create a dictionary of all
    # entries. 
    
    def __init__(self, skip_comments=True, *args, **kwargs):
        NormalizingIndividualFileTransformerBase.__init__(self, *args, **kwargs)
        self.__include_map = dict()
        self.__skip_comments = skip_comments
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def _process_normalizing(self, repair_path, intermediate_result, input_file, output_file):
        normalizer = IncludeDirectiveNormalizer(DefaultProjectFile(path_rel_to_root_unix=repair_path, 
                local_repository_root=self._local_source_resource_resolver.get_base_paths()[0]), 
                                                self._include_canonicalizer_factory,
                                                filemap_factory_func=self._filemap_factory.get_filemap)
        # TODO or only create the iterator here? But this would not allow to return the statistics...
        if self.__skip_comments:
            comment_filter = CommentFilter()
            filtered_input_file = comment_filter.filter(input_file)
        else:
            filtered_input_file = input_file
        self.__include_map[repair_path] = tuple(ifilter(None, imap(normalizer.get_include_specification, filtered_input_file)))
        
        statistics_dict = normalizer.get_statistics_dict()
        if self.__skip_comments:
            DictTools.merge_dict(statistics_dict, comment_filter.get_statistics_dict(), value_merge_func=None)
        self.__logger.debug("%s includes files %s" % (repair_path, tuple(normalizer.get_included_files())))
        return (normalizer.get_included_files(), statistics_dict)
    
    def get_include_map(self):
        """
        @rtype: iterator of tuple(str, tuple(IncludeSpecificationType, FileResource))
        """
        return self.__include_map.iteritems()
    
    @staticmethod
    def format_include_map(local_source_base_dir, include_map_items):
        for base_path, include_specifications in include_map_items:
            for _include_specification_type, included_resource in include_specifications:
                included_path = included_resource.name()
                if included_path.startswith(local_source_base_dir + os.path.sep):
                    included_path = PathTools.native_to_posix(included_path.split(local_source_base_dir + os.path.sep)[1])
                yield "%s,%s" % (base_path, included_path)    
    
