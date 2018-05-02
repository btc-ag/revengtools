# -*- coding: UTF-8 -*-

# Original copyright notice:
#
# Copyright 2004 Toby Dickenson
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from base.dependency.dependency_default import DefaultDependencyFilter
from base.dependency.dependency_if import DependencyFilterConfiguration,\
    DependencyFilter
import imp
from base.modules_if import ModuleListSupply

class PydepTools(object):
    @staticmethod
    def stopat(s, type):
        """
        @return: True if the module should be drawn, but its dependencies should not be 
        considered, even if the dependency target is drawn as well.
        """
        if s in ('modulefinder', 'md5', 'csv', 're', 'doctest', 'datetime', 'pprint', 
                 'logging', 'warnings', 'os', 'threading', 'urllib', 'timeit', 'platform', 
                 'Queue', 'optparse', 'urllib2', 'mimetools', 'urlparse', 'thread', 'textwrap', 
                 'xml.dom.minidom',
                 'xml.parsers.expat'):
            return True
        return False

    @staticmethod
    def use(s, type):
        """
        Return true if this module is interesting and should be drawn. Return false
        if it should be completely omitted. 
        """
        if s in ('os', 'copy', 'ntpath', 'sys', 'qt', 'time', '__future__', 'types', 
                 'string', 'collections', 'subprocess', 'pickle', 'UserDict', 'pdb', 
                 'inspect', 'tempfile', 'unittest', 'traceback', 'doctest', 'warnings', 
                 're', 'posixpath', 'pprint', 'math', 'weakref', 'itertools', 'functools'):
            # nearly all modules use all of these... more or less. They add nothing to
            # our diagram.
            return 0
        if s.startswith('encodings.'):
            return 0
        if s.endswith('__init__'):
            return 0
        if s == '__main__':
            return 1
        if PydepTools.toocommon(s, type):
            # A module where we dont want to draw references _to_. Dot doesnt handle these
            # well, so it is probably best to not draw them at all.
            return 0
        return 1

    @staticmethod
    def toocommon(s, type):
        # Return true if references to this module are uninteresting. Such references
        # do not get drawn. This is a default policy - please override.
        #
        if s == '__main__':
            # references *to* __main__ are never interesting. omitting them means
            # that main floats to the top of the page
            return 1
        if type == imp.PKG_DIRECTORY:
            # dont draw references to packages.
            return 1
        return 0

config_module_list = ModuleListSupply()

class pydepgraphdot:
    def __init__(self, depgraph, types, filter=None):
        self.__depgraph = depgraph
        self.__types = types
        self.colored = 1
        assert isinstance(filter, DependencyFilter)
        self.__filter = filter

#    def main(self,argv):
#        opts,args = getopt.getopt(argv,'',['mono'])
#        for o,v in opts:
#            if o=='--mono':
#                self.colored = 0
#        self.render()

    
    def render(self, start=['__main__']):
        p = self.__depgraph
        t = self.__types
        # TODO so sollte das natürlich nicht geschehen...
        if self.__filter == None:
            self.__filter = DefaultDependencyFilter(config=DependencyFilterConfiguration(), 
                                                    module_list=config_module_list.get_module_list()) 
                #PydepGraphOutputter(colored=self.colored, 
                #                                   types=t, 
                #                                   outfile=sys.stdout,
                #                                   output_groups=True,
                #                                   nodes=,
                #                                   edges=)

        # normalise our input data
        for k, d in p.items():
            for v in d.keys():
                if not p.has_key(v):
                    p[v] = {}
                    
        allkd = p.items()
        allkd.sort()
        output_k = set(start)
        edges = set()
        changed = True
        # TODO das ist ja grausam ... aber sollte funktionieren
        while changed:
            changed = False
            for k, d in allkd:
                tk = t.get(k)
                if PydepTools.use(k, tk) and k in output_k and not PydepTools.stopat(k, tk):
                    allv = d.keys()
                    allv.sort()
                    for v in allv:
                        tv = t.get(v)
                        if PydepTools.use(v, tv) and not PydepTools.toocommon(v, tv) \
                                and (k, v) not in edges:
                            edges.add((k, v))
                            self.__filter.dependency(k, v)
                            if k not in output_k:
                                output_k.add(k)
                                changed = True
                            if v not in output_k:
                                output_k.add(v)
                                changed = True
        #ks = set([x[0] for (x,y) in allkd if len(y) > 0])
        self.__filter.postamble()
                
if __name__ == "__main__":
    import doctest
    doctest.testmod()



