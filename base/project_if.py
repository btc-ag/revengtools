'''
Created on 20.12.2011

@author: SIGIESEC
'''
class ProjectFile(object):
    # TODO this should probably be renamed to ModuleResource
    
    def get_module_name(self):
        raise NotImplementedError(self.__class__)
    
    def get_resource(self):
        """
        Note: The resource may be not be local and it may be virtual or temporary. If a canonical path is 
        required, get_path_rel_to_root_unix should be used.
        
        @rtype: Resource
        """
        raise NotImplementedError(self.__class__)
    
    def get_local_repository_root(self):
        """
        @rtype: Resource
        """
        raise NotImplementedError(self.__class__)

    def get_path_rel_to_root_unix(self):
        """
        @rtype: string (relative posix path)
        """
        raise NotImplementedError(self.__class__)
    
