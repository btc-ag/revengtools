'''
Created on 09.06.2011

@author: SIGIESEC

TODO this was copied from cpp.csharp.csproj_parser and has probably lots of duplication!
'''
from __future__ import with_statement
from base.basic_config_if import BasicConfig
from base.diagnostics_if import ModuleCheckerParameterKeys, CheckerParameterKeys, \
    DiagnosticResult, TechnologyTypes, DiagnosticSubjectTypeParameterKeys
from base.diagnostics_util import CheckerRuleFactory, CheckerRunner
from commons.config_if import AutoConfigurable, ConfigDependent
from commons.configurator import Configurator 
from commons.core_util import IterTools, frozendict, StringTools,\
    isinstance_or_duck
from commons.os_util import FixedBaseDirPathResolver, PathTools
from itertools import chain
from xml.dom.minidom import Text
from xml.parsers.expat import ExpatError
import logging
import ntpath
import os.path
import sys
import types
import xml.dom.minidom

class VSConstants(object):
    VCXPROJ_EXTENSION = ".vcxproj"
    SOURCE_EXTENSION = ".cpp"
    MSVC_EXTENSION = ".sln"
    NAMESPACE_URI="http://schemas.microsoft.com/developer/msbuild/2003"    

class ProjectReferenceProxy(object):
    def __init__(self, target_resource):
        self.__target_resource = target_resource
        
    def get_resource(self):
        return self.__target_resource
    
    def __str__(self):
        return "ProjectReferenceProxy(%s)" % (self.__target_resource, )

class ModuleResolver(object):
    def calc_resolved_modules(self, from_module, target_modules):
        raise NotImplementedError(self.__class__)

class VCXProjParserTools(object):
    __logger = logging.getLogger("cpp.msvc.vcxrpoj_parser")
    
    @classmethod
    def __get_relative_name(cls, absolute_name, project_dir_resolver):
        # TODO duplicates csproj_modules.CSharpModuleListSupply
        resource = project_dir_resolver.resolve(absolute_name)
        return os.path.relpath(resource.name(), resource.get_resolution_root())

    @classmethod
    def get_best_name(cls, vcxrpoj_parser, project_dir_resolver):
        try:
            return vcxrpoj_parser.get_assembly_name()
        except Exception:
            cls.__logger.warning(".VCXProj file %s does not declare an assembly name" % (vcxrpoj_parser.get_filename()), exc_info=1)
            #return "no_assembly_name<%s>" % (PathTools.native_to_posix(cls.__get_relative_name(vcxrpoj_parser.get_filename(), 
            #                                                                                     project_dir_resolver))) 
        names = list()
        try:
            (basename, _ext) = os.path.splitext(os.path.basename(vcxrpoj_parser.get_filename()))
            names.append(basename)
        except ValueError:
            pass
        try:
            names.append(vcxrpoj_parser.get_root_namespace())
        except ValueError:
            cls.__logger.info(".VCXProj file %s does not declare a root namespace" % (vcxrpoj_parser.get_filename()), exc_info=1)
        return sorted(names, key=lambda x: -len(x))[0]
        # allow to ensure that returned names are unique!

config_basic = BasicConfig()

class ModuleResolverBase(ModuleResolver):
    def __init__(self, add_unresolvable=True):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__add_unresolvable = add_unresolvable
        # TODO inject this
        self.__project_dir_resolver = config_basic.get_local_source_resolver()
    
    
    def _resolve_individual(self, target_module):
        try:
            with target_module.get_resource().open() as openresource:                
                vcxrpoj_parser = VCXProjParser(openresource)
                return VCXProjParserTools.get_best_name(vcxrpoj_parser, self.__project_dir_resolver)
        
        except Exception:
            self.__logger.debug("Exception while parsing %s" % (target_module.get_resource()), exc_info=1)
            return None

    def _resolve_target(self, target_module):
        raise NotImplementedError(self.__class__)
    
    def calc_resolved_modules(self, from_module, target_modules):
        new_tos = set()
        for to_module in target_modules:
            if isinstance(to_module, ProjectReferenceProxy):
                to_module_resolved = self._resolve_target(to_module)
                if to_module_resolved != None:
                    new_tos.add(to_module_resolved)
                else:
                    self.__logger.warning("Project reference %s->%s cannot be resolved", from_module, to_module)
                    #VCXProjCheckerDefault._add_irregularity(self, result)
                    if self.__add_unresolvable:
                        new_tos.add("unresolvable<%s>" % ntpath.basename(to_module.get_resource().name()))
            else:
                new_tos.add(to_module)
        
        return new_tos

