# -*- coding: UTF-8 -*-

'''
Created on 26.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.graph.attrgraph_if import NodeGrouper
from commons.graph.attrgraph_util import NodeGroup

class OutputterConfiguration(AutoConfigurable):
    # TODO das wird eigentlich nicht benötigt, wenn der IoC-Container Listen unterstützen würde
    def outputters(self):
        return ()

class ModuleGroup(NodeGroup):
    pass

class DependencyChecker(AutoConfigurable):
    def is_legal_dependency(self, source, target):
        raise NotImplementedError(self.__class__)

class GraphDescription(object):
    def get_legend(self):
        raise NotImplementedError(self.__class__)

    def set_legend(self, value):
        raise NotImplementedError(self.__class__)

    def get_extra(self):
        raise NotImplementedError(self.__class__)

    def get_description(self):
        raise NotImplementedError(self.__class__)

    def set_extra(self, value):
        raise NotImplementedError(self.__class__)

    def get_section(self):
        raise NotImplementedError(self.__class__)

    def get_category(self):
        raise NotImplementedError(self.__class__)

    def get_full_description(self):
        raise NotImplementedError(self.__class__)

    def set_section(self, value):
        raise NotImplementedError(self.__class__)

    def set_category(self, value):
        raise NotImplementedError(self.__class__)

    def set_description(self, value):
        raise NotImplementedError(self.__class__)

    def set_basename(self, value):
        raise NotImplementedError(self.__class__)

    def get_filename(self):
        raise NotImplementedError(self.__class__)
   
# TODO an outputter should be able to handle different types of dependencies 
# (from different parsers), either in the general interface, or a decorator around
# multiple set dependency outputters
class DependencyFilter(AutoConfigurable):
    def __init__(self, config, module_list):
        raise NotImplementedError(self.__class__)        
    
    def dependency(self, source, target):
        raise NotImplementedError(self.__class__)
    
    # TODO postamble sollte eher write oderso heißen
    def postamble(self):
        raise NotImplementedError(self.__class__)
    
    # TODO set_node_size passt hier eigentlich nicht rein und wird auch nicht mehr benutzt
#    def set_node_size(self, node, height, width):
#        raise NotImplementedError(self.__class__)
    
    def graph(self):
        raise NotImplementedError(self.__class__)
    
class ModuleGrouper(NodeGrouper, AutoConfigurable):
    # TODO Eigentlich sollte das Interface besser DependencyUnitGrouper heißen
    
    # TODO Im Moment einstufig, aber auch mehrstufige Gruppierung unterstützen (z.B. Layer, Packages)

    pass

class DependencyFilterConfiguration(AutoConfigurable):
    def skip_module(self, _module):
        raise NotImplementedError(self.__class__)
    
    def skip_module_as_source(self, _source):
        raise NotImplementedError(self.__class__)
    
    def skip_module_as_target(self, _target):
        raise NotImplementedError(self.__class__)
    
    def skip_edge(self, _source, _target):
        raise NotImplementedError(self.__class__)
    
    # TODO das gehört hier nicht rein
    def get_edge_color(self, _source, _target):
        raise NotImplementedError(self.__class__)
        
    def get_module_grouper(self):
        raise NotImplementedError(self.__class__)
    
    def clone(self, modules):
        raise NotImplementedError(self.__class__)

class NodeColorer(AutoConfigurable):
    # TODO das gehört eher in commons.graph.output_if
    def get_node_color(self, node):
        raise NotImplementedError(self.__class__)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
