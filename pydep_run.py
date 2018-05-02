#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 21.09.2010

@author: SIGIESEC
'''
from base.dependency.dependency_base import NullModuleGrouper
from base.dependency.dependency_default import DefaultDependencyFilter,\
    NullDependencyFilterConfiguration
from base.dependency.dependency_if import ModuleGrouper
from commons.graph.output_base import BaseGraphOutputter
from hashlib import md5
from infrastructure.graph_layout.graphviz.graphviz import (
    GraphvizFormatterHelper)
from python.dependency_parser import PydepProcessor
from python.depgraph2dot import PydepTools
import colorsys
import imp
import logging
import sys
from base.modules_if import ModuleListSupply

class PydepGraphOutputter(BaseGraphOutputter):
    do_grouping = False

    def __init__(self, colored, types, output_groups, graph, outfile, node_grouper=NullModuleGrouper(), node_decorators=()):
        BaseGraphOutputter.__init__(self, output_groups, graph, outfile, node_grouper, node_decorators)
        assert isinstance(node_grouper, NullModuleGrouper), "cannot currently handle grouped graph"
        self.__types = types
        self.colored = colored

    def fix(self, s):
        # Convert a module name to a syntactically correct node name
        return GraphvizFormatterHelper.sanitize_node_name(s)

    def color(self, s, type):
        # Return the node color for this module name. This is a default policy - please override.
        #
        # Calculate a color systematically based on the hash of the module name. Modules in the
        # same package have the same color. Unpackaged modules are grey
        if PydepTools.stopat(s, type):
            t = "stop"
        else:
            t = self.normalise_module_name_for_hash_coloring(s, type)

        return self.color_from_name(t)

    def normalise_module_name_for_hash_coloring(self, s, type):
        if type == imp.PKG_DIRECTORY:
            return s
        else:
            i = s.rfind('.')
            if i < 0:
                return ''
            else:
                return s[:i]

    def color_from_name(self, name):
        n = md5(name).digest()
        hf = float(ord(n[0]) + ord(n[1]) * 0xff) / 0xffff
        sf = float(ord(n[2])) / 0xff
        vf = float(ord(n[3])) / 0xff
        r, g, b = colorsys.hsv_to_rgb(hf, 0.3 + 0.6 * sf, 0.8 + 0.2 * vf)
        return '#%02x%02x%02x' % (r * 256, g * 256, b * 256)


    def alien(self, a, b):
        # Return non-zero if references to this module are strange, and should be drawn
        # extra-long. the value defines the length, in rank. This is also good for putting some
        # vertical space between seperate subsystems. This is a default policy - please override.
        #
        return 0

    def weight(self, a, b):
        # Return the weight of the dependency from a to b. Higher weights
        # usually have shorter straighter edges. Return 1 if it has normal weight.
        # A value of 4 is usually good for ensuring that a related pair of modules 
        # are drawn next to each other. This is a default policy - please override.
        #
        if b.split('.')[-1].startswith('_'):
            # A module that starts with an underscore. You need a special reason to
            # import these (for example random imports _random), so draw them close
            # together
            return 4
        return 1

    def label(self, s):
        # Convert a module name to a formatted node label. This is a default policy - please override.
        #
        return '\\.\\n'.join(s.split('.'))

    def write_attributes(self, a):
        if a:
            self.file().write(' [')
            self.file().write(','.join(a))
            self.file().write(']')

    def node_attributes(self, k, type):
        a = []
        a.append('label="%s"' % self.label(k))
        if self.colored:
            a.append('fillcolor="%s"' % self.color(k, type))
        else:
            a.append('fillcolor=white')
        if PydepTools.toocommon(k, type):
            a.append('peripheries=2')
        return a

    def edge_attributes(self, k, v):
        a = []
        weight = self.weight(k, v)
        if weight != 1:
            a.append('weight=%d' % weight)
        length = self.alien(k, v)
        if length:
            a.append('minlen=%d' % length)
        return a

    def _output_edges(self):
        for (k, v) in self._graph().edges():
            self.file().write('%s -> %s' % (self.fix(k), self.fix(v)))
            self.write_attributes(self.edge_attributes(k, v))
            self.file().write(';\n')

    def _output_nodes(self):
        for k in self._graph().node_names():
            if PydepTools.use(k, None):
                self.file().write(self.fix(k))
                self.write_attributes(self.node_attributes(k, self.__types.get(k)))
                self.file().write(';\n')

    def _output_head(self):
        logging.info("_output_head, %i nodes, %i edges" % (len(tuple(self._graph().node_names())),
                                                            len(tuple(self._graph().edges()))))
        self.file().write('digraph G {\n') #f.write('concentrate = true;\n')
    #f.write('ordering = out;\n')
        self.file().write('ranksep=1.0;\n')
        self.file().write('node [style=filled,fontname=Calibri,fontsize=24];\n')

    def _output_tail(self):
        self.file().write('}\n')

config_module_grouper = ModuleGrouper
config_module_list = ModuleListSupply()

class PydepRunner(object):
    def main(self, paths, filter=DefaultDependencyFilter(config=NullDependencyFilterConfiguration(), module_list=config_module_list.get_module_list())):
        processor = PydepProcessor()
        processor.process(paths)
        processor.output(filter)
        PydepGraphOutputter(colored=True,
                            types=processor.types(),
                            output_groups=True,
                            graph=filter.graph(),
                            outfile=sys.stdout).output_all()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    PydepRunner().main(sys.argv[1:])
