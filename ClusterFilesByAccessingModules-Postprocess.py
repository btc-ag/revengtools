#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from casttools import CastToolsConfigParser, CastSizeNode
from clustering_graphviz import AbstractClusteringGraphvizOutput
import casttools
import clustering
import collections
import csv
import graphviz
import logging
import os
import pprint
import re
import sys

logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)

if len(sys.argv) <= 2:
	sys.exit("Aufrufsyntax: $0 [Ausgabe aus ClusterFilesByAccessingModules] [Operationsdatei]")

inputFilename = sys.argv[1]
operationFilename = sys.argv[2]

moduleDependenciesClustered = casttools.basic_clustering(inputFilename, operationFilename)

class ModulesFilesClusteringGraphvizOutput(AbstractClusteringGraphvizOutput):
	split_rest = True

	def sizeable_nodes(self):
		return [node for node, nodelabel in self.nodes.iteritems() if casttools.is_fullname(nodelabel[0])]
		
class CastModulesFilesClusteringGraphvizOutput(CastSizeNode, ModulesFilesClusteringGraphvizOutput):
	__empty__ = 0


globalconfig = CastToolsConfigParser()	
output = CastModulesFilesClusteringGraphvizOutput()
output.process(moduleDependenciesClustered)
if globalconfig.get("OUTPUT", "DOT").upper().find("TEXT") >= 0:
	clustering.print_dependencies_order(clustering.key_set_to_csv(moduleDependenciesClustered), 
	lambda x: casttools.full_to_basename(x) + ":" + str(casttools.cast_loc_caching(x)),
	lambda x: x,
	lambda dependencies: 
		lambda x,y: cmp(casttools.total_size_caching(dependencies[y]), casttools.total_size_caching(dependencies[x])))
if globalconfig.get("OUTPUT", "DOT").upper().find("DOT") >= 0:
	output.output_graphviz()
