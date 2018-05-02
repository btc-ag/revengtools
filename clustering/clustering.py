#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from commons.core_util import CollectionTools, DictReaderTools,\
    SetValuedDictTools
from itertools import imap
import logging
import pprint
import copy

# TODO Convert to classes
# TODO Should use and return the Graph class from package graph


def print_dependencies(dependencies):
    """
    >>> print_dependencies({'a': 'x', 'b': 'x', 'c': 'y'})
    a = x
    b = x
    c = y
    """
    for moduleName in sorted(dependencies.keys()):
        print moduleName, "=", dependencies[moduleName]

def print_dependencies_order(dependencies, formatFilename = None,
                             formatModulename = lambda x: x,
                             order = lambda dependencies: lambda x, y: cmp(len(dependencies[y]), len(dependencies[x]))):
    """
    >>> print_dependencies_order({'c': ['x', 'y', 'z'], 'a': ['x1', 'x2'], 'b': ['y']})
    { x y z } c
    { x1 x2 } a
    { y } b
    """
    for moduleName in sorted(dependencies.keys(), order(dependencies)):
        print \
            "{", \
            " ".join(sorted(map(formatFilename, dependencies[moduleName]))), \
            "}", \
            formatModulename(moduleName)

class BasicOperations(object):
    @staticmethod
    def join_modules(dependencies, targetModule, sourceModules):
        """
        Joins the specified source modules in the list of dependencies into the target module, 
        which may or may not exist previously.
        
        >>> BasicOperations.join_modules({}, 'x', ['y'])
        {}
    
        >>> pprint.pprint(BasicOperations.join_modules({'x': set(['a', 'b']), 'y': set(['c'])}, 'x', ['y']))
        {'x': set(['a', 'b', 'c'])}
        
        >>> pprint.pprint(BasicOperations.join_modules({'x': set(['a', 'b']), 'y': set(['c'])}, 'x', ['y']))
        {'x': set(['a', 'b', 'c'])}
        
        >>> pprint.pprint(BasicOperations.join_modules({'x': set(['a', 'b']), 'y': set(['c'])}, 'x', ['z']))
        {'x': set(['a', 'b']), 'y': set(['c'])}
        
        >>> pprint.pprint(BasicOperations.join_modules({frozenset(['x']): set(['a', 'b']), frozenset(['y']): set(['c'])}, frozenset(['x']), [frozenset(['z'])]))
        {frozenset(['y']): set(['c']), frozenset(['x']): set(['a', 'b'])}
        """
        return SetValuedDictTools.join_keys(dependencies, targetModule, sourceModules)
    
    @staticmethod
    def delete_module(dependencies, targetModule):
        """
        >>> BasicOperations.delete_module({'x': set(['a', 'b']), 'y': set(['c'])}, 'y')
        {'x': set(['a', 'b'])}
    
        >>> BasicOperations.delete_module({'y': set(['c'])}, 'y')
        {}
    
        >>> BasicOperations.delete_module({'y': set(['c'])}, 'z')
        {'y': set(['c'])}
        """
        if targetModule in dependencies:
            del dependencies[targetModule]
        return dependencies
    
