# -*- coding: UTF-8 -*-

'''
Created on 26.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from base.dependency.module.linkdeps_if import ModuleLinkDepsSupply

# TODO Hier könnte man auch einen generischen Style-Checker zugrunde legen
# TODO statt der module_deps_supply könnte man auch nur den Graph übergeben
# TODO wenn die Klasse des module_groupers bekannt ist, könnte der module_grouper auch intern 
#      instanziert werden 

class EPMArchitecturalStyleChecker(AutoConfigurable):
    def __init__(self, module_grouper):
        pass
    
    def physical_rule_violations(self, module_deps_supply = ModuleLinkDepsSupply()):
        raise NotImplementedError
    
    def logical_rule_violations(self):
        raise NotImplementedError
