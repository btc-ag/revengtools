'''
Created on 18.02.2012

@author: SIGIESEC
'''
from commons.config_if import FactoryRequired
from commons.core_util import SetValuedDictTools, isinstance_or_duck
from commons.os_util import PathCanonicalizer, FileResource, PathTools
from commons.resource_if import (ResourceUnresolvable, IllegalResourceIdentifierError)
from cpp.incl_deps.include_list_generator import PreprocessorConstants
from cpp.incl_deps.include_resolver_if import (IIncludePathCanonicalizer, 
    IncludeSpecificationTypes, IIncludePathCanonicalizerFactory)
from itertools import imap, chain, islice
import logging
import os

class DefaultIncludePathCanonicalizer(IIncludePathCanonicalizer):
    # TODO It must be possible to ignore subtrees, which must be considered during canonic path calculation.
    
    def __init__(self, quoted_include_paths, angle_include_paths, path_module=os.path,
                 canonic_quoted_include_paths=None,
                 canonic_angle_include_paths=None):
        """
        
        Angle include paths take precedence over quoted include paths. Therefore, it is not possible to
        use quoted includes for a directory tree, and angle includes for a subtree of that.
        You can implement a decorator, which checks for such cases first.  
        
        @param quoted_include_paths: The base paths to use for quoted include specifications.
        @param angle_include_paths: The base paths to use for angle include specifications. 
        @param path_module: An object behaving like os.path, defaults to posixpath
        @param canonic_quoted_include_paths: The list of canonic base paths to use for quoted includes. 
          If None, the default is to use the most paths closest to the root among the quoted_included_paths. 
          In many cases, this may not be what is desired, because this typically includes paths too close to the root,
          e.g. the top-level path of the local repository.
        @param canonic_angle_include_paths: Same as canonic_quoted_include_paths for angle includes.
        """
        if not canonic_quoted_include_paths:
            self.__canonic_quoted_include_paths = PathCanonicalizer.default_canonic_path_list(quoted_include_paths, path_module=path_module)
        else:
            self.__canonic_quoted_include_paths = canonic_quoted_include_paths
        if not canonic_angle_include_paths:
            self.__canonic_angle_include_paths = PathCanonicalizer.default_canonic_path_list(angle_include_paths, path_module=path_module)
        else:
            self.__canonic_angle_include_paths = canonic_angle_include_paths
        self.__quoted_include_paths_canonicalizer = PathCanonicalizer(input_path_list=quoted_include_paths,                                                                       
                                                                      canonic_path_list=self.__canonic_quoted_include_paths, 
                                                                      path_module=path_module)
        self.__angle_include_paths_canonicalizer = PathCanonicalizer(input_path_list=angle_include_paths, 
                                                                      canonic_path_list=self.__canonic_angle_include_paths, 
                                                                      path_module=path_module)
        
    def get_canonic_paths(self, include_specification_types):
        result = set()
        for include_specification_type in include_specification_types:
            if include_specification_type == IncludeSpecificationTypes.QUOTED:
                result.update(self.__canonic_quoted_include_paths)
            if include_specification_type == IncludeSpecificationTypes.ANGLE:
                result.update(self.__canonic_angle_include_paths)
        return PathCanonicalizer.default_canonic_path_list(result)
        
    def canonicalize(self, included_file, try_first=()):
        """
        @rtype: tuple(IncludeSpecificationType, Resource)
        """
        try:
            for candidate in try_first:
                try:
                    return (IncludeSpecificationTypes.ANGLE, self.__angle_include_paths_canonicalizer.canonical_resource_for_path(candidate))
                except ResourceUnresolvable:
                    pass
                except IllegalResourceIdentifierError:
                    # This happens when the resource is not located within the specified directory trees.
                    pass
            return (IncludeSpecificationTypes.ANGLE, self.__angle_include_paths_canonicalizer.canonical_resource_for_path(included_file))
        except ResourceUnresolvable:
            return (IncludeSpecificationTypes.QUOTED, self.__quoted_include_paths_canonicalizer.canonical_resource_for_path(included_file))
        