class OperationProcessor(object):
    def __init__(self, inputFileReader, operationFileReader):
        self.__inputDictIter = inputFileReader
        self.__operationDictIter = operationFileReader
        self.__moduleDependenciesClustered = None
    
    @staticmethod
    def join_and_delete_modules(inDependencies, operationFileReader, deletedDependencies):
        """
        Processes a dictionary of dependencies given a list of operations.
        Supported operations are JOIN, DELETE and KILL. Operations may be commented out by using the prefix "no".
        
        >>> OperationProcessor.join_and_delete_modules({}, [], None)
        {}
    
        >>> OperationProcessor.join_and_delete_modules({}, [{'operation': 'JOIN', 'targetModule': 'x', 'sourceModules': ['y']}], None)
        {}
    
        >>> pprint.pprint(OperationProcessor.join_and_delete_modules({'x': set(['a', 'b']), 'y': set(['c'])}, [{'operation': 'JOIN', 'targetModule': 'x', 'sourceModules': ['y']}], None))
        {'x': set(['a', 'b', 'c'])}
    
        >>> OperationProcessor.join_and_delete_modules({'x': set(['a', 'b']), 'y': set(['c'])}, [{'operation': 'JOIN', 'targetModule': 'z', 'sourceModules': ['x', 'y']}], None)
        {'z': set(['a', 'c', 'b'])}
    
        >>> OperationProcessor.join_and_delete_modules({'x': set(['c']), 'y': set(['c'])}, [{'operation': 'DELETE', 'targetModule': 'y'}], None)
        {'x': set(['c'])}
    
        >>> deletedDependencies = dict()
        >>> OperationProcessor.join_and_delete_modules({'y': set(['c'])}, [{'operation': 'DELETE', 'targetModule': 'y'}], deletedDependencies)
        {}
        >>> deletedDependencies
        {'y': set(['c'])}
    
        >>> deletedDependencies = dict()
        >>> OperationProcessor.join_and_delete_modules({'x': set(['c']), 'y': set(['c'])}, [{'operation': 'DELETE', 'targetModule': 'y'}, {'operation': 'DELETE', 'targetModule': 'x'}], deletedDependencies)
        {}
        >>> deletedDependencies == {'x': set(['c']), 'y': set(['c'])}
        True
        """
        # TODO Is it correct that the function operates on the original  
        #      dependencies dict? If yes, this should be stated in the docstring.
        dependencies = inDependencies
        for row in operationFileReader:
            if    row['operation'] == 'JOIN':
                BasicOperations.join_modules(dependencies, row['targetModule'], row['sourceModules'])
            elif  row['operation'] == 'DELETE':
                if deletedDependencies != None:
                    deletedDependencies.update(
                        {row['targetModule']: dependencies.get(row['targetModule'], set())})
                BasicOperations.delete_module(dependencies, row['targetModule'])
            elif  row['operation'] == 'KILL':
                BasicOperations.delete_module(dependencies, row['targetModule'])
            elif  row['operation'].startswith('no'):
                # Operation is commented out
                pass
            else:
                raise ValueError("Unknown operation %s" % [row['operation']])
    
        return dependencies


    @staticmethod
    def read_dependencies(inputFileReader):
        """
        >>> OperationProcessor.read_dependencies([])
        {}
        
        >>> OperationProcessor.read_dependencies([{'callingModule': 'x', 'calledFile': 'a'}])
        {'x': set(['a'])}
    
        >>> OperationProcessor.read_dependencies([{'callingModule': 'x', 'calledFile': 'a'}, {'callingModule': 'x', 'calledFile': 'b'}])
        {'x': set(['a', 'b'])}
        """
        return DictReaderTools.transform_to_set_valued_dict(inputFileReader, 
                                                            keyKey='callingModule', 
                                                            valueKey='calledFile')

    @staticmethod
    def join_missing_files(_fileDependencies, deletedFileDependencies):
        """
        >>> OperationProcessor.join_missing_files({}, {'c': set(['x', 'y'])})
        {'c': set(['y', 'x'])}
    
        >>> OperationProcessor.join_missing_files({'c': set(['z'])}, {'c': set(['x', 'y'])})
        {'c': set(['z'])}
        """
        fileDependencies = _fileDependencies
        for curFile in deletedFileDependencies:
            if curFile not in fileDependencies:
                fileDependencies.update({curFile: deletedFileDependencies[curFile]})
        return fileDependencies

    def get_target_groups(self):
        if self.__moduleDependenciesClustered == None:
            moduleDependencies = OperationProcessor.read_dependencies(self.__inputDictIter)
            deletedDependencies = dict()
            moduleDependencies = self.join_and_delete_modules(moduleDependencies, self.__operationDictIter,
                                    deletedDependencies)
            fileDependencies = LocalCollectionTools.convert_module_list_to_file_list(moduleDependencies)
            deletedFileDependencies = LocalCollectionTools.convert_module_list_to_file_list(deletedDependencies)
            fileDependencies = self.join_missing_files(fileDependencies, deletedFileDependencies)
            #fileDependencies = value_set_to_csv(fileDependencies)
            fileDependencies = CollectionTools.value_set_to_tuple(fileDependencies)
        
            #print_dependencies(fileDependencies)
            self.__moduleDependenciesClustered = CollectionTools.transpose(fileDependencies)
    
        return self.__moduleDependenciesClustered

