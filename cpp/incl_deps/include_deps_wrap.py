'''
Created on 17.02.2012

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.config_if import ConfigDependent
from commons.progress_if import ProgressListener, progress_listener_attached_to
from cpp.cpp_if import CppFileConfiguration
from cpp.cpp_util import CppProjectUtil
from cpp.incl_deps.file_transform_facade import CppFileTransformerFactory
from cpp.incl_deps.file_transform_if import FileTransformationModes
from cpp.incl_deps.file_transform_resolver import IncludeCollectorProcessor
from cpp.incl_deps.include_deps_if import IncludeDependencyGenerator
import logging

config_cpp_file_configuration = CppFileConfiguration()
config_basic_config = BasicConfig()
config_progress_listener = ProgressListener

class PythonIncludeDependencyGeneratorWrapper(IncludeDependencyGenerator, ConfigDependent):
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def generate(self):
        progress_listener = config_progress_listener()
        local_source_base_dir = config_basic_config.get_local_source_base_dir()
        file_transfomer = CppFileTransformerFactory(config_cpp_file_configuration, config_basic_config).create_file_repair_processor(local_source_base_dir=local_source_base_dir,
                                                        target=None, 
                                                        target_dir=None, 
                                                        mode=FileTransformationModes.ListIncludes, 
                                                        required_includes=None, 
                                                        closure=False,
                                                        invalidate=True,
                                                        required_include_files_calculator_class=None)
        start_dirs = config_basic_config.get_local_source_base_dir_subset()
        starting_files = CppProjectUtil.scan_project_files(start_dirs, local_source_base_dir, config_cpp_file_configuration, self.__logger)
        with progress_listener_attached_to(file_transfomer, progress_listener):
            file_transfomer.process_files(starting_files)
        assert hasattr(file_transfomer, "get_include_map")
        include_map_items = file_transfomer.get_include_map()
        for line in IncludeCollectorProcessor.format_include_map(local_source_base_dir, include_map_items):
            print line
        self.__logger.info(file_transfomer.get_statistics_dict())
        #return file_transfomer.get_statistics_dict()        