class DefaultIncludePathCanonicalizerFactory(IIncludePathCanonicalizerFactory, FactoryRequired):
    MODULE_INTERNAL_INCLUDE_PATHS=0
    MODULE_EXTERNAL_INCLUDE_PATHS=1
    
    # TODO if one wished to include module-internal include directives differently, this would need to be extended
    
    def __init__(self, 
                 global_internal_include_paths, 
                 global_external_include_paths, 
                 module_include_paths_func=lambda module_name: ([], []),
                 quoted_internal_include_paths=False,
                 path_module=os.path):
        self.__global_internal_include_paths = list(global_internal_include_paths)
        self.__global_external_include_paths = list(global_external_include_paths)
        self.__module_include_paths_func = module_include_paths_func
        self.__quoted_internal_include_paths = quoted_internal_include_paths
        assert all(imap(path_module.isabs, global_external_include_paths))
        assert all(imap(path_module.isabs, global_internal_include_paths))
        self.__path_module = path_module
        self.__logger = logging.getLogger(self.__class__.__module__)
        
    def __get_module(self, project_file):
        try:
            module = project_file.get_module()
            if module:
                return module
        except:
            pass
        # TODO lookup module
        return None
    
    def get_include_path_canonicalizer(self, implementation_file, current_resource):
        assert isinstance(current_resource, FileResource)
        current_resource_dir = self.__path_module.dirname(self.__path_module.normpath(current_resource.name()))
        quoted_include_paths = [current_resource_dir]
        
        angle_include_paths = []
        module_include_paths = self.__module_include_paths_func(self.__get_module(implementation_file))
        internal_include_paths = chain(module_include_paths[self.MODULE_INTERNAL_INCLUDE_PATHS], 
                                       self.__global_internal_include_paths)
        
        if self.__quoted_internal_include_paths:
            quoted_include_paths.extend(internal_include_paths)
        else:
            angle_include_paths.extend(internal_include_paths)
            
        angle_include_paths.extend(module_include_paths[self.MODULE_EXTERNAL_INCLUDE_PATHS])
        angle_include_paths.extend(self.__global_external_include_paths)
        
        # TODO this is not totally clean, assumes CAB-specific setup
        if current_resource_dir.endswith(self.__path_module.sep + "src"):
            current_resource_pardir = self.__path_module.normpath(self.__path_module.join(current_resource_dir, self.__path_module.pardir))
            self.__logger.info("Using CAB workaround: adding include path %s for %s" % (current_resource_pardir, current_resource)) 
            angle_include_paths.append(current_resource_pardir)        
        
        angle_include_paths = map(self.__path_module.normpath, angle_include_paths)
        quoted_include_paths = map(self.__path_module.normpath, quoted_include_paths)
        
        self.__logger.debug("Creating include path canonicalizer for implementation file %s and resource %s with quoted include paths %s and angle include paths %s"
                            % (implementation_file, current_resource, quoted_include_paths, angle_include_paths))
        return DefaultIncludePathCanonicalizer(quoted_include_paths=quoted_include_paths,
                                               angle_include_paths=angle_include_paths,
                                               path_module=self.__path_module)
    
            