class IndividualModuleResolver(ModuleResolverBase):
    def __init__(self):
        ModuleResolverBase.__init__(self)
        self.__logger = logging.getLogger(self.__class__.__module__)        
    
    def _resolve_target(self, target_module):
        return self._resolve_individual(target_module)

class SetModuleResolver(ModuleResolverBase):    
    def __init__(self, file_to_module_name_map):
        ModuleResolverBase.__init__(self)
        self.__file_to_module_name_map = file_to_module_name_map
        self.__logger = logging.getLogger(self.__class__.__module__)        

    def _resolve_fuzzy(self, to_module):
        file_basename = StringTools.strip_suffix(os.path.basename(to_module.get_resource().name()), 
                                                 VSConstants.VCXProj_EXTENSION, ignore_case=True)
        candidates = list(filename for (filename, modulename) in self.__file_to_module_name_map.iteritems()
                          if modulename == file_basename or os.path.basename(filename) == file_basename)
        candidates = sorted(candidates, key=lambda x: -len(self.__file_to_module_name_map[x]))
        if len(candidates):
            if len(candidates) > 1:
                self.__logger.warning("Could not resolve project reference to %s exactly, but multiple fuzzy matches could be found in %s, using %s" % (to_module.get_resource().name(), 
                                                                                                   ", ".join(candidates), candidates[0]))
            else:
                self.__logger.warning("Could not resolve project reference to %s exactly, but a fuzzy match could be found in %s" % (to_module.get_resource().name(), 
                                                                                                   candidates[0]))
            return self.__file_to_module_name_map[candidates[0]]
        return None
    
    def _resolve_target(self, to_module):        
        if to_module.get_resource().name() not in self.__file_to_module_name_map:
            result = self._resolve_individual(to_module)
            if result:
                self.__file_to_module_name_map[to_module.get_resource().name()] = result
            # TODO try best match if exact match is not found
            else:
                return self._resolve_fuzzy(to_module)                
            return result 
        return self.__file_to_module_name_map.get(to_module.get_resource().name(), None)

class ProjectReferenceParser(object):
    def __init__(self, path_resolver, basedir):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__path_resolver = path_resolver
        self.__basedir = basedir
        assert os.path.abspath(self.__basedir)
    
    def __parse_project_reference_name(self, pr_element):
        # TODO this is not very clean. the project reference proxy should use the resource, not its name...
        project_file_path = pr_element.getAttribute("Include")      
        if project_file_path:
            return ProjectReferenceProxy(self.__path_resolver.resolve(project_file_path))
        else:
            logging.warning("No 'Include' attribute on 'ProjectReference' element: %s" % (pr_element, ))
            return None
    
    
    def get_project_references(self, dom):
        for pr_element in dom.getElementsByTagNameNS(VSConstants.NAMESPACE_URI, "ProjectReference"):
            reference = self.__parse_project_reference_name(pr_element)
            if reference:
                yield reference

