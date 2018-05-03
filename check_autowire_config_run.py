#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 09.09.2010

@author: SIGIESEC
'''
from commons.config_plain import PlainAutoWireConfigParser
from commons.config_util import AutoWireConfigChecker
import logging
import sys

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    checker = AutoWireConfigChecker()
    gen = PlainAutoWireConfigParser(entry_hook=checker.check_entry)
    map(None, gen.parse_files(sys.argv[1:]))
    problems = checker.get_problems()
    for (severity, description, context) in problems:
        print "%s: %s at %s" % (severity, description, context)
    print "%i problems" % (len(problems))
    
if __name__ == '__main__':
    main()
