#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Extension functionality around the os and path modules (os.path, posixpath, ntpath).
Implements the commons.resource_if interface based on local files. 

Created on 21.05.2011

@author: SIGIESEC
'''
from __future__ import with_statement
from commons.core_if import ContentMetric
from commons.core_util import isinstance_or_duck, CollectionTools, StringTools
from commons.resource_if import (ResourceMetricProcessor, Resource, 
    ResourceAccessError, IllegalResourceIdentifierError, ResourceUnresolvable, 
    GenerationStrategy)
from commons.resource_util import ResourceUtil
from commons.v26compat_util import compatrelpath
from datetime import datetime
from itertools import imap, ifilter, permutations
import csv
import logging
import ntpath
import os.path
import posixpath
import re
import sys
import urllib
import urlparse
import warnings
import shelve

class AbsoluteFileMetricProcessor(ResourceMetricProcessor):
    """
    @deprecated: ResourceMetricProcessor is deprecated in the current form.
    """
    
    def apply_metric_to_resource(self, path):
        """
        Returns the number of apply_metric_to_resource contained in a file.
        
        @param abspath: a path, which must be absolute; result is undefined if not
        """
        raise NotImplementedError(self.__class__)

class LocalFileMetricProcessor(AbsoluteFileMetricProcessor):
    """
    @deprecated: ResourceMetricProcessor is deprecated in the current form.
    """

    def apply_metric_to_resource(self, path):
        """
        Returns the number of apply_metric_to_resource contained in a file.
        
        @param path: a path, evaluated relative to the current working directory
        """
        raise NotImplementedError(self.__class__)
    
class ResolvingResourceMetricProcessor(ResourceMetricProcessor):
    """
    @deprecated: ResourceMetricProcessor is deprecated in the current form.
    """
    def __init__(self, metric, resource_resolver):
        assert isinstance(metric, ContentMetric)
        assert isinstance(resource_resolver, ResourceResolver)
        self.__metric = metric
        self.__resource_resolver = resource_resolver
    
    def get_metric(self):
        return self.__metric
        
    def apply_metric_to_resource(self, path):
        return self.__metric.apply_metric(self.__resource_resolver.resolve(input_identifier=path).open())


class CachingResourceMetricProcessor(ResourceMetricProcessor):
    """
    @deprecated: ResourceMetricProcessor is deprecated in the current form.
    """
    def __init__(self, decoratee):
        assert isinstance(decoratee, ResourceMetricProcessor)
        self.__decoratee = decoratee
        self.__cache = dict()
        
    def get_metric(self):
        return self.__decoratee.get_metric()
        
    def get_cached_lengths_items(self):
        return self.__cache.iteritems()
    
    def lines_cached(self, resource):
        return self.__cache[resource][0]

    @classmethod
    def __modification_date(cls, resource):
        return resource.stat().st_mtime

    def __put_entry(self, resource, lines):
        self.__cache[resource] = (lines, self.__modification_date(resource))
        
    def modified(self, resource):
        return self.__cache[resource][1] != self.__modification_date(resource)
    
    def apply_metric_to_resource(self, resource):
        if resource not in self.__cache or self.modified(resource):
            lines = self.__decoratee.apply_metric_to_resource(resource)
            self.__put_entry(resource, lines)
            return lines
        else:
            return self.lines_cached(resource)

#class PersistentCachingFileLengthCalculatorDecorator(AbsoluteFileMetricProcessor):
#    pass
    # TODO must be implemented

class NormalizedPathsIter(object):
    """
    Decorates an iterator of items which are strings or lists of strings and applies
    os.path.normcase and posixpath.normpath to each element which looks like a path.
    
    >>> test = [('./dyn', ), [], ['dyn', '1'], set(['dyn', 'foo/../dyn']), ('foo/../dyn', 'Hallo Welt'), ('foo/..', ), ('c:\\\\test.cpp', )]
    >>> for element in NormalizedPathsIter(test): print(element)
    ('dyn',)
    ['dyn', '1']
    set(['dyn'])
    ('dyn', 'Hallo Welt')
    ('.',)
    ('c:/test.cpp',)
    """
    def __init__(self, decoratee):
        """
        
        @param decoratee: The object that should be decorated.
        @type decoratee: types.Iterable
        """
        self.__metric = decoratee.__iter__()

    def __iter__(self):
        return self
    

    def __get_normalized_item(self, item):
        # TODO replace by using a LocalPathResolver?
        #item = os.path.normcase(item) #if item.find('.') != -1:
        item = PathTools.unix_normpath(item)
        return item

    def __get_normalized_iter(self, line):
        for x in line:
            if any(x.find(sep) != -1 for sep in PathToolsConstants.anysep):
                x = self.__get_normalized_item(x)
            yield x
            
    def next(self):
        # StopIteration exception is passed through
        line = ()
        while len(line) == 0:
            line = self.__metric.next()

        my_line_iter = self.__get_normalized_iter(line)
        return line.__class__(my_line_iter) # this works for tuple, list, set, ...?

    @staticmethod
    def create(filename, what, delimiter=',', allow_missing=False):
        return NormalizedPathsIter(FileTools.create_csv_reader(filename, what, delimiter, allow_missing))


class PathToolsConstants:
    """
    @cvar anysep: A regular expression fragment that represents any possible separation character as defined by os.path 
    @type anysep: str
    """
    anysep = "[" + re.escape(os.path.sep) + (re.escape(os.path.altsep) if os.path.altsep else "") + "]"

class PathTools(object):
    """
    This utility class bundles methods manipulating filesystem paths.
    
    Its methods use os.path, but the behaviour may be undefined if os.path is neither ntpath 
    nor posixpath.
    
    @todo: Change static methods to instance methods and parametrise the object with the
        os.path module to use.
    """
    
    @staticmethod
    def fileinfo_str(filename):
        # TODO this is too specific for commons.os_util and should be hidden or moved
        return "%s (%s)" % (filename,
                            datetime.fromtimestamp(os.stat(filename).st_mtime).strftime("%Y-%m-%d %H:%M"))

    @staticmethod
    def replace_extension(filename, new_extension):
        """
        Replaces the extension within a path by another.
        
        @param filename: The original file name (path), optionally including an extension.
        @type filename: basestring
        @param new_extension: The new extension.
        @type new_extension: basestring
        @return: type(filename)
        
        >>> PathTools.replace_extension(filename="/a/c.cpp", new_extension=".h")
        '/a/c.h'
        >>> PathTools.replace_extension(filename="/a/c", new_extension=".h")
        '/a/c.h'
        """
        return os.path.splitext(filename)[0] + new_extension

    @staticmethod
    def relative_path(path_name, relative_to, ignore_absolute=True, path_module=os.path):
        """
        >>> PathTools.relative_path('./inc/foo.df', ".\\\\inc\\\\bar.df")
        'foo.df'
    
        >>> PathTools.relative_path('./_dyn/foo.h', '.\\\\inc\\\\bar.df')
        '..\\\\_dyn\\\\foo.h'
        
        @param ignore_absolute: If true, absolute paths will be returned without modification 
        """
        # TODO warum sollte man absolute Pfade ignorieren? es könnte sinnvoll sein, Pfade, die nicht unterhalb von relative_to liegen, zu ignorieren
        if not path_module.isabs(path_name) or not ignore_absolute:
            if hasattr(path_module, "relpath"):
                return path_module.relpath(path_name, path_module.dirname(relative_to))
            else:
                warnings.warn("Using path module without relpath", DeprecationWarning)
                return compatrelpath(path_name, path_module.dirname(relative_to))
        else:
            return path_name
        # norm_path_name = os.path.normcase(path_name)
        # norm_relative_to = os.path.normcase(relative_to)
        # logging.error("%s,%s" % (os.path.dirname(norm_path_name), os.path.dirname(norm_relative_to)))
        # if os.path.dirname(norm_path_name) == os.path.dirname(norm_relative_to):
            # return os.path.basename(norm_path_name)
        # else:
            # return None

    @staticmethod
    def unix_normpath(path):
        """
        Transforms a ntpath or posixpath path to a (normalized) posixpath path.
        
        @todo: Should be renamed to to_posixpath_normpath.
        
        >>> PathTools.unix_normpath('/x/y/z')
        '/x/y/z'
        >>> PathTools.unix_normpath('\\\\x\\\\y\\\\..\\\\z')
        '/x/z'
        """
        return os.path.normpath(path).replace(os.path.sep, posixpath.sep)

    __cygwin_regex = re.compile("(?i)" + PathToolsConstants.anysep + "cygdrive")
    @staticmethod
    def is_cygwin_directory(path):
        """
        >>> PathTools.is_cygwin_directory("/cygdrive/D/x/y/z")
        True
        >>> PathTools.is_cygwin_directory("/x/y/z")
        False
        >>> PathTools.is_cygwin_directory("D:\\\\x\\\\y\\\\z")
        False
        """
        return PathTools.__cygwin_regex.match(path) != None

    @staticmethod
    def cygwin_to_cmd_path(path):
        return os.path.normpath(os.path.normcase(re.sub(r'(?i)[/\\\\]cygdrive[/\\\\]([a-z])', r'\1:', path)))
    
    @staticmethod
    def windows_to_native(windows_path):
        """
        Convert a (relative) Windows path to a native path.
        
        If windows_path is not a Windows path, the result is undefined.
        
        >>> PathTools.windows_to_native("D:\\\\foo")
        'D:\\\\foo'
        >>> PathTools.windows_to_native(".\\\\foo")
        '.\\\\foo'

        #>>> PathTools.windows_to_native("D:\\\\foo")
        #ValueError on POSIX
        #>>> PathTools.windows_to_native("/foo")
        #'/foo'
        """
        if os.path == posixpath:
            if ntpath.isabs(windows_path):
                raise ValueError("Cannot convert an absolute Windows path to POSIX: %s" % windows_path)
            return windows_path.replace('\\', os.path.sep)
        elif os.path == ntpath:
            return windows_path
        else:
            raise NotImplementedError("Can only convert to posix or nt")
            

    @staticmethod
    def native_to_posix(native_path):
        """
        >>> PathTools.native_to_posix("D:\\\\foo")
        'D:/foo'
        >>> PathTools.native_to_posix("/foo")
        '/foo'
        """
        if os.path == posixpath:
            return native_path
        elif os.path == ntpath:
            return native_path.replace('\\', '/')
        else:
            raise NotImplementedError()
        
    @staticmethod
    def get_url_for_local_path(path):
        """
        >>> PathTools.get_url_for_local_path('D:\\\\foo')
        'file:///D:/foo'
        >>> PathTools.get_url_for_local_path('D:\\\\foo bar')
        'file:///D:/foo%20bar'
        """
        return urlparse.SplitResult("file", None, urllib.pathname2url(path), None, None).geturl()
    
    @staticmethod
    def splitall(path):
        """
        >>> PathTools.splitall('D:\\\\foo\\\\bar\\\\x.txt')
        ['D:\\\\', 'foo', 'bar', 'x.txt']
        """
        retval = list()
        restpath = path
        while restpath != '':
            (head, tail) = os.path.split(restpath)
            restpath = ''
            if tail:
                retval = [tail] + retval
                restpath = head
            elif head:
                retval = [head] + retval
            
        return retval

    @staticmethod
    def splitall_iter(path):
        """
        >>> list(PathTools.splitall_iter('D:\\\\foo\\\\bar\\\\x.txt'))
        ['D:\\\\', 'foo', 'bar', 'x.txt']
        """
        (head, tail) = os.path.split(path)
        if head:
            if tail:
                for x in PathTools.splitall_iter(head):
                    yield x
                yield tail
            else:
                yield head
        else:
            if tail:
                yield tail
                
    @staticmethod
    def resource_to_relpath(canonic_resource, path_module=os.path):
        if canonic_resource.get_resolution_root():
            return PathTools.relative_path(path_name=canonic_resource.name(), relative_to=canonic_resource.get_resolution_root() + path_module.sep, 
                ignore_absolute=False, 
                path_module=path_module)
        else:
            return canonic_resource.name()

    @staticmethod
    def canonicalize_capitalization(path, pathmodule=os.path, strict=False):
        if not pathmodule.exists(path):
            if strict:
                raise ValueError("File %s cannot be found" % (path, ))
            else:
                return path
        (head, tail) = pathmodule.split(path)
        if (pathmodule.sep in head) and tail:
            head = PathTools.canonicalize_capitalization(head)
        for tail_cand in os.listdir(head):
            if tail_cand.lower() == tail.lower():
                tail = tail_cand
                break
            
        return os.path.join(head, tail)

    
    @classmethod
    def common_base_directory(cls, file_paths, pathmodule=os.path):
        return StringTools.get_common_prefix(imap(os.path.normpath, imap(pathmodule.dirname, file_paths)))
                

class WalkTools(object):
    @staticmethod
    def walk_extensions(top, extensions, onerror=None, skip_dirs=[]):
        """
        Walks a directory tree and enumerates all files with certain extensions.
        
        @param top: base directory
        @param skip_dirs: subdirectories to skip
        @param extensions: A tuple (not a list) of extensions to look for, e.g. ('.cpp', '.h') 
        @param onerror: unary function to call on an error, a OSError will be passed as the parameter
        
        @rtype: iterable of strings (paths starting with top)
        """
        for dirpath, dirnames, filenames in os.walk(top=top, onerror=onerror):
            for dirname in skip_dirs:
                try:
                    dirnames.remove(dirname)
                except ValueError:
                    pass
            for filename in ifilter(lambda filename: filename.endswith(extensions), filenames):
                yield os.path.join(dirpath, filename)


class FileTools(object):
    """
    A static utility class containing extension methods for files.
    """
    
    __logger = None

    @staticmethod
    def file_len(fname):
        """
        Returns the number of apply_metric_to_resource in a file.
        
        @param fname: path of the file
        @return: a non-negative integer
        @raise OSError: if the file does not exist 
        @deprecated: Use commons.os_util.LocalFileMetricProcessor instead
        """
        if os.path.exists(fname):
            with open(fname) as f:
                i = -1
                for i, _l in enumerate(f):
                    pass
                return i + 1
        else:
            raise OSError("file not found: %s" % fname)
            #raise Warning()

    @classmethod
    def create_csv_dict_reader(cls, filename, what, fieldnames, delimiter=',', allow_missing=False):
        if cls.__logger == None:
            cls.__logger = logging.getLogger(cls.__module__)
        if os.path.exists(filename):
            cls.__logger.info("Reading %s from %s" % (what, PathTools.fileinfo_str(filename)))
            csv_reader = csv.DictReader(open(filename), delimiter=delimiter, fieldnames=fieldnames)
        elif allow_missing:
            cls.__logger.info("%s not found when trying to read %s" % (filename, what))
            csv_reader = ()
        else:
            raise IOError("%s not found when trying to read %s" % (filename, what))
        return csv_reader

    @classmethod
    def create_csv_reader(cls, filename, what, delimiter=',', allow_missing=False):
        if cls.__logger == None:
            cls.__logger = logging.getLogger(cls.__module__)
        if os.path.exists(filename):
            cls.__logger.info("Reading %s from %s" % (what, PathTools.fileinfo_str(filename)))
            csv_reader = csv.reader(open(filename), delimiter=delimiter)
        elif allow_missing:
            cls.__logger.info("%s not found when trying to read %s" % (filename, what))
            csv_reader = ()
        else:
            raise IOError("%s not found when trying to read %s" % (filename, what))
        return csv_reader

class PrinterDecorator(object):
    def __init__(self, decoratee, out_file=sys.stdout):
        self.__dict__['_PrinterDecorator__file'] = out_file
        self.__dict__['_PrinterDecorator__instance'] = decoratee

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        decoratee_attr = getattr(self.__instance, attr)
        if callable(decoratee_attr):
            return lambda ** args: self.__file.write(decoratee_attr(args))
        else:
            return decoratee_attr

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

def execute_shell_script(script_path):
    return os.system("bash %s" % (script_path))

class FileResource(Resource):
    """
    An implementation of the C{Resource} interface for local files.
    """
    
    def __init__(self, path, resolution_root=None):
        self.__path = path
        self.__resolution_root = resolution_root

    def get_resolution_root(self):
        return self.__resolution_root

    def exists(self):
        return os.path.exists(self.__path)

    def open(self, mode="r"):
        try:            
            return open(self.__path, mode)
        except IOError, exc:
            raise ResourceAccessError("File %s could not be opened with mode %s" % (self.__path, mode), exc)            

    def stat(self):
        try:
            return os.stat(self.__path)
        except OSError, exc:
            raise ResourceAccessError("Could not stat file %s" % (self.__path), exc)            

    def name(self):
        return self.__path

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.name())
    
    def __hash__(self):
        return hash(self.__path)
    
    def __eq__(self, other):
        return ((isinstance(other, FileResource) and self.__path == other.name()) 
                or (isinstance(other, basestring) and self.__path == other))         

class ResourceResolver(object):
    #TODO this should be moved to commons.resource_if
    
    def return_types(self):
        """
        Returns the types of Resource objects that could be returned by resolve.
        
        @rtype: iterable of TypeType objects
        """
        raise NotImplementedError(self.__class__)        
    
    def resolve(self, input_identifier, force_check=False):
        """
        Resolves a context-dependent resource identifier to an absolute resource identifier.
        
        @param input_identifier: an object used to identify a file, the valid values are 
            implementation-dependent, e.g. a filename, a relative path, or a URL fragment
        @param force_check: if True, the PathResolver must check that the resource exists; 
            however, it cannot be guaranteed that this holds after the method returns
        @return: an absolute resource identifier, e.g. an absolute local path or absolute URL,
            that can be reasonably assumed to exist
        @rtype: Resource
        @raise IllegalResourceIdentifierError: if the format of input_path is invalid
        @raise ResourceUnresolvable: if the format of input_path is valid, but it could not be resolved 
        """
        raise NotImplementedError(self.__class__)
    
    def unresolve(self, absolute_identifier):
        raise NotImplementedError(self.__class__)
        
    
class LocalPathResolver(ResourceResolver):
    """
    A resource resolver, whose resolve method returns absolute local paths.
    """
    def _get_path(self, input_identifier):
        if isinstance(input_identifier, FileResource):
            path = input_identifier.name()
        elif isinstance(input_identifier, basestring):
            path = input_identifier
        else:
            raise IllegalResourceIdentifierError("Neither string nor FileResource: %s" % input_identifier)
        return path
    
    def get_base_paths(self):
        raise NotImplementedError(self.__class__)

    def return_types(self):
        return (FileResource, )
    
class NullPathResolver(LocalPathResolver):

    def resolve(self, input_identifier, force_check=False):
        path = self._get_path(input_identifier)
        abs = os.path.abspath(path)
        if force_check and not os.path.exists(abs):
            raise ResourceUnresolvable(candidates=[abs])
        return FileResource(abs)

    def get_base_paths(self):
        return ()
    
class FailingPathResolver(LocalPathResolver):

    def resolve(self, input_identifier, force_check=False):
        raise ResourceUnresolvable(candidates=[])

    def get_base_paths(self):
        return ()

class FixedBaseDirPathResolver(LocalPathResolver):
    """
    A local path resolver, which resolves paths relative to a single base path.
    
    >>> resolver = FixedBaseDirPathResolver("/foo", path_module=posixpath)
    >>> posixpath.normpath(resolver.resolve("bar").name())
    '/foo/bar'
    """
    def __init__(self, base_resource, path_module=os.path, normalize=False, strict=True):
        """
        @param path_module: an os.path-like object
        @type path_module: an object with the methods isabs and exists (and normpath if normalize==True)
        
        @param normalize: states whether returned paths must be normalized
        @type normalize: boolean
        """
        self.__strict = strict
        self.__path_module = path_module
        base_path = self._get_path(base_resource)
        self.__base_resource = base_resource
        #assert self.__path_module.isabs(base_path)
        self.__base_path = base_path
        if normalize:
            self.__normpath = self.__path_module.normpath
        else:
            self.__normpath = lambda x: x
    
    def resolve(self, input_identifier, force_check=False):
        path = self._get_path(input_identifier)
        result = None
        if self.__path_module.isabs(path):
            if self.__strict:
                if not self.__path_module.normcase(self.__path_module.normpath(path)).startswith(self.__path_module.normcase(self.__base_path)):
                    raise IllegalResourceIdentifierError("Absolute path %s is not in basedir %s " % (path, self.__base_path))
            result = path
        else:
            result = self.__path_module.join(self.__base_path, path)
            if force_check and not self.__path_module.exists(result):
                raise ResourceUnresolvable(candidates=[result])
        return FileResource(self.__normpath(result), resolution_root=self.__base_resource)

    def get_base_paths(self):
        return (self.__base_path,)

class MultipleBaseDirPathResolver(LocalPathResolver):
    """
    A local path resolver, which resolves paths relative to a set of base paths.
    
    Implementation notes:
    * os.path.exists will always be called within the resolve method, regardless of the value of the force_check parameter.  
    
    >>> resolver = MultipleBaseDirPathResolver(["/foo", "/foo2"], path_module=posixpath)
    """
    def __init__(self, base_resources, path_module=os.path, normalize=False, default=None, strict=True):
        """
        @param default: The fallback path to be used if resolving an identifier does not match in any of the base resources. 
        
        @see: FixedBaseDirPathResolver.__init__ for the description of the class parameters
        """
        self.__strict = strict
        self.__default = default
        self.__path_module = path_module
        self.__base_paths = []
        for base_resource in base_resources:
            base_path = self._get_path(base_resource)
            assert self.__path_module.isabs(base_path)
            self.__base_paths.append(self.__path_module.normpath(base_path))
        if normalize:
            self.__normpath = self.__path_module.normpath
        else:
            self.__normpath = lambda x: x
    
    def resolve(self, input_identifier, force_check=False):
        path = self._get_path(input_identifier)
        result = None
        candidates = []
        resolution_root = None
        if self.__path_module.isabs(path):
            for base_path in self.__base_paths:
                if self.__path_module.normpath(path).startswith(base_path):
                    resolution_root = base_path
                    result = path
                    break                
            if self.__strict and result == None:
                raise IllegalResourceIdentifierError("Absolute path %s is not in any basedir %s " % (path, self.__base_paths))
            else:
                result = path
        else:
            for base_path in self.__base_paths:
                candidate = self.__path_module.join(base_path, path)
                candidates.append(result)
                if self.__path_module.exists(candidate):
                    result = candidate
                    resolution_root = base_path
                    break                    
        if result == None:
            if self.__default:
                result = self.__path_module.join(self.__default, path)
                resolution_root = self.__default
                candidates.append(result)
            else:
                raise ResourceUnresolvable(candidates=candidates)
        if force_check and not self.__path_module.exists(result):
            raise ResourceUnresolvable(candidates=candidates)
        return FileResource(self.__normpath(result), resolution_root=resolution_root)

    def get_base_paths(self):
        return tuple(self.__base_paths)

class NullGenerationStrategy(GenerationStrategy):
    """
    An implementation of C{GenerationStrategy} that never modifies the input resource and 
    does not generate any output. 
    """
    
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
        
    def process(self, repair_resource, generator_func):
        #assert isinstance_or_duck(repair_resource, FileResource)
        return generator_func(repair_resource, FileResource(os.devnull))

class ExternalGenerationStrategy(GenerationStrategy):
    """
    Am implementation of C{GenerationStrategey} that transforms the input resources to a 
    different (external) target directory. The folder hierarchy of the input resources
    is reproduced in the output directory tree.  
    """
    def __init__(self, target_dir, copy_on_error=False):
        """
        @param target_dir: The pathname of the base directory for the target files. 
        @type target_dir: basestr 
        """
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__target_dir = target_dir
        self.__copy_on_error = copy_on_error
        self.__target_resolver = FixedBaseDirPathResolver(self.__target_dir, strict=False)
        
    def process(self, input_resource, generator_func):
        """
        
        @type input_resource: Resource (but the delimiters used by the input resource must be compatible with the delimiters of os.path)
        """
        assert isinstance_or_duck(input_resource, FileResource)
        input_resource_root = input_resource.get_resolution_root()
        if not input_resource_root:
            raise ValueError("Input resource %s has no resolution root, cannot determine correct output path" % input_resource)
        relpath = PathTools.relative_path(input_resource.name(), relative_to=input_resource_root.name() + os.path.sep, ignore_absolute=False)
        output_resource = self.__target_resolver.resolve(relpath, force_check=False)
        output_directory = os.path.dirname(output_resource.name())
        if not os.path.exists(output_directory):            
            os.makedirs(output_directory)
        else:
            if not os.path.isdir(output_directory):
                raise ValueError("File %s is in the way, this is the designated output directory" % output_directory)
        try:
            return generator_func(input_resource, output_resource)
        except Exception:
            if self.__copy_on_error:
                ResourceUtil.copy(input_resource, output_resource)
            raise
        
        
class InPlaceGenerationStrategy(GenerationStrategy):
    """
    An implementation of C{GenerationStrategy} which replaces the input resources 
    with the transformed content. A backup file of the original content is generated.
    On repeated runs, the backup file and thus the original content is used, i.e.
    multiple executions of the same transformation are idempotent.
    
    If you want to transform the result of a transformation again (with the same 
    or a different transformation), the backup files must be deleted first 
    (or a different generation strategy must be used).  
    """    
    
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
    
    def process(self, input_resource, generator_func):
        """
        @type input_resource: FileResource
        """
        assert isinstance_or_duck(input_resource, FileResource)
        new_file_local = input_resource.name() + '.new'
        if os.path.exists(new_file_local):
            os.unlink(new_file_local)
        backup_resource = FileResource(input_resource.name() + '.orig', resolution_root=input_resource.get_resolution_root())
        if backup_resource.exists():
            self.__logger.info("Backup file %s already exists, regenerating from backup file" % (backup_resource, ))
            input_resource = backup_resource
            output_resource = input_resource
        else:
            input_resource = input_resource
            output_resource = FileResource(new_file_local, resolution_root=input_resource.get_resolution_root())
        try:
            retval = generator_func(input_resource, output_resource)
        except Exception:
            self.__revert(input_resource, output_resource, backup_resource)
            raise
        if output_resource.name() != input_resource.name():
            os.rename(input_resource.name(), backup_resource.name())
            os.rename(output_resource.name(), input_resource.name())
        return retval

    def __revert(self, input_resource, output_resource, backup_resource):
        if output_resource.name() == input_resource.name():
            os.unlink(input_resource.name())
            os.rename(backup_resource.name(), input_resource.name())
        else:
            if output_resource.exists():
                os.unlink(output_resource.name())
               

class PathCanonicalizer(object):
    """
    Canonicalizes paths for given base directories within a search path.
    
    Usually, if a search path contains paths that are nested within each other, there are 
    multiple possibilities to represent the same absolute path as a relative path within
    the search path.
    
    E.g. if the search path contains directories /a/b and /a, the absolute path /a/b/c may
    be represented as both b/c (relative to /a) and c (relative to /a/b).
    
    >>> pc = PathCanonicalizer(input_path_list=['/a/b', '/a'], canonic_path_list=['/a'], path_module=posixpath)
    >>> pc.canonical_resource_for_path('/a/b/c')
    "b/c"
    """
    # TODO this will behave weird when symbolic links are involved
    # TODO check_input_paths_covered is not a prerequisite for creating the PathCanonicalizer... if this is not fulfilled,
    # there are paths that cannot be canonicalized, but the current implementation is restricted to more constrained
    # use cases
    # TODO use more specific exceptions instead of ValueError
    
    @staticmethod
    def check_canonic_path_list(canonic_path_list, path_module=os.path):
        for (path1, path2) in permutations(imap(path_module.normpath, canonic_path_list), 2):
            if path2.startswith(path1):
                raise ValueError("Canonic paths are not unique: %s starts with %s" % (path2, path1)) 
         
        return True
    
    @staticmethod   
    def check_input_paths_covered(input_path_list, canonic_path_list, path_module=os.path):
        for input_path in imap(path_module.normpath, input_path_list):
            nc_input_path = path_module.normcase(input_path)
            if not any(imap(lambda canonic_path: nc_input_path.startswith(canonic_path), imap(path_module.normcase, imap(path_module.normpath, canonic_path_list)))):
                raise ValueError("Input path %s not covered by any canonic path %s" % (input_path, canonic_path_list))
    
    
    def __init__(self, input_path_list, canonic_path_list, path_module=os.path):
        # TODO check if every path resolveable by the input paths can also be resolved using a canonical path?
        self.check_canonic_path_list(canonic_path_list, path_module)
        self.check_input_paths_covered(input_path_list, canonic_path_list, path_module)
        self.__input_path_resolver = MultipleBaseDirPathResolver(base_resources=map(FileResource, input_path_list), path_module=path_module, normalize=True)
        self.__canonic_path_resolver = MultipleBaseDirPathResolver(base_resources=map(FileResource, canonic_path_list), path_module=path_module, strict=True)
        #self.__path_module = path_module


    def canonical_resource_for_path(self, path):
        resource = self.__input_path_resolver.resolve(path, force_check=True)
        try:
            canonic_resource = self.__canonic_path_resolver.resolve(resource, force_check=False)
        except IllegalResourceIdentifierError:
            raise ResourceUnresolvable()
        return canonic_resource

    #def canonicalize(self, path):
    #    return PathTools.resource_to_relpath(self.canonical_resource_for_path(path), path_module=self.__path_module)

    
    @classmethod
    def get_canonic_path(cls, path, candidate_paths, path_module):
        path_joined = path_module.join(*path) + path_module.sep
        result = path_joined
        for other_path in candidate_paths:
            other_path_joined = path_module.join(*other_path) + path_module.sep
            if path_module.normcase(path_joined).startswith(path_module.normcase(other_path_joined)) and len(other_path_joined) < len(result):
                result = other_path_joined
        return result[:len(result)-len(path_module.sep)]
    
    @classmethod
    def default_canonic_path_list(cls, input_include_paths, path_module=os.path):
        norm_input_include_paths = map(path_module.split, imap(path_module.normpath, input_include_paths))
        result = []
        
        CollectionTools.extend_unique_keys(result, 
                                           (cls.get_canonic_path(path, norm_input_include_paths, path_module=path_module) for path in norm_input_include_paths),
                                           lambda path: path_module.normcase(path))
        return result

class ShelveCache(object):
    """
    An implementation of a persistent object cache based on the shelve  
    (i.e. Berkeley DB files) and pickle modules.
    """
    
    # TODO extract Cache interface
    # TODO ensure that tuples with same hash values do not collide unnoticed
    
    def __init__(self, storage_path, factory_func, source_data_last_modified):
        self.__shelf = shelve.open(storage_path)
        self.__factory_func = factory_func
        self.__source_data_last_modified = source_data_last_modified
        
    def __del__(self):
        self.close()
        
    def __make_key(self, key):
        return str(key)
        
    def close(self):
        if self.__shelf:
            self.__shelf.close()
            self.__shelf = None
            
    def get_cached_object_creation_time(self, key):
        return self.__shelf[self.__make_key(key)][0]
            
    def get_cached_object(self, key):
        return self.__shelf[self.__make_key(key)][1]

    def has_cached_object(self, key):
        return self.__make_key(key) in self.__shelf

    def has_valid_cached_object(self, key):
        return self.has_cached_object(key) and self.get_cached_object_creation_time(key) >= self.__source_data_last_modified
            
    def invalidate_cached_object(self, key):
        del self.__shelf[self.__make_key(key)]
        self.__shelf.sync()
            
    def __update_cached_object(self, key, value):
        self.__shelf[self.__make_key(key)] = (datetime.now(), value)
        self.__shelf.sync()

    def get_object(self, key):
        if self.has_valid_cached_object(key):
            return self.get_cached_object(key)
        else:
            result = self.__factory_func(key)
            self.__update_cached_object(key, result)
            return result            
    
class FileListsManager(object):
    # TODO use generic cache
    
    def __init__(self, cache_storage_dir, extensions):
        self.__cache_storage_dir = cache_storage_dir
        self.__filelists = dict()
        self.__extensions = tuple(extensions)
        self.__invalidated = False
        self.__logger = logging.getLogger(self.__class__.__module__)
        
    def __load_filelist(self, filename):
        self.__logger.info("Loading filelist from %s" % (PathTools.fileinfo_str(filename)))
        result = set()
        for line in open(filename):            
            result.add(line.strip("\n"))
        return frozenset(result)
    
    def __create_filelist(self, basepath):
        self.__logger.info("Creating filelist for %s" % basepath)
        # TODO parametrise skip_dirs (!)
        result = frozenset(WalkTools.walk_extensions(basepath, self.__extensions, skip_dirs=['.svn']))
        if len(result):
            self.__logger.info("Number of entries in filelist for %s is %i" % (basepath, len(result)))
        else:
            self.__logger.warning("Filelist for %s is empty" % basepath)
        return result
    
    def __store_filelist(self, filename, filelist):
        with open(filename, "w") as outputfile:
            for line in filelist:
                print >>outputfile, line
    
    def __get_filelists_cache_filename(self, basepath):
        return os.path.join(self.__cache_storage_dir, ".filelist_cache.%i" % hash(basepath))

    def __load_or_create_filelist(self, basepath):
        filelist_cache = self.__get_filelists_cache_filename(basepath)
        if os.path.exists(filelist_cache) and not self.__invalidated:
            self.__logger.info("Loading filelist for %s" % basepath)
            return self.__load_filelist(filelist_cache)
        else:
            filelist = self.__create_filelist(basepath)
            self.__store_filelist(filelist_cache, filelist)
            return filelist
    
    def invalidate_all(self):
        # TODO delete filelists on disk
        self.__logger.info("Invalidating all cached filelists") 
        self.__filelists = dict()
        self.__invalidated = True
    
    def invalidate_filelist(self, basepath):
        if basepath in self.__filelists:
            del self.__filelists[basepath]
        filelists_cache = self.__get_filelists_cache_filename(basepath)
        if os.path.exists(filelists_cache):
            os.unlink(filelists_cache)
    
    def get_filelist(self, basepath):
        if basepath not in self.__filelists:
            self.__filelists[basepath] = self.__load_or_create_filelist(basepath)
        return self.__filelists[basepath]
    
    def __missing__(self, key):
        return self.get_filelist(key)
        
    def __getattr__(self, attr):
        """ Delegate access to dictionary """
        return getattr(self.__filelists, attr)
        

#doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
