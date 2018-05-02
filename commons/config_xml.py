'''
Created on 30.05.2011

@author: SIGIESEC
'''
from commons.config_extension_if import IAutoWireFormatSuite
from commons.config_util import AutoWireConfigParserBase, ConfigTools
import xml.dom.minidom

# TODO explicit inclusion of config files should be supported by the XML format
# TODO specification of non-autowire instances should be possible

class XMLAutoWireFormatSuite(IAutoWireFormatSuite):
    def get_parser(self):
        return XMLAutoWireConfigParser()

    def get_unparser(self, abstracts_to_concrete_map):
        raise NotImplementedError(self.__class__)

class XMLAutoWireConfigParser(AutoWireConfigParserBase):
    NAMESPACE_URI="http://www.btc-ag.com/ArchitectureManagement/PyIoC"
    
    def __init__(self):
        AutoWireConfigParserBase.__init__(self)
        pass

    def __parse_parameter(self, parameter):
        name = parameter.getAttribute("name")
        value_dict = dict()
        value_dict["value"] = parameter.getAttribute("value")
        type = parameter.getAttribute("type")
        if type:
            value_dict["type"] = type
#        else:
#            value_dict["type"] = "str"
        return (name, value_dict)

    def __parse_autowire(self, autowire):
        abstract = autowire.getAttribute("abstract")
        concrete = autowire.getAttribute("concrete")
        return (ConfigTools.fqn_to_pair(abstract), 
                (ConfigTools.fqn_to_pair(concrete), 
                 dict(self.__parse_parameter(parameter) 
                      for parameter in autowire.getElementsByTagNameNS(self.NAMESPACE_URI, "parameter"))))
    
    
    def __parse_autowiring(self, autowiring_element):
        autowires = autowiring_element.getElementsByTagNameNS(self.NAMESPACE_URI, "autowire")
        for autowire in autowires:
            yield self.__parse_autowire(autowire)
    
    
    def __parse_config(self, config_element):
        autowiring = config_element.getElementsByTagNameNS(self.NAMESPACE_URI, "autowiring")
        if len(autowiring):
            return self.__parse_autowiring(autowiring[0])
        else:
            # TODO warn: self._errors.add()
            return ()
    
    
    def parse_lines(self, lines):
        dom = xml.dom.minidom.parse(lines)
        return self.__parse_config(dom.getElementsByTagNameNS(self.NAMESPACE_URI, "config")[0])
    


