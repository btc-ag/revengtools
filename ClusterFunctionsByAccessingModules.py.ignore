#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from cast.castutils import is_func_fullname, func_full_to_readable_name
from cast.clustering.clustering_cast import basic_clustering
from clustering.clustering import print_dependencies_order, key_set_to_csv
from clustering.clustering_graphviz import AbstractClusteringGraphvizOutput
from configuration.revengtools_config import RevEngToolsConfigParser
import logging
import sys

logging.basicConfig(stream = sys.stderr, level = logging.DEBUG)

if len(sys.argv) <= 2:
    sys.exit("Aufrufsyntax: $0 [Ausgabe aus ClusterFilesByAccessingModules] [Operationsdatei]")

inputFilename = sys.argv[1]
operationFilename = sys.argv[2]

globalconfig = RevEngToolsConfigParser()
globalconfig.put("MIN_SIMILARITY", "0.1")
moduleDependenciesClustered = basic_clustering(inputFilename, operationFilename)

class ModulesFunctionsClusteringGraphvizOutput(AbstractClusteringGraphvizOutput):
    split_rest = True

#    def sizeable_nodes(self):
#        return [node for node, nodelabel in self.nodes.iteritems() if casttools.is_fullname(nodelabel[0])]

    def format_label(self, label):
        if is_func_fullname(label):
            return func_full_to_readable_name(label)
        else:
            return super(ModulesFunctionsClusteringGraphvizOutput, self).format_label(label)


globalconfig = RevEngToolsConfigParser()
output = ModulesFunctionsClusteringGraphvizOutput()
output.process(moduleDependenciesClustered)
if globalconfig.get("OUTPUT", "DOT").upper().find("TEXT") >= 0:
    print_dependencies_order(key_set_to_csv(moduleDependenciesClustered),
    func_full_to_readable_name,
#    lambda x: os.path.basename(x.strip("[]")) + ":" + str(casttools.cast_loc_caching(x)),
    lambda x: x,
    lambda dependencies:
        lambda x, y: cmp(len(dependencies[y]), len(dependencies[x])))
if globalconfig.get("OUTPUT", "DOT").upper().find("DOT") >= 0:
    output.output_graphviz()
