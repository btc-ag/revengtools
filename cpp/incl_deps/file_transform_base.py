# -*- coding: UTF-8 -*-
'''
Created on 18.02.2012

@author: SIGIESEC
'''
from commons.core_util import isinstance_or_duck, DictTools
from commons.os_util import ResourceResolver, PathTools
from commons.progress_default import ProgressListenerMixin
from commons.resource_if import GenerationStrategy
from cpp.incl_deps.file_transform_if import (ManualProcessingException, 
    FileTransformationException, FileTransformer)
import logging
import os


class IndividualCppFileTransformer(ProgressListenerMixin, FileTransformer):
        
    def __init__(self, local_source_resource_resolver, generation_strategy, prepare_func, process_func):
        assert isinstance_or_duck(local_source_resource_resolver, ResourceResolver)
        assert isinstance_or_duck(generation_strategy, GenerationStrategy)
        self.__prepare_func = prepare_func
        self.__process_func = process_func
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__resource_resolver = local_source_resource_resolver
        self.__generation_strategy = generation_strategy
        
        self.__successful_files = []
        self.__skipped_files = []
        self.__error_files = []
        self.__fatal_files = []
        self.__nested_statistics = dict()
        
    @classmethod
    def is_local_file(cls, path):
        # TODO das ist PRINS-spezifisch...
        # return re.match(r"([.][/\\])?[_A-Za-z0-9]+[/\\]", path)
        return not os.path.isabs(path)
    
    def __generate(self, repair_path_rel_to_root_unix, input_resource, output_resource):
        intermediate_result = self.__prepare_func(repair_path_rel_to_root_unix, input_resource)
        if self.__process_func != None:
            with input_resource.open(mode="r") as in_file:
                with output_resource.open(mode="w") as out_file:
                    (used_files, statistics) = self.__process_func(repair_path_rel_to_root_unix, intermediate_result, in_file, out_file)
                    DictTools.merge_dict(self.__nested_statistics, statistics, 
                                         value_merge_func=lambda x,y: x+y)
            
            return used_files
        else:
            return intermediate_result

    def process_file(self, repair_path_name):
        """
        @return: 
        @rtype: iterator (or set?) of strings
        """
        
        repair_path_rel_to_root_unix = PathTools.unix_normpath(repair_path_name)
        if not self.is_local_file(repair_path_rel_to_root_unix):
            self.__logger.info("Ignoring non-local file %s" % (repair_path_rel_to_root_unix, ))
            return []
        try:
            repair_resource = self.__resource_resolver.resolve(repair_path_rel_to_root_unix)
        
            self.__logger.info("Processing %s" % (repair_path_rel_to_root_unix, ))
            required_include_files = self.__generation_strategy.process(repair_resource, 
                                                                        lambda input_resource, output_resource: self.__generate(repair_path_rel_to_root_unix, input_resource, output_resource))
                                
            # TODO nur die lokalen Header zur�ck liefern
            self.__successful_files.append(repair_path_rel_to_root_unix)
            return required_include_files
        except ManualProcessingException:
            self.__skipped_files.append(repair_path_rel_to_root_unix)
            self.__logger.info("Using manual includes in %s, skipping file" % (repair_path_rel_to_root_unix,))
            return []
        except FileTransformationException:
            self.__error_files.append(repair_path_rel_to_root_unix)
            self.__logger.warning("Error while processing %s, skipping file" % (repair_path_rel_to_root_unix,), exc_info=1)
            return []
        except:
            self.__logger.warning("Fatal error while processing %s, skipping file" % (repair_path_rel_to_root_unix,), exc_info=1)
            self.__fatal_files.append(repair_path_rel_to_root_unix)
            return []
        
    def process_files(self, file_paths):
        to_process = list(file_paths)
        self._progress_listener().start(len(to_process))
        for file_path in to_process:
            self.process_file(file_path)
            self._progress_listener().increment()
        self._progress_listener().done()
            
    def get_statistics(self):
        """
        @deprecated: use get_statistics_dict instead
        """
        return (len(self.__successful_files), len(self.__skipped_files), len(self.__error_files), len(self.__fatal_files))
    
    def get_statistics_dict(self):
        result = dict()
        DictTools.merge_dict(result, self.__nested_statistics, 
                             value_merge_func=None, 
                             key_merge_func=lambda key: "File content - %s" % key)
        result.update({"Sucessfully processed files": len(self.__successful_files), 
                       "Files skipped": len(self.__skipped_files), 
                       "Files with an error": len(self.__error_files), 
                       "Files with fatal error": len(self.__fatal_files)})
        return result

class ClosureFileRepairProcessor(ProgressListenerMixin, object):
    def __init__(self, decoratee):
        self.__individual_file_repair_processor = decoratee
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def process_file(self, file_path):
        self.process_files([file_path])
    
    def process_files(self, file_paths):
        try:
            to_process = list(file_paths)
            progress_listener = self._progress_listener("Processing transitive closure of dependent files using %s" % self.__individual_file_repair_processor)
            progress_listener.start(len(to_process))
            processed = set()
            while len(to_process) > 0:
                next_file = to_process.pop()
                if not next_file in processed:
                    to_process.extend(self.__individual_file_repair_processor.process_file(next_file))
                    progress_listener.set_total(len(to_process) + len(processed))                
                    progress_listener.increment()
                    processed.add(next_file)
        finally:
            progress_listener.done()
            
    def __getattr__(self, name):
        return getattr(self.__individual_file_repair_processor, name)
