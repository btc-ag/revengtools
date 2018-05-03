from base.dependency.interface.interface_dependency_extraction import (
    InterfaceDependencyExtractor, ExternalAnalyserAdapter)
from infrastructure.ctags.ctags_class_mapper import CTagClassMapper, MapperError, CTagLanguage
from infrastructure.scms.svn.change_freq_analyse import SVNFreqAnalyser
import collections
import logging
import os
import time

ChangeInterfaceAnaysisResult = collections.namedtuple("ChangeInterfaceAnaysisResult", ["Name", "Filename", "IDeps", "Changes"])

class SVNAndInterfaceDepAnalyzer:
    def __init__(self):
        self.mapper = CTagClassMapper("external/ctags/ctags.exe", CTagLanguage.CSharp)
        module_dir = os.path.dirname(__file__) or '.'
        self.depAnalyser = InterfaceDependencyExtractor(ExternalAnalyserAdapter(os.path.join(module_dir, "external/BTC.Arch.CSharpAnalyzer/BTC.Arch.Modularity.App.exe")))
    
    def lookupClasses(self, depList):
        res = []
        for (className,count) in depList:
            try:
                files = self.mapper.lookup_class(className.TypeName)
                res.append((className.TypeName,files, count))
            except MapperError:
                res.append((className.TypeName,None, count))
                logging.error("Can't lookup class %s", className.TypeName)

        return res
    
    def __get_filename_for_type(self, typename):
        try:
            return self.mapper.lookup_class(typename)
        except MapperError:
            logging.error("Can't lookup class %s", typename)
            return None

    def interface_dependency_analyse(self, leftSideSourceFiles, leftSideDllFiles, rightSideDllFiles, startDate, endDate):
        logging.info("Creating Class -> File index")
        self.mapper.create_index(leftSideSourceFiles)
        
        logging.info("Analyzing types in dlls and count interface deps")
        depList = self.depAnalyser.left_right_compare(rightSideDllFiles, leftSideDllFiles)

        svnAnalyser = SVNFreqAnalyser()
        start = time.mktime(startDate.timetuple())
        end = time.mktime(endDate.timetuple())
        logging.info("Analyzing change frequency of files in the SVN")
        #TODO: Fall leftSideSourceFiles = [] besser behandeln
        fileListWithChanges = []
        if leftSideSourceFiles:
            fileListWithChanges = svnAnalyser.getChangeCountOfFileList(leftSideSourceFiles, start, end)

        logging.info("Build result")
        result = []
        for item in depList:
            #Lookup Class
            sourceFiles = self.__get_filename_for_type(item[0].TypeName)
            
            #Lookup Changes
            changes = None
            if sourceFiles is not None:
                changes = sum(fileListWithChanges[os.path.normpath(filename)] for filename in sourceFiles)
            result.append(ChangeInterfaceAnaysisResult(item[0].TypeName, sourceFiles, item[1],changes))
        return result
