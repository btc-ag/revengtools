'''
Created on 18.02.2012

@author: SIGIESEC
'''
from commons.core_util import DictReaderTools
from commons.os_util import (InPlaceGenerationStrategy, NullGenerationStrategy, 
    ExternalGenerationStrategy, FileTools, FixedBaseDirPathResolver, FileResource)
from cpp.cpp_util import IncludePathMappingFactory
from cpp.incl_deps.file_transform_base import ClosureFileRepairProcessor
from cpp.incl_deps.file_transform_if import FileTransformationModes
from cpp.incl_deps.include_resolver_util import (
    DefaultIncludePathCanonicalizerFactory)


class CppFileTransformerFactory(object):
    """
    Acts as a facade.
    """
    
    def __init__(self, cpp_file_configuration, basic_config):
        self.__cpp_file_configuration = cpp_file_configuration
        self.__basic_config = basic_config        
    
    def __create_include_path_canonicalizer_factory(self, local_source_base_dir):
        internal_include_paths = [local_source_base_dir]
        external_include_paths = IncludePathMappingFactory(self.__basic_config).create().get_include_directories()
        ipcf = DefaultIncludePathCanonicalizerFactory(global_internal_include_paths=internal_include_paths, 
            global_external_include_paths=external_include_paths)
            #module_include_paths_func,
            #quoted_internal_include_paths,
            #path_module
        return ipcf

    def __create_generation_strategy(self, target, target_dir):
        # TODO use Enumeration for target types
        if target == "inplace":
            generation_strategy = InPlaceGenerationStrategy()
        elif target== "none":
            generation_strategy = NullGenerationStrategy()
        else:
            generation_strategy = ExternalGenerationStrategy(target_dir=target_dir, 
                copy_on_error=True)
        return generation_strategy


    def __create_repairing_file_repair_processor(self, required_includes, local_source_resource_resolver, is_implementation_file_func, generation_strategy, required_include_files_calculator_class, include_list_generator_factory):
        if required_includes:
            from cpp.incl_deps.repair_includes_base import OnePhaseRequiredIncludeFilesCalculator
            required_include_map = DictReaderTools.transform_to_set_valued_dict(FileTools.create_csv_dict_reader(required_includes, "required includes", ["from_file", "to_file"], ",", allow_missing=True), "from_file", "to_file")
            required_include_files_calculator = OnePhaseRequiredIncludeFilesCalculator(include_map=required_include_map, 
                is_implementation_file_func=is_implementation_file_func, 
                resource_resolver=local_source_resource_resolver)
        else:
            required_include_files_calculator = required_include_files_calculator_class(is_implementation_file_func=is_implementation_file_func, 
                resource_resolver=local_source_resource_resolver)
        from cpp.incl_deps.file_transform_repair import RepairingIndividualFileRepairProcessor
        individual_file_repair_processor = RepairingIndividualFileRepairProcessor(is_implementation_file_func=is_implementation_file_func, 
            local_source_resource_resolver=local_source_resource_resolver, 
            required_include_files_calculator=required_include_files_calculator, 
            generation_strategy=generation_strategy,
            include_list_generator_factory=include_list_generator_factory)
        return individual_file_repair_processor


    def __create_normalizing_file_repair_processor(self, local_source_resource_resolver, is_implementation_file_func, ipcf, generation_strategy, invalidate):
        from cpp.incl_deps.file_transform_resolver import NormalizingIndividualFileTransformer
        individual_file_repair_processor = NormalizingIndividualFileTransformer(is_implementation_file_func=is_implementation_file_func, 
            local_source_resource_resolver=local_source_resource_resolver, 
            include_canonicalizer_factory=ipcf, 
            generation_strategy=generation_strategy, 
            header_extensions=self.__cpp_file_configuration.get_header_file_extensions(), 
            cache_storage_dir=self.__basic_config.get_results_directory(),
            invalidate=invalidate)
        return individual_file_repair_processor

    def __create_list_include_processor(self, local_source_resource_resolver, is_implementation_file_func, ipcf, generation_strategy, invalidate):        
        from cpp.incl_deps.file_transform_resolver import IncludeCollectorProcessor
        individual_file_repair_processor = IncludeCollectorProcessor(is_implementation_file_func=is_implementation_file_func, 
            local_source_resource_resolver=local_source_resource_resolver, 
            include_canonicalizer_factory=ipcf, 
            generation_strategy=generation_strategy, 
            header_extensions=self.__cpp_file_configuration.get_header_file_extensions(), 
            cache_storage_dir=self.__basic_config.get_results_directory(),
            invalidate=invalidate) # TODO add parameter
        return individual_file_repair_processor

    def create_file_repair_processor(self, local_source_base_dir, mode, required_includes, closure, invalidate, target=None, target_dir=None, required_include_files_calculator_class=None, include_list_generator_factory=None):
        local_source_resource_resolver = FixedBaseDirPathResolver(FileResource(local_source_base_dir), normalize=True)
        is_implementation_file_func = self.__cpp_file_configuration.is_implementation_file
        generation_strategy = self.__create_generation_strategy("none" if mode==FileTransformationModes.ListIncludes else target, target_dir)
        if mode in (FileTransformationModes.NormalizeOnly, FileTransformationModes.ListIncludes):
            ipcf = self.__create_include_path_canonicalizer_factory(local_source_base_dir)
            if mode == FileTransformationModes.NormalizeOnly:
                individual_file_repair_processor = self.__create_normalizing_file_repair_processor(local_source_resource_resolver, 
                                                                                                   is_implementation_file_func, 
                                                                                                   ipcf, 
                                                                                                   generation_strategy, 
                                                                                                   invalidate)
            elif mode == FileTransformationModes.ListIncludes:
                individual_file_repair_processor = self.__create_list_include_processor(local_source_resource_resolver, 
                                                                                        is_implementation_file_func, 
                                                                                        ipcf, 
                                                                                        generation_strategy, 
                                                                                        invalidate)
        elif mode == FileTransformationModes.Repair:
            # TODO repairing should be able to perform the same normalization as for NormalizeOnly 
            individual_file_repair_processor = self.__create_repairing_file_repair_processor(required_includes, 
                                                                                             local_source_resource_resolver, 
                                                                                             is_implementation_file_func, 
                                                                                             generation_strategy, 
                                                                                             required_include_files_calculator_class, 
                                                                                             include_list_generator_factory=include_list_generator_factory)
        else:
            raise ValueError("Invalid file repair mode")
        if closure:
            file_repair_processor = ClosureFileRepairProcessor(
                decoratee=individual_file_repair_processor)
        else:
            file_repair_processor = individual_file_repair_processor
        return file_repair_processor
