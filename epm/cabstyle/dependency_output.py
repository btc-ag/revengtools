'''
Created on 16.06.2011

@author: SIGIESEC
'''
from base.dependency.dependency_base import BaseSuffixModuleGrouper
from base.dependency.dependency_if import ModuleGrouper
from base.modules_if import ModuleListSupply
from commons.core_util import HierarchicalDecomposer, IterTools,\
    AdaptiveReplacementCache
from itertools import ifilter, imap

config_module_list_supply = ModuleListSupply()

class CABStyleFinestLevelModuleGrouperInternal(ModuleGrouper):    
    DELIMITER = "."
    #TODO: variable cache size
    UPPERCOUNT_CACHE_SIZE=5000
    GET_ALL_INTERNAL_MODULES_WITH_PREFIX_CACHE_SIZE=5000

    def __init__(self, modules, internal_modules, min_parts = 1):
        self.__node_prefixes = None
        self.__internal_modules = set(internal_modules)
        self.__min_parts = min_parts
        # Use a cache for calls to uppercount and get_all_internal_modules_with_prefix, since Christian identified this to be time-consuming by profiling
        self.__uppercount_cache = AdaptiveReplacementCache(self.UPPERCOUNT_CACHE_SIZE)(self.uppercount)
        self.__get_all_internal_modules_with_prefix_cache = AdaptiveReplacementCache(self.GET_ALL_INTERNAL_MODULES_WITH_PREFIX_CACHE_SIZE)(self.__get_all_internal_modules_with_prefix)
        if modules:
            self.configure_nodes(modules)

    def configure_nodes(self, nodes):
        node_set = set(nodes) if nodes else ()
        #check precondition
        #if not self.__internal_modules.issubset(node_set):
        #    raise ValueError("%s instance is configured with internal_modules=%s, so cannot set ..." % (self.__class__, self.__internal_modules))
        #change
        self.__node_prefixes = set(ifilter(None, imap(self.get_node_group_prefix, node_set)))
        

    def __get_all_internal_modules_with_prefix(self, prefix):
        return tuple(ifilter(lambda x:x.lower().startswith(prefix.lower()), self.__internal_modules))
    
    def get_all_internal_modules_with_prefix(self, prefix):
        return self.__get_all_internal_modules_with_prefix_cache(prefix)
        
    @staticmethod
    def uppercount(in_str):
        return 0-IterTools.quantify(imap(lambda ch:ch.isupper(), in_str))
            
    def __fix_module_prefix(self, prefix):        
        prefix = sorted(imap(lambda module: module[:len(prefix)], self.get_all_internal_modules_with_prefix(prefix)), key=self.__uppercount_cache)[0]
        if prefix.lower().startswith("btc."):
            prefix = "BTC." + prefix[4:]
        return prefix


    def get_shortest_prefix_with_at_most_one_internal_module(self, parts):        
        for length in xrange(len(parts), 0, -1):
            if len(self.get_all_internal_modules_with_prefix(self.DELIMITER.join(parts[:length]) + self.DELIMITER)) > 1:
                return length + 1
        return 0
    
    
    def get_node_group_prefix(self, module):
        # TODO this is too complicated and shows symptoms of premature optimization. 
        # Perhaps it is better to create a hierarchical module group model and use this to derive a flat module group model, which
        # can be then either be fine-grained or coarse-grained.
        if module in self.__internal_modules:
            parts = module.split(self.DELIMITER)
            prefix_length = self.get_shortest_prefix_with_at_most_one_internal_module(parts)
            if prefix_length > self.__min_parts:            
                prefix = self.DELIMITER.join(parts[:prefix_length-1])
            else:
                prefix = self.DELIMITER.join(parts[:self.__min_parts])
            return self.__fix_module_prefix(prefix)
        
#            sub_modules = self.get_all_internal_modules_with_prefix(module + self.DELIMITER)
#            if len(sub_modules) > 0:
#                return self.__fix_module_prefix(module)
#            pos = module.rfind(self.DELIMITER)
#            if pos != -1:
#                sibling_modules = self.get_all_internal_modules_with_prefix(module[:pos] + self.DELIMITER)
#                if module[:pos] in self.__internal_modules and len(sibling_modules) == 0:
#                    pos = module[:pos].rfind(self.DELIMITER)
#                return self.__fix_module_prefix(self.get_node_group_prefix(module[:pos]))
#            else:
#                return self.__fix_module_prefix(module)
        
        return "EXTERNAL"

    def node_group_prefixes(self):
        return iter(self.__node_prefixes)
    

# TODO rename original class to ...Service
class CABStyleFinestLevelModuleGrouper(CABStyleFinestLevelModuleGrouperInternal):
    def __init__(self, modules=None):
        CABStyleFinestLevelModuleGrouperInternal.__init__(self, 
                                                          modules=modules,
                                                          internal_modules=config_module_list_supply.get_module_list(),
                                                          min_parts=3)

# TODO make this class testable and create ...Service instead of original class
class CABStyleTopLevelModuleGrouperBase(ModuleGrouper):
    DELIMITER = "."
    OWN_LEVEL = 3
    OWN_PREFIX="<NONE>"
    BTC_PREFIX="BTC."
    BTC_LEVEL = 2
    OTHER_LEVEL = 1
    ADDITIONAL_PREFIXES = ()
    
    def __init__(self, modules, internal_modules):
        self.__node_prefixes = None
        self.__decomposer = HierarchicalDecomposer(delimiter=self.DELIMITER)
        self.__internal_modules = set(internal_modules)
        if modules:
            self.configure_nodes(modules)
    
    def configure_nodes(self, nodes):
        self.__node_prefixes = set(ifilter(None, imap(self.get_node_group_prefix, nodes)))
    
    def get_node_group_prefix(self, module):
        for prefix in self.ADDITIONAL_PREFIXES:
            if module.startswith(prefix):
                return prefix
        if module.upper().startswith(self.OWN_PREFIX):
            prefix = self.__decomposer.limited_to(module, self.OWN_LEVEL)
        elif module.upper().startswith(self.BTC_PREFIX):
            prefix = self.__decomposer.limited_to(module, self.BTC_LEVEL)
        elif module.find(self.DELIMITER) != -1:
            prefix = self.__decomposer.limited_to(module, self.OTHER_LEVEL)
        elif module in self.__internal_modules:
            prefix = module
        else:
            prefix = "OTHER_EXTERNAL"
        if len(prefix):
            return prefix
        else:
            return None
    
    def node_group_prefixes(self):
        return iter(self.__node_prefixes)

class CABStyleBaseSuffixModuleGrouperBase(BaseSuffixModuleGrouper):
    def get_node_group_prefix(self, module):
        if module in self.module_group_exceptions:
            return self.module_group_exceptions[module]
        else:
            return BaseSuffixModuleGrouper.get_node_group_prefix(self, module)

    def _determine_node_group_prefixes(self, nodes):
        #EPMDependencyFilterConfiguration.node_group_prefixes(self, modules)
        # TODO currently ignores nodes parameter...
        return sorted(self.defined_module_group_prefixes, key=lambda x:-len(x))
