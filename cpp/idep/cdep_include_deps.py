'''
Created on 22.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from commons.os_util import execute_shell_script
from cpp.incl_deps.include_deps_if import IncludeDependencyGenerator
import os.path
import sys

config_basic = BasicConfig()

class CdepIncludeDependencyGenerator(IncludeDependencyGenerator):

    def generate(self):
        script_path = os.path.join(os.path.dirname(sys.modules[CdepIncludeDependencyGenerator.__module__].__file__), "cdep_include_deps.sh")
        execute_shell_script(script_path)

    def incremental_generate(self):
        pass
        # TODO
        # if solution_file_changed:
        #    generate for new projects
        #    remove for removed projects
        # if vcproj_changed:
        #    generate for new files
        #    remove for removed files
        # for all changed files:
        #    regenerate