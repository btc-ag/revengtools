'''
Created on 26.09.2010

@author: SIGIESEC
'''
from systems.prins.header_linker import PRINSHeaderLinker
import unittest
import cpp.header_linker_default
import base.generic_files_util
from cpp.cpp_default import DefaultCppFileConfiguration
from cpp.msvc.file_supply import FileMSVCDataSupply
from cpp.file_supply import FileCppDataSupplier, FileFileToModuleMapSupply
from configuration.config_base import RevEngToolsBasicConfig

header_linker_class = PRINSHeaderLinker

class HeaderLinkerTest(unittest.TestCase):
    # TODO the test should not use external data, which may change over time...
    
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
    
    @staticmethod
    def __test_internal(header_linker, header):
        #header_linker.outputter().clear_dict()
        header_linker.link_header(header)
        result_dict = header_linker.outputter().get_dict()
        if header in result_dict: 
            return result_dict[header]
        else:
            return None

    def setUp(self):
        # TODO this should not be used in a regular test
#        from commons.configurator import Configurator
#        Configurator().default()
        cpp.header_linker_default.config_cpp_data_supply = FileCppDataSupplier()
        cpp.header_linker_default.config_cpp_file_configuration = DefaultCppFileConfiguration()
        cpp.header_linker_default.config_file_to_module_map_supply = FileFileToModuleMapSupply()
        basic_config = RevEngToolsBasicConfig()
        base.generic_files_util.config_basic = basic_config
        cpp.file_supply.config_basic = basic_config
        self.header_linker = header_linker_class()
        
    def tearDown(self):
        self.header_linker = None

    def test1(self):
        self.assertEquals('ProcessVariableEventTracerClient', 
                          self.__test_internal(self.header_linker, 'processvariable/eventtracerclient/include/client.h'))
    def test2(self):
        self.assertEquals('ProcessVariableDataTransferObjectAPI',
                          self.__test_internal(self.header_linker, 'processvariable/eventtracerclient/include/binarystream.h'))
    def test3(self):
        self.assertEquals('ArchiveConfigurationLegacySpontaneous', 
                          self.__test_internal(self.header_linker, 'archivemanagement/utilspontan/include/archivepvutil.h'))
    def test4(self):
        self.assertEquals(None, 
                          self.__test_internal(self.header_linker, 'inc/stsc.df'))
    def test5(self):
        self.assertEquals(None, 
                          self.__test_internal(self.header_linker, 'inc/compiler.h'))
    def test6(self):
        self.assertEquals(None, 
                          self.__test_internal(self.header_linker, 'inc/ststypes.dh'))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    