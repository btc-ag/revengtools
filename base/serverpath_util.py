'''
Created on 07.10.2010

@author: SIGIESEC
'''
from base.serverpath_if import ServerPath
from commons.os_util import FileTools

config_path_tools = ServerPath

def server_loc(file_server_path):
    """
    Gets the number of lines of filename after mapping the filename from the server space 
    to the local space.
    """
    # TODO this should be converted to using a ResourceResolver that does the mapping
    return FileTools.file_len(config_path_tools.server_to_local_path(file_server_path))
