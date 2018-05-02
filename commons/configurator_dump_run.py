"""
Tool to dump the active configuration according to autowire.config files.

Created on 17.08.2012

@author: SIGIESEC
"""
from commons.configurator import _ConfiguratorInternal, Configurator
from commons.config_plain import PlainAutoWireConfigGenerator
from commons.config_util import ConfigTools

# TODO for each line, also output the source of this line (file and line number)
# TODO also include arguments

def dump():
    configurator = _ConfiguratorInternal()
    configurator.load_configuration(flavors=[])
    abstracts_to_concrete_map = configurator.get_adapter_map()
    args_map = dict(abstracts_to_concrete_map.itervalues())
    generator = PlainAutoWireConfigGenerator(abstracts_to_concrete_map,
                                             selection_strategy_func=lambda abstract, concretes: concretes[0],
                                             # select the single concrete adapter for each abstract adapter                                             
                                             args_func=lambda concrete_name: args_map[ConfigTools.fqn_to_pair(concrete_name)], 
                                             )
    for line in generator.get_configuration_lines(): 
        print line

if __name__ == "__main__":
    Configurator().default()
    dump()
