'''
Created on 23.09.2010

@author: SIGIESEC
'''

from commons.configurator import Configurator
from cpp.cpp_if import FileToModuleMapSupply
import logging
import pprint
import sys

config_file_to_module_map_supply = FileToModuleMapSupply()

def check(pathname, mymap):
    print("%s: %s" %(pathname, str(pathname in mymap)))

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    Configurator().default()
    impl_file_to_modules = config_file_to_module_map_supply.get_implementation_file_to_module_map()
    pprint.pprint(impl_file_to_modules)
    check("archivemanagement/api/src/archiveconfiguration.cpp", impl_file_to_modules)
    
    header_file_to_modules = config_file_to_module_map_supply.get_header_file_to_module_map()
    check("processvariable/types/include/pvtypes.h", header_file_to_modules)
    pprint.pprint([(path, module) for (path, module) in header_file_to_modules.iteritems() 
           if path.find("processvariable") != -1])