class IncludeResolver(object):
    def __init__(self, repair_path, include_path_canonicalizer, fuzzy_resolver_func=lambda x: None):
        self.__repair_path = repair_path
        self.__include_path_canonicalizer = include_path_canonicalizer
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__count_resolvable = dict({IncludeSpecificationTypes.ANGLE:0 , IncludeSpecificationTypes.QUOTED :0})
        self.__count_unresolvable = 0
        self.__count_fuzzy = 0
        self.__fuzzy_resolver_func = fuzzy_resolver_func

    def get_statistics_dict(self):
        return dict({"Total include specifications processed": self.__count_resolvable[IncludeSpecificationTypes.ANGLE]
                     + self.__count_resolvable[IncludeSpecificationTypes.QUOTED] + self.__count_unresolvable,
                     "Include specifications that could not be resolved exactly": self.__count_unresolvable,
                     "Include specifications that could be matched fuzzily": self.__count_fuzzy,
                     "Quoted include specifications": self.__count_resolvable[IncludeSpecificationTypes.QUOTED],
                     "Angle bracket include specifications": self.__count_resolvable[IncludeSpecificationTypes.ANGLE]}
                    )
    
    def resolve_include_specification(self, included_file, try_first):
        """
        @rtype: tuple(IncludeSpecificationType, Resource)
        """
        try:
            (include_specification_type, canonical_resource) = self.__include_path_canonicalizer.canonicalize(included_file, try_first)
            self.__count_resolvable[include_specification_type] += 1
            return (include_specification_type, canonical_resource)
        except ResourceUnresolvable:
            self.__logger.warning("Include file %s in file %s cannot be resolved exactly" % (included_file, self.__repair_path))
            self.__logger.debug("Cause", exc_info=1)
            self.__count_unresolvable += 1
            fuzzy_result = self.__fuzzy_resolver_func(included_file)
            if fuzzy_result:
                self.__count_fuzzy += 1
                return fuzzy_result
            else:
                return (IncludeSpecificationTypes.ANGLE, FileResource(path=PathTools.unix_normpath(included_file)))
        
#        try:
#            included_file_resolved = self.__local_include_resource_resolver.resolve(included_file)
#            self.__logger.info("File %s includes %s" % (self.__repair_path, included_file_resolved.name()))
#            include_specification = '"%s"' % (PathTools.native_to_posix(included_file_resolved.name()), )
#        except ResourceUnresolvable:
#            if self.__std_include_resource_resolver:
#                try:
#                    included_file_resolved = self.__std_include_resource_resolver.resolve(included_file)
#                    include_specification = '<%s>' % (PathTools.native_to_posix(included_file_resolved.name()), )
#                except ResourceUnresolvable:
#                    self.__logger.warning("Include file %s in file %s cannot be resolved" % (included_file, self.__repair_path), exc_info=1)
#                    include_specification = '"%s"' % (PathTools.unix_normpath(included_file), )
#            else:
#                self.__logger.warning("Include file %s in file %s cannot be resolved, and no standard include resource resolver specified, so assuming a standard include file" % (included_file, self.__repair_path), exc_info=1)
#                include_specification = '<%s>' % (PathTools.unix_normpath(included_file), )
#        return include_specification

class FileMapFactory(object):
    def __init__(self, filelists):
        self.__filelists = filelists
        self.__filemaps = dict()
    
    def get_filemap(self, paths):
        path_set = frozenset(paths)
        if path_set not in self.__filemaps:
            self.__filemaps[path_set] = self.__create_filemap(path_set)
        return self.__filemaps[path_set]
    
    def __create_filemap(self, paths):
        items = chain.from_iterable(((os.path.basename(filename), filename) 
                                     for filename in self.__filelists.get_filelist(basepath)) 
                                    for basepath in paths)
        return SetValuedDictTools.convert_from_itemiterator(items)
    

class FuzzyResolverInternal(object):
    """
    If match_partially_unique should be true, also match_nonexact_if_unique has to be true.
    """
    def __init__(self, filemap, match_nonexact_if_unique=True, match_partially_unique=True, path_module=os.path):
        """
        @param: A file map, which maps base names to a collection of paths with that basename.
        """
        self.__filemap = filemap
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__path_module = path_module
        self.__match_nonexact_if_unique = match_nonexact_if_unique
        self.__match_partially_unique = match_partially_unique
        

    def __match_parts(self, basename, parts):
        search_for = self.__path_module.join(*parts)
        result = filter(lambda resource:resource.endswith(search_for), self.__filemap[basename])
        return result

    def get_matches(self, path):
        """
        
        @param path: a normalized path
        """
        basename = self.__path_module.basename(path)
        if basename in self.__filemap:
            candidates = self.__filemap[basename]
            if self.__match_nonexact_if_unique and len(candidates) == 1:
                return candidates
            
            # TODO: normalizing might be skipped
            normpath = self.__path_module.normpath(path)
            parts = list(x for x in normpath.split(self.__path_module.sep) if x != self.__path_module.pardir)
            result = self.__match_parts(basename, parts)
            if len(result):
                return result
            elif self.__match_partially_unique:
                for start in range(len(parts)-1, 0, -1):
                    result = self.__match_parts(basename, parts[start:])
                    if len(result) == 1:
                        self.__logger.info("Partial fuzzy match for %s: %s (candidates=%s)" % (path, result[0], candidates))
                        return result
                return candidates
            elif len(candidates) > 1:
                return candidates
        return ()

