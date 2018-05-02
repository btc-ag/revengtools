#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 11.11.2010

@author: SIGIESEC
'''
from infrastructure.graph_layout.graphviz.graphviz_executor import SVGScriptInjector
import sys

def main():
    SVGScriptInjector(sys.stdin, sys.stdout, ['graphviz-tools.js']).inject()

if __name__ == "__main__":
    main()
