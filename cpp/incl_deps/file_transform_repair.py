'''
Created on 18.02.2012

@author: SIGIESEC
'''
from base.project_default import DefaultProjectFile
from commons.core_util import isinstance_or_duck
from cpp.incl_deps.file_transform_base import IndividualCppFileTransformer
from cpp.incl_deps.repair_includes_base import BaseFileNormalizer
from cpp.incl_deps.repair_includes_if import RequiredIncludeFilesCalculator

def RepairingIndividualFileRepairProcessor(local_source_resource_resolver, generation_strategy, is_implementation_file_func, required_include_files_calculator, include_list_generator_factory): 
    assert isinstance_or_duck(required_include_files_calculator, RequiredIncludeFilesCalculator)
    prepare_func = lambda repair_path_rel_to_root_unix, input_resource: required_include_files_calculator.calculate_required_include_files(
                    project_file=DefaultProjectFile(path_rel_to_root_unix=repair_path_rel_to_root_unix, 
                                                   #module_name, 
                                                   local_repository_root=input_resource.get_resolution_root(), 
                                                   resource=input_resource)) 

    file_normalizer = BaseFileNormalizer(is_implementation_file_func=is_implementation_file_func, include_list_generator_factory=include_list_generator_factory)
    process_func = lambda repair_path, intermediate_result, input_file, output_file: file_normalizer.process(repair_path=repair_path, included_paths=intermediate_result, input_file=input_file, output_file=output_file)
    return IndividualCppFileTransformer(local_source_resource_resolver=local_source_resource_resolver,
                                         generation_strategy=generation_strategy,
                                         prepare_func=prepare_func,
                                         process_func=process_func)
