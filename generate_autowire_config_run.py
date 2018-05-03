#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 09.09.2010

@author: SIGIESEC
'''
from commons.config_plain import PlainAutoWireFormatSuite
from commons.config_util import (ModuleEnumerator, ModuleScanner, 
    AbstractsToConcreteMap)
import logging

def main():
    modules = ModuleEnumerator.find_modules(".")
    scanner = ModuleScanner()
    for module in modules:
        print "Scanning module %s" % (module,),
        try:
            scanner.gather_autoconfigurables_by_name(module)
            print "OK"
        except ImportError, exc:
            logging.debug("Scanning %s failed, reason: %s", module, exc)
            print "FAILED"
        
    gen = PlainAutoWireFormatSuite().get_unparser(AbstractsToConcreteMap(scanner.get_autoconfigurables()).get_map())
    
    out_file = open("autowire.config.in", "w")
    out_file.write(str(gen))
    out_file.close()
    
if __name__ == '__main__':
    main()