class FuzzyResolver(object):
    
    def __init__(self, include_path_canonicalizer, filemap_factory_func):
        """
        
        @param include_path_canonicalizer:
        @type include_path_canonicalizer: IIncludePathCanonicalizer
        @param filemap_factory_func: a function which returns a filemap for a given set of canonic paths,
            such as FileMapFactory.get_filemap
        """
        assert isinstance_or_duck(include_path_canonicalizer, IIncludePathCanonicalizer)
        self.__include_path_canonicalizer = include_path_canonicalizer
        filemap = filemap_factory_func(self.__include_path_canonicalizer.get_canonic_paths((IncludeSpecificationTypes.ANGLE, IncludeSpecificationTypes.QUOTED)))
        self.__logger = logging.getLogger(self.__class__.__module__)
        if self.__logger.isEnabledFor(logging.DEBUG):
            self.__logger.debug("using filemap with %i keys (first entries: %s)" % (len(filemap.keys()), list(islice(filemap.iteritems(), 10))))
        self.__fuzzy_resolver_internal = FuzzyResolverInternal(filemap)
           
    def get_fullpath(self, include_path):
        candidates = self.__fuzzy_resolver_internal.get_matches(include_path)
        if len(candidates):
            # TODO the full list of candidates should be returned, the caller should decide what to do           
            if len(candidates) > 1:
                # TODO allow the following: try to resolve using project-internal include paths only
                self.__logger.warning("Fuzzy match for %s returned multiple candidates %s, ignoring" % (include_path, candidates))
                return None
            else:                
                result = next(iter(candidates))
                result_specification = self.__include_path_canonicalizer.canonicalize(result)
                self.__logger.info("Unique fuzzy match for %s: %s (spec = %s)" % (include_path, result, result_specification))
                return result_specification
        else:
            self.__logger.info("No fuzzy match for %s" % include_path)
            return None

class IDNValueError(ValueError):
    pass