class LocalCollectionTools(object):
    @staticmethod
    def convert_module_list_to_file_list(moduleDependencies):
        """
        Converts a module-to-set(file)-dictionary to a file-to-set(module)-dictionary.
        
        >>> pprint.pprint(LocalCollectionTools.convert_module_list_to_file_list({'x': set(['a', 'b']), 'y': set(['c'])}))
        {'a': set(['x']), 'b': set(['x']), 'c': set(['y'])}
        
        >>> print_dependencies(CommaSeparationTools.value_set_to_csv(LocalCollectionTools.convert_module_list_to_file_list({'x': set(['a', 'b']), 'y': set(['c'])})))
        a = x
        b = x
        c = y
        """
        return SetValuedDictTools.transpose(moduleDependencies)

class CommaSeparationTools(object):
    @staticmethod
    def to_csv(listOfStrings):
        """
        >>> CommaSeparationTools.to_csv(['c', 'b', 'a'])
        'c,b,a'
        
        >>> CommaSeparationTools.to_csv([])
        ''
        """
        return ','.join(listOfStrings)
    
    @staticmethod
    def to_csv_sorted(listOfStrings):
        """
        >>> CommaSeparationTools.to_csv_sorted(set(['c', 'b', 'a']))
        'a,b,c'
    
        >>> CommaSeparationTools.to_csv_sorted([])
        ''
        """
        return CommaSeparationTools.to_csv(sorted(listOfStrings))
    
    @staticmethod
    def value_set_to_csv(dictionary):
        """
        Takes a set-of-strings-valued dictionary and returns a new dictionary after sorting 
        each value set and concatenating the string values by commas.
        
        >>> CommaSeparationTools.value_set_to_csv({'x': set(['a', 'b'])})
        {'x': 'a,b'}
    
        >>> CommaSeparationTools.value_set_to_csv({'x': set([])})
        {'x': ''}
        """
        for key in dictionary:
            dictionary[key] = CommaSeparationTools.to_csv_sorted(dictionary[key])
        return dictionary
    
    @staticmethod
    def key_set_to_csv(inDictionary):
        """
        
        >>> CommaSeparationTools.key_set_to_csv({frozenset(['a', 'b']) : 'x'})
        {'a,b': 'x'}
    
        >>> CommaSeparationTools.key_set_to_csv({frozenset([]): 'x'})
        {'': 'x'}
        """
        outDictionary = dict()
        for key in inDictionary:
            outDictionary[CommaSeparationTools.to_csv_sorted(key)] = inDictionary[key]
        return outDictionary

def distance(tuple1, tuple2):
    """
    Calculates the absolute distance of two iterables, returns values between 
    0 and len(tuple1) + len(tuple2) .
    
    >>> distance(('a'), ())
    1
    
    >>> distance(('a'), ('a'))
    0
    
    >>> distance(['a', 'b'], ('b', 'c'))
    2
    
    >>> distance(['a', 'b'], ('c', 'd'))
    4
    """
    return len(set(tuple1).symmetric_difference(set(tuple2)))

def distance_rel(tuple1, tuple2):
    """
    Calculates the relative distance of two tuples, returns values between 0.0 and +inf.
    
    >>> distance_rel(('a'), ())
    inf
    
    >>> distance_rel(('a'), ('a'))
    0.0
    
    >>> distance_rel(['a', 'b'], ('b', 'c'))
    2.0

    >>> distance_rel(['a', 'b'], ('c', 'd'))
    inf
    """
    intersectCount = len(set(tuple1).intersection(set(tuple2)))
    if (intersectCount == 0.0):
        return float("+inf")
    else:
        return (0.0 + len(set(tuple1).symmetric_difference(set(tuple2)))) / (float(intersectCount))

