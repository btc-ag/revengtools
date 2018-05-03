# -*- coding: utf-8 -*-

import collections
import json
import logging
import subprocess

TypeInformation = collections.namedtuple('TypeInformation', ['TypeName','Assembly'])

# TODO rename the module according to the naming convention to interface_dependency_extractor

class ExternalAnalyzerFailedError(Exception):
    pass

class WrongFileTypeError(ExternalAnalyzerFailedError):
    """Thrown when the analysed file has the wrong format (e.g. not a .NET assembly)"""
    pass

class ExternalAnalyserAdapter(object):
    def __init__(self, analyserExe):
        self.logger = logging.getLogger(self.__class__.__module__)
        self.pathToAnalyserExe = analyserExe
    def analyse_dll(self, dllFile):
        print dllFile
        prog = subprocess.Popen([self.pathToAnalyserExe, dllFile],stdout=subprocess.PIPE)
        xmlResult = prog.communicate()[0]
        if prog.returncode != 0:
            if prog.returncode == -2:
                raise WrongFileTypeError(xmlResult)
            else:
                raise ExternalAnalyzerFailedError(xmlResult) 
        return xmlResult
        
class InterfaceDependencyExtractor(object):
    # TODO (low prio) according to the design guidelines, it should be preferred to return generators etc. instead of lists. never return mutable lists 
    
    # TODO change logging.* to self.__logger.*
    def __init__(self, analyserAdapter):
        self.__analyserAdapter = analyserAdapter
    def __convert_to_type_info(self, jsonData):
        return TypeInformation(jsonData['TypeName'], jsonData['DefinedInAssembly'])
    def left_right_compare(self, rightSideDlls, leftSideDlls=None):
        # TODO rename "left_right_compare", "rightSideDlls" and "leftSideDlls" to more meaningful names and
        # add a documentation comment
        types = {}
        
        if leftSideDlls is None:
            #Analyse all interface deps to all targets
            types = collections.defaultdict(lambda: set())
        else:
            #Initialize every class with 0
            for dll in leftSideDlls:
                result = self.analyse_exported_classes(dll)
                for cls in result:
                    types[cls] = set()
    
        for dll in rightSideDlls:
            try:
                result = self.analyse_interface_dependencies(dll)
            except WrongFileTypeError:
                logging.warn("Skipped DLL %s" % dll)
                continue
            for (cls,deps) in result:
                for dep in deps:
                    if dep in types or leftSideDlls is None:
                        types[dep].add(cls)
        return types.items()
            
    def analyse_exported_classes(self, filename):
        """	Returns a list of all types that are exported by a assembly	"""
        logging.info("Analyzing dll '{0}'".format(filename))
        output = self.__analyserAdapter.analyse_dll(filename)
        jsonData = json.loads(output)
        
        assemblyName = jsonData['Name']
        classList = jsonData['Classes']
        classList = filter(lambda x: x['IsExported'], classList)
        classList = [TypeInformation(x['Name'], assemblyName) for x in classList]
        return classList
    
    def analyse_interface_dependencies(self, filename):
        """ Returns a list of tuples with the format (name of class, [list of interface dependencies]) """
        output = self.__analyserAdapter.analyse_dll(filename)
        jsonData = json.loads(output)

        classList = jsonData['Classes']
        
        classList = filter(lambda x: x['IsExported'], classList)
        
        result = []
        for cls in classList:
            interfaceTypes = set()
            for m in cls['Methods']:
                if m['IsVisible']:
                    interfaceTypes.add(self.__convert_to_type_info(m['ReturnType']))
                    interfaceTypes.update([self.__convert_to_type_info(t['Type']) for t in m['Parameters']])
            for f in cls['Fields']:
                if f['IsVisible']:
                    interfaceTypes.add(self.__convert_to_type_info(f['Type']))
            result.append((cls['Name'],interfaceTypes))
        return result
