'''
Created on 20.12.2011

@author: SIGIESEC
'''
from base.project_if import ProjectFile
from commons.os_util import FileResource
import os.path

class DefaultProjectFile(ProjectFile):
    def __init__(self, path_rel_to_root_unix, module_name=None, local_repository_root=None, resource=None, path_module=os.path):
        self.__module_name = module_name
        self.__local_repository_root = local_repository_root
        self.__path_rel_to_root_unix = path_rel_to_root_unix
        if resource:
            self.__resource = resource
        elif self.__local_repository_root:
            self.__resource = FileResource(path_module.join(self.__local_repository_root, self.__path_rel_to_root_unix))

    def get_module_name(self):
        return self.__module_name

    def get_local_repository_root(self):
        return self.__local_repository_root

    def get_path_rel_to_root_unix(self):
        return self.__path_rel_to_root_unix

    def get_resource(self):
        return self.__resource
    
    def __str__(self):
        return "DefaultProjectFile(resource=%s, relpath=%s, repository=%s, module=%s)" % (self.__resource, self.__path_rel_to_root_unix, self.__local_repository_root, self.__module_name)

    module_name = property(get_module_name, None, None, "module_name's docstring")
    local_repository_root = property(get_local_repository_root, None, None, "local_repository_root's docstring")
    path_rel_to_root_unix = property(get_path_rel_to_root_unix, None, None, "path_rel_to_root_unix's docstring")
    resource = property(get_resource, None, None, "resource's docstring")