def find_min_dist(allKeys, keysBelowThreshold, distanceThreshold, distance_function = distance):
    """
    >>> pprint.pprint(find_min_dist([frozenset(['a']), frozenset(['b'])], [frozenset(['a']), frozenset(['b'])], 1))
    None

    >>> pprint.pprint(find_min_dist([frozenset(['a']), frozenset(['b'])], [frozenset(['a']), frozenset(['b'])], 2))
    (frozenset(['b']), frozenset(['a']))
    """
    # TODO Nicht jedes Mal alle Distanzen neu berechnen, sondern zwischenspeichern und nur die geänderten neu berechnen
    minDist = distanceThreshold
    minKeyPair = None
    for key1 in keysBelowThreshold:
        for key2 in allKeys:
            thisDist = distance_function(key1, key2)
            if (thisDist <= minDist) and (thisDist > 0):
                minDist = thisDist
                minKeyPair = (key1, key2)
    return minKeyPair

def find_module_clusters(inModuleDependencies, distanceThreshold, sizeThreshold, size_fun = len):
    """
    Try to further reduce the number of clusters by merging the existing 
    module clusters, if their distance is less than distanceThreshold.
    
    size_fun should calculate the size of a value of inModuleDependencies, the 
    default is the length of the list.
    
    find_module_clusters does not try to further reduce clusters that are 
    larger than sizeThreshold.
    
    @return: A tuple-valued dictionary, which maps keys of tuples of source elements 
    to tuples of target elements.
    """
    moduleDependencies = CollectionTools.value_tuple_to_set(inModuleDependencies)

    # In einer Schleife wiederholen, bis in einem Schritt keine Änderung mehr stattgefunden hat

    minKeyPair = (0, 0)
    while minKeyPair != None:
        # Teilmenge der keys bestimmen, deren values den threshold nicht überschreiten
        keysBelowThreshold = [key for key in moduleDependencies.keys() if size_fun(moduleDependencies[key]) < sizeThreshold]
        #pprint.pprint(keysBelowThreshold)

        logging.info("Keys below size threshold %i" % len(keysBelowThreshold))

        # Für alle Paare die Distanz bestimmen und das Paar mit der minimalen Distanz zusammenfügen

        minKeyPair = find_min_dist(moduleDependencies.keys(),
								keysBelowThreshold,
								distanceThreshold,
								distance_rel)

        # TODO join_modules fügt nur die beiden Cluster zusammen, aber nicht tatsächlich die Module.
        # TODO join_modules müsste dafür erweitert werden für den Fall, dass die keys bereits iterables sind.
        # TODO oder ist das jetzige Verhalten sogar besser?
        if minKeyPair != None:
            logging.info("Joining %s and %s (distance %f)" ,
						minKeyPair[0], minKeyPair[1],
						distance_rel(minKeyPair[0], minKeyPair[1]))
            BasicOperations.join_modules(moduleDependencies, 
                         tuple(sorted(set(minKeyPair[0]) | set(minKeyPair[1]))), 
                         [minKeyPair[0], minKeyPair[1]])
    return CollectionTools.value_set_to_tuple(moduleDependencies)

def basic_clustering_generic(inputFileReader, operationFileReader, minimumSimilarity, maximumSize, size_func):
    """
    @return: A tuple-valued dictionary, which maps keys of tuples of source elements 
    to tuples of target elements.
    """
    moduleDependenciesClustered = OperationProcessor(inputFileReader, operationFileReader).get_target_groups() # Weitere Gruppierungen von Zugreifern finden
    logging.info("Number of files: %i", sum(imap(len, moduleDependenciesClustered.itervalues())))
    logging.info("Number of intermediate clusters: %i", len(moduleDependenciesClustered))
    moduleDependenciesClustered = find_module_clusters(moduleDependenciesClustered, float(minimumSimilarity), 
        float(maximumSize), 
        size_func)
#clustering.print_dependencies(moduleDependencies)
    logging.info("Number of resulting clusters: %i", len(moduleDependenciesClustered))
    return moduleDependenciesClustered

# doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
