'''
Created on 01.04.2011

@author: SIGIESEC
'''
import logging
import re
import sys
import ntpath
import posixpath

class InternalSolutionFileParser(object):
    """
    A parser for Visual Studio 2008 Solution files (.SLN). It parses the dependencies between native
    C++ projects only. For C# projects, the dependencies are not contained in the solution file.    
    """
    
    def __init__(self, solution_file):
        """
        Creates an instance 
        
        @param solution_file: An iterator of lines of a VS2008 solution file, typically 
            a .SLN file opened for reading.
        """
        self.__vcprojs = []
        self.__project_ids_to_name = dict()
        self.__project_dependencies = dict()
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__parse(solution_file)
        
    def __parse(self, solution_file):
        in_deps = 0
        current_project_id = None
        for line in solution_file:
            line = line.strip()
            if line.startswith("Project("):
                #print("starts with Project(")
                m = re.match(r"Project\(\"{[-A-F0-9]*}\"\) = \"([A-Za-z0-9_.]*)\", \"([^\"].*)\", \"{([-A-F0-9]*)}\"", line)
                if m != None:
                    current_project_name = m.group(1)
                    current_project_vcproj = m.group(2)
                    current_project_id = m.group(3)
                    if current_project_vcproj.endswith('proj'):
                        #self.__logger.debug("project %s with id %s" % (current_project_name, current_project_id))
                        self.__project_ids_to_name[current_project_id] = current_project_name
                        self.__project_dependencies[current_project_id] = set()
                        self.__vcprojs.append(current_project_vcproj.replace(ntpath.sep, posixpath.sep))
                else:
                    self.__logger.warning("unparsable line %s" % (line,))
            elif line.startswith("EndProject"):
                current_project_id = None
                in_deps = 0
            elif line.startswith("ProjectSection(ProjectDependencies)"):
                in_deps = 1
            elif line.startswith("EndProjectSection"):
                in_deps = 0
            elif in_deps:
                m = re.match(r"{([-A-F0-9]*)} = {[-A-F0-9]*}", line)
                if m != None:
                    depend_project_id = m.group(1)
                    self.__logger.debug("project %s depends on %s" % (current_project_id, 
                                                                      depend_project_id))
                    if current_project_id in self.__project_dependencies:
                        self.__project_dependencies[current_project_id].add(depend_project_id)
                else:
                    self.__logger.warning("unparsable line %s" % (line,))

    def vcprojs(self):
        return self.__vcprojs
    
    def project_ids_to_name(self):
        return self.__project_ids_to_name
    
    def project_id_dependencies(self):
        return self.__project_dependencies
        
    @staticmethod
    def __is_empty(iterator):
        try:
            iterator.next()
        except StopIteration:
            return True
        return False
    
    def get_dependencies_iter(self):
        ids_sorted_by_name = sorted(self.__project_ids_to_name.keys(), #
                                         lambda x,y: cmp(self.__project_ids_to_name[x], self.__project_ids_to_name[y]))
        self.__logger.debug("ids_sorted_by_name = %s", ids_sorted_by_name)
        for current_project_id in ids_sorted_by_name:
            current_project_name = self.__project_ids_to_name[current_project_id]
            self.__logger.debug("project_id = %s, project_name = %s", current_project_id, current_project_name)
            if len(self.__project_dependencies[current_project_id]) != 0:
                for depend_project_id in sorted(self.__project_dependencies[current_project_id]):
                    if depend_project_id in self.__project_ids_to_name:
                        yield (current_project_name,
                               self.__project_ids_to_name[depend_project_id])
                    else:
                        self.__logger.debug("No project with id %s (in project %s)" % (depend_project_id, current_project_name))
            else:
                self.__logger.debug("Project %s has no outgoing dependencies within the solution file." % (current_project_name))
                incoming_dependencies = (project_id for project_id in self.__project_dependencies if current_project_id in self.__project_dependencies[project_id])
                if self.__is_empty(incoming_dependencies):
                    self.__logger.info("Project %s has no dependencies within the solution file. It will not be shown in any further output." % (current_project_name))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        import doctest
        doctest.testmod()
    else:
        logging.basicConfig(level=logging.DEBUG)
        parser = InternalSolutionFileParser(open(sys.argv[1], "r"))
        for (source, target) in parser.get_dependencies_iter():
            print "%s,%s" % (source, target)