class VCXProjParser(object):
    
    def __init__(self, file_or_filename, path_resolver=None):
        self.__logger = logging.getLogger(self.__class__.__module__)
        if isinstance(file_or_filename, basestring):
            self.__filename = file_or_filename
        elif isinstance(file_or_filename, types.FileType):
            self.__filename = file_or_filename.name
        else:
            self.__filename = None
        self.__absdir = os.path.abspath(os.path.dirname(self.__filename))
        if path_resolver:
            self.__path_resolver = path_resolver
        elif self.__filename:
            self.__path_resolver = FixedBaseDirPathResolver(os.path.dirname(self.__filename), normalize=True)
        else:
            self.__path_resolver = None
        self.__dom = xml.dom.minidom.parse(file_or_filename)
        
    def get_filename(self):
        return self.__filename
    
    def get_project_references(self):        
        return ProjectReferenceParser(self.__path_resolver, self.__absdir).get_project_references(self.__dom)
    
    def get_assembly_references(self):
        for element in self.__dom.getElementsByTagNameNS(VSConstants.NAMESPACE_URI, "Reference"):
            referenced_assembly_spec = element.getAttribute("Include")
            yield referenced_assembly_spec.split(",")[0]
    
    def get_all_references(self):
        return chain(self.get_project_references(), self.get_assembly_references())    

    def get_assembly_name(self):
        elements = self.__dom.getElementsByTagNameNS(VSConstants.NAMESPACE_URI, "TargetName")
        if len(elements) == 1:
            name_text = elements[0].firstChild
            if isinstance(name_text, Text) and name_text.data:
                return name_text.data

        basename = os.path.basename(self.get_filename()).strip(VSConstants.VCXPROJ_EXTENSION)
        self.__logger.warning("%s: %i AssemblyNames found: %s; using file basename %s" % (self.get_filename(), len(elements), elements, basename))
        return basename
    
    def get_root_namespace(self):
        elements = self.__dom.getElementsByTagNameNS(VSConstants.NAMESPACE_URI, "RootNamespace")
        if len(elements) == 1:
            name_text = elements[0].firstChild
            if name_text == None:
                return ""
            elif isinstance(name_text, Text):
                return name_text.data
            else:
                raise ValueError("%s: %s is not a Text node" % (self.get_filename(), name_text))
        raise ValueError("%s: %i RootNamespaces found" % (self.get_filename(), len(elements)))
            
    def get_source_files(self):
        if not self.__path_resolver:
            raise RuntimeError("No path resolver set")
        elements = self.__dom.getElementsByTagNameNS(VSConstants.NAMESPACE_URI, "ClCompile")
        for element in elements:
            filename = element.getAttribute("Include")
            if filename:
                yield self.__path_resolver.resolve(PathTools.windows_to_native(filename))
            
class VCXProjChecker(AutoConfigurable):        

    def get_checked_rules(self):
        raise NotImplementedError(self.__class__)
    
    def has_errors(self):
        raise NotImplementedError(self.__class__)
    
    def get_irregularities(self):
        raise NotImplementedError(self.__class__)  
    
class VCXProjProcessor(ConfigDependent):
    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def parse_file(self, filename):
        try:
            parser = VCXProjParser(open(filename))
            from_proj = parser.get_assembly_name()
            to_proj = None
            for to_proj in IndividualModuleResolver().calc_resolved_modules(from_proj, parser.get_project_references()):
                print "%s,%s,PR" % (from_proj, to_proj)
            for to_proj in parser.get_assembly_references():
                print "%s,%s,AR" % (from_proj, to_proj)
            if to_proj == None:                        
                print "%s,None,None" % (from_proj)
                self.__logger.info("Assembly %s has no references (project file %s)" % (from_proj, filename))
                    
            print list(parser.get_source_files())
        except ExpatError, exc:
            self.__logger.error("Unparsable file %s: %s" % (filename, exc))
            
    def parse_files(self, filenames):
        for filename in filenames:
            self.parse_file(filename)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    configurator = Configurator()
    configurator.default()
    vcxproj_processor = configurator.create_instance(VCXProjProcessor)
    if len(sys.argv) > 1:
        logging.info("Processing %i files to process specified as cmdline arguments" % (len(sys.argv)-1))
        vcxproj_processor.parse_files(sys.argv[1:])
    else:
        logging.info("Reading list of files to process from stdin")
        vcxproj_processor.parse_files(x.strip() for x in sys.stdin)