class IncludeDirectiveNormalizer(object):
    # TODO make it configurable whether to use <> oder "" for in-repository headers
    # TODO also check whether an include can be uniquely resolved
    
    def __init__(self, repair_project_file, include_canonicalizer_factory, filemap_factory_func=None):
        """
        
        @param repair_path:
        @param include_canonicalizer_factory:
        @type include_canonicalizer_factory: cpp.incl_deps.repair_includes_if.IIncludePathCanonicalizerFactory
        """
        self.__repair_path = repair_project_file.get_path_rel_to_root_unix()
        self.__repair_project_file = repair_project_file
        # TODO currently, the implementation file is always set to None!
        include_path_canonicalizer = include_canonicalizer_factory.get_include_path_canonicalizer(None, repair_project_file.get_resource())
        #include_path_canonicalizer.get()
        self.__include_resolver = IncludeResolver(repair_project_file.get_path_rel_to_root_unix(), 
                                                  include_path_canonicalizer=include_path_canonicalizer,
                                                  fuzzy_resolver_func=FuzzyResolver(include_path_canonicalizer, filemap_factory_func).get_fullpath 
                                                    if filemap_factory_func else lambda x: None)
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__count_unparsable = 0
        self.__count_exception = 0
        self.__count_total = 0
        self.__included_files = list()
    
    def __get_template(self, include_specification_type):
        if include_specification_type == IncludeSpecificationTypes.ANGLE:
            return "<%s>"
        elif include_specification_type == IncludeSpecificationTypes.QUOTED:
            return '"%s"'
        else:
            raise ValueError("Unknown include specification type %s" % include_specification_type)
        

    def __get_include_specification_for_include_directive_line(self, line):
        parts = PreprocessorConstants.INCLUDE_DIRECTIVE_REGEX.split(line)
        if len(parts) != 2:
            msg = "Unprocessable line in file %s: %s" % (self.__repair_path, line)
            self.__logger.warning(msg)
            raise IDNValueError(msg)
        raw_include_specification = parts[1].strip()
        match_quoted = PreprocessorConstants.REGEX_INCLUDE_SPECIFICATION_QUOTED.match(raw_include_specification)
        if match_quoted and len(match_quoted.groups()) == 1:
            included_file = match_quoted.group(1)
            match_type = IncludeSpecificationTypes.QUOTED
        else:
            match_angle = PreprocessorConstants.REGEX_INCLUDE_SPECIFICATION_ANGLE.match(raw_include_specification)
            if match_angle and len(match_angle.groups()) == 1:
                included_file = match_angle.group(1)
                match_type = IncludeSpecificationTypes.ANGLE
            else:
                msg = "Ignoring unparsable line in file %s: %s" % (self.__repair_path, line)
                self.__logger.warning(msg)
                self.__count_unparsable += 1
                raise IDNValueError(msg)
    #included_file = PathTools.unix_normpath(included_file)
        return self.__include_resolver.resolve_include_specification(PathTools.native_to_posix(included_file), try_first=
            (os.path.normpath(os.path.join(self.__repair_project_file.get_resource().name(), os.path.pardir, included_file)), ) if match_type == IncludeSpecificationTypes.QUOTED else ())

    def __normalize_include_line(self, line):
        try:
            (include_specification_type, canonical_resource) = self.__get_include_specification_for_include_directive_line(line)
            parts = PreprocessorConstants.INCLUDE_DIRECTIVE_REGEX.split(line)
            canonical_path = PathTools.unix_normpath(PathTools.resource_to_relpath(canonical_resource))
            include_specification = self.__get_template(include_specification_type) % (canonical_path)
            # TODO restrict this to internal files 
            self.__included_files.append(canonical_path)
            return "%s%s %s\n" % (parts[0], PreprocessorConstants.INCLUDE_DIRECTIVE, include_specification)
        except IDNValueError:
            return line
    
    @staticmethod
    def has_line_include_directive(line):        
        return PreprocessorConstants.INCLUDE_DIRECTIVE_REGEX.search(line)

    def get_include_specification(self, line):
        try:
            if self.has_line_include_directive(line):
                self.__logger.debug("Line has include directive: %s" % line)
                return self.__get_include_specification_for_include_directive_line(line)
            else:
                self.__logger.debug("Line has no include directive: %s" % line)
                return None
        except IDNValueError:
            self.__logger.debug("Ignored line %s" % line, exc_info=1)
            return None
    
    def normalize(self, line):
        # TODO: include line number information!
        if self.has_line_include_directive(line):
            try:
                self.__count_total += 1
                # TODO: check if comment and optionally ignore
                return self.__normalize_include_line(line)
            except:
                self.__logger.warning("Ignoring unprocessable line in file %s: %s (exception raised)" % (self.__repair_path, line), exc_info=1)
                self.__count_exception += 1
                return line
        else:
            return line
        
    def get_statistics_dict(self):
        result = self.__include_resolver.get_statistics_dict()
        result.update({"Total #include lines": self.__count_total,
                       "Unparsable lines": self.__count_unparsable,
                       "Unprocessable lines (internal error)": self.__count_exception})
        return result

    
    def get_included_files(self):
        return iter(self.__included_files)
    
    
    
    
