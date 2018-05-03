'''
Created on 28.12.2011

@author: SIGIESEC
'''
from commons.core_util import SetValuedDictTools
from commons.os_util import PathTools
from cpp.incl_deps.include_rule_checker_if import UnknownPath
import logging

class IncludeRuleCheckerProcessor(object):
    UNKNOWN_PATH_PSEUDO_RULE_NAME="UnknownPath"
    
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def check_links(self, file_links, checkers):
        """
        
        @param file_links:
        @type file_links: iterable of tuples of minimum length 2, whose first two elements are two file paths denoting an include relationship
        @param checkers: 
        @type checkers: collection of IncludeRuleChecker instances
        
        @rtype: a 3-tuple containing 
            1. a dictionary mapping dependencies to a list of names of violating rules
            2. total count of input items
            3. a dictionary mapping names of violations rules to number of total violations 
        """
        illegal_links = list()
        total_count = 0
        
        rule_violations = dict()
        for checker in checkers:
            rule_violations[checker.get_rule_name()] = 0
        rule_violations[self.UNKNOWN_PATH_PSEUDO_RULE_NAME] = 0
        for line in file_links:
            if len(line) < 2:
                self.__logger.warning("Illegal input item %s" % line)
            else:
                (from_file, to_file) = line[0:2] 
                total_count += 1
                try:
                    for checker in checkers:
                        if not checker.is_legal_dependency(from_file, to_file):
                            rule_name = checker.get_rule_name()
                            illegal_links.append(((from_file, to_file), rule_name))
                            rule_violations[rule_name] += 1
                except UnknownPath:                
                    illegal_links.append(((from_file, to_file), self.UNKNOWN_PATH_PSEUDO_RULE_NAME))
                    rule_violations[self.UNKNOWN_PATH_PSEUDO_RULE_NAME] += 1
        return SetValuedDictTools.convert_from_itemiterator(illegal_links), total_count, rule_violations

class IncludeRuleCheckerOutputter(object):
    def output(self, output_file, illegal_links, total_count, rule_violations):
        print >>output_file, "Illegal include links:"
        for (from_file, to_file), violations in sorted(illegal_links.iteritems()):
            print >>output_file, "%s -> %s (%s)" % (PathTools.unix_normpath(from_file), PathTools.unix_normpath(to_file), ", ".join(violations))
        
        print >>output_file, ("%i total links, %i illegal links" % 
              (total_count, len(illegal_links)))
        
        if len(illegal_links):
            print >>output_file, "Violations by rule:",
            print >>output_file, ", ".join("%s=%i" % (name,count) for name, count in rule_violations.iteritems())
