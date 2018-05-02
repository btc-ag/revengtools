import optparse
import time
import os.path
import logging
import sys

from change_interface_dep_analysis import SVNAndInterfaceDepAnalyzer

def parseFileList(fileName):
    f = open(fileName,"r")
    res = []
    for line in f.readlines():
        #Check if line is empty
        line = line.rstrip("\n")
        if line:
            res.append(line)
    return res
        
parser = optparse.OptionParser(usage = "usage: %prog [options] <FileWithSources> <FileWithLeftDlls> <FileWithRightDlls>")
(options,args) = parser.parse_args()

logging.basicConfig(format="", level=logging.INFO)

if len(args) != 3:
    parser.error("Missing parameters!")

leftSideSourceFiles = parseFileList(args[0])
leftSideDllFiles = parseFileList(args[1])
rightSideDllFiles = parseFileList(args[2])

interval = 120 #days
logging.info("Using default interval %s", interval)

analyzer = SVNAndInterfaceDepAnalyzer()
depListWithFileNameAndChanges = analyzer.interface_dependency_analyse(leftSideSourceFiles, leftSideDllFiles, rightSideDllFiles, interval)

formatString = "{0:<100}{1:<10}{2:<10}"
print formatString.format("Class","IDeps","Changes")
for i in depListWithFileNameAndChanges:
    print formatString.format(i[0],i[2],i[3])