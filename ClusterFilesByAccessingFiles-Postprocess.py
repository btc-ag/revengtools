#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from cast.castutils import full_to_basename
from clustering_graphviz import AbstractClusteringGraphvizOutput
import cast.clustering.clustering_cast
import clustering.clustering
import collections
import csv
import graphviz
import logging
import os
import pprint
import sys

logging.basicConfig(stream = sys.stderr, level = logging.DEBUG)

if len(sys.argv) <= 1:
	sys.exit("Aufrufsyntax: $0 [Ausgabe aus ClusterFilesByAccessingFiles]")

inputFilename = sys.argv[1]

globalconfig = CastToolsConfigParser()
globalconfig.put("MIN_SIMILARITY", "3")
moduleDependenciesClustered = clustering_cast.basic_clustering(inputFilename)

class FilesFilesClusteringGraphvizOutput(AbstractClusteringGraphvizOutput):
	# TODO Knoten nur zusammenf�hren, wenn dadurch keine neuen ausgehenden Abh�ngigkeiten entstehen!
	# Hierzu kann die bisherige Identifikation von ähnlichen Knoten einfach umgedreht werden!

	split_rest = False
	max_node_size = 20.0
	min_node_size = 3.0

	def node_color(self, node):
		if self.in_links(node) == 0:
			return "yellow"
		elif self.out_links(node) == 0:
			return "green"
		else:
			return super(FilesFilesClusteringGraphvizOutput, self).node_color(node)

	def find_remaining(self, moduleDependenciesClustered, clusterKey):
		"""
		>>> x = FilesFilesClusteringGraphvizOutput()
		>>> 
		"""
		# TODO kopiert die folgende Zeile die Daten?
		rest = list(clusterKey)
		for file in clusterKey:
			if self.find_dependencies(moduleDependenciesClustered, moduleDependenciesClustered[clusterKey], file, self.cluster_node_name) > 0:
				rest.remove(file)
		return tuple(rest)

class CastFilesFilesClusteringGraphvizOutput(CastSizeNode, FilesFilesClusteringGraphvizOutput):
	def output_text(self):
		dependencies = dict()
		i = 1
		for toNode in self.nodes:
			fromNode = set()
			for (n1, n2) in self.edges:
				if n2 == toNode:
					fromNode.update(self.nodes[n1])
			frozenFromNode = frozenset(fromNode)
			if frozenFromNode in dependencies:
				logging.debug("Duplicate fromNode %s, old val = %s, new val = %s" % (frozenFromNode, dependencies[frozenFromNode], self.nodes[toNode]))
				if frozenFromNode == set():
					frozenFromNode = (str(i))
					i += 1
				else:
					raise BaseException("Internal error")
			dependencies.update({frozenFromNode: self.nodes[toNode]})
		#for (fromNode, toNode) in self.edges:
		#	dependencies.update({self.nodes[fromNode]: self.nodes[toNode]})	
		clustering.print_dependencies_order(clustering.key_set_to_csv(dependencies),
		lambda x: full_to_basename(x) + ":" + str(casttools.cast_loc_caching(x)),
		lambda x: ",".join(map(lambda y: full_to_basename(y), x.split(","))),
		lambda dependencies:
			lambda x, y: cmp(casttools.total_size_caching(dependencies[y]), casttools.total_size_caching(dependencies[x])))


	__empty__ = 0

output = CastFilesFilesClusteringGraphvizOutput()
output.process(moduleDependenciesClustered)
output.pick_top(len(output.nodes) * 0.25, None)
if globalconfig.get("OUTPUT", "DOT").upper().find("TEXT") >= 0:
	output.output_text()
	# clustering.print_dependencies_order(clustering.key_set_to_csv(moduleDependenciesClustered), 
		# lambda x: os.path.basename(x.strip("[]")) + ":" + str(casttools.cast_loc_caching(x)),
		# lambda x: ",".join(map(lambda y: os.path.basename(y.strip("[]")), x.split(","))),
		# lambda dependencies: 
			# lambda x,y: cmp(casttools.total_size_caching(dependencies[y]), casttools.total_size_caching(dependencies[x])))
if globalconfig.get("OUTPUT", "DOT").upper().find("DOT") >= 0:
	output.output_graphviz()
