# -*- coding: UTF-8 -*-

'''
Created on 24.10.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from base.dependency.generation_log_if import GenerationLogSupply
from commons.configurator import Configurator
from commons.scm_default import FallbackVersionDescriber
from commons.scm_if import VersionDescriber
from epm.generation_log_output import EPMHTMLGeneratedGraphOverviewWriter
import os.path

config_generation_log_supply = GenerationLogSupply()
config_basic = BasicConfig()
config_version_describer = VersionDescriber()

def main():
    Configurator().default()
    output_file = open(os.path.join(config_basic.get_results_directory(),
            'index.html'), "wt")
    version_info = FallbackVersionDescriber(config_version_describer).describe_local_version(basepath=config_basic.get_local_source_base_dir(),
                                                                       detailed=False)
    generation_log = config_generation_log_supply.get_generation_log_iter()
    writer = EPMHTMLGeneratedGraphOverviewWriter(output_file, generation_log, (config_basic.get_system(),
               config_basic.get_version(),
               version_info[2],
               config_basic.get_local_source_base_dir_subset()))
    writer.write()

if __name__ == '__main__':
    main()
