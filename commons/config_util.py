# -*- coding: UTF-8 -*-
'''
Contains various classes used in the implementation of the IoC mechanism. 
Additionally, it contains some base classes that can be used by implementors 
of extensions of the IoC mechanism. 

Created on 09.09.2010

@warning: the doctest tests in this module do not work anymore. These should be removed and replaced by real documentation.
For tests/examples, see test.commons.config_util_test instead.

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable
from commons.config_extension_if import IAutoWireConfigParser
from commons.core_util import ClassTools, CollectionTools
from commons.os_util import FileResource
from commons.v26compat_util import compatchain
from types import TypeType
from itertools import imap
import logging
import os.path
import sys
import warnings

# TODO this module contains some parts that belong to different module types
# TODO implement support for decorators (commons.config_if.Decorator)!

class ConfigTools(object):
    FQN_SEP = "."
    
    @staticmethod
    def fqn_to_pair(qualified_class_name):
        """
        
        @param qualified_class_name:
        @raise ValueError: if qualified_class_name has not the correct format 
        """
        try:
            module_name, class_name = qualified_class_name.rsplit(ConfigTools.FQN_SEP, 1)
        except ValueError:
            raise ValueError("Not a fully qualified class name: %s" % qualified_class_name)
        if not len(module_name) or not len(class_name):
            raise ValueError("Not a fully qualified class name: %s" % qualified_class_name)
        return module_name, class_name
    
    @staticmethod
    def pair_to_fqn(name_tuple):
        assert len(name_tuple) == 2
        return "%s%s%s" % (name_tuple[0], ConfigTools.FQN_SEP, name_tuple[1])
    
    @staticmethod
    def to_fqn(class_object):
        """
        @return: Returns the fully quallified name (fqn).
        """
        return "%s%s%s" % (class_object.__module__, ConfigTools.FQN_SEP, class_object.__name__)

    @staticmethod
    def is_class_abstract_autoconfigurable(class_object):
        """
        >>> import commons.database_if
        >>> ConfigTools.is_class_abstract_autoconfigurable(commons.database_if.DatabaseConfiguration)
        True
        >>> import configuration.config_db
        >>> ConfigTools.is_class_abstract_autoconfigurable(configuration.config_db.RevEngToolsDatabaseConfiguration)
        False
        """
        #return issubclass(class_object, AutoConfigurable) \
        #    and class_object != AutoConfigurable
        return AutoConfigurable in class_object.__bases__

    @staticmethod
    def is_class_concrete_autoconfigurable(class_object):
        """
        >>> import commons.database_if
        >>> ConfigTools.is_class_concrete_autoconfigurable(commons.database_if.DatabaseConfiguration)
        False
        >>> import configuration.config_db
        >>> ConfigTools.is_class_concrete_autoconfigurable(configuration.config_db.RevEngToolsDatabaseConfiguration)
        True
        """
        return ConfigTools.is_class_any_autoconfigurable(class_object) \
            and not ConfigTools.is_class_abstract_autoconfigurable(class_object)

    @staticmethod
    def is_class_any_autoconfigurable(class_object):
        """
        >>> import commons.database_if
        >>> ConfigTools.is_class_any_autoconfigurable(commons.database_if.DatabaseConfiguration)
        True
        >>> import configuration.config_db
        >>> ConfigTools.is_class_any_autoconfigurable(configuration.config_db.RevEngToolsDatabaseConfiguration)
        True
        """
        return issubclass(class_object, AutoConfigurable) \
            and class_object != AutoConfigurable

    @staticmethod
    def is_autoconfigurable_object(variable):
        """
        >>> ConfigTools.is_autoconfigurable_object(Test.ac_instance)
        True
        >>> ConfigTools.is_autoconfigurable_object(Test.ac_class)
        False
        """
        # return isinstance(variable, AutoConfigurable)
        return isinstance(variable, object) \
            and hasattr(variable, '__class__') \
            and ConfigTools.is_class_abstract_autoconfigurable(getattr(variable, '__class__'))

    @staticmethod
    def is_autoconfigurable_class(module, config_var_name):
        """
        >>> ConfigTools.is_autoconfigurable_class(Test, 'ac_instance')
        False
        >>> ConfigTools.is_autoconfigurable_class(Test, 'ac_class')
        True
        >>> ConfigTools.is_autoconfigurable_class(sys.modules[ConfigTools.__module__], 'AutoConfigurable')
        False
        >>> ConfigTools.is_autoconfigurable_class(ConfigTools, 'Test')
        False
        """
        var = getattr(module, config_var_name, None)
        return isinstance(var, TypeType) \
                and ConfigTools.is_class_abstract_autoconfigurable(var) \
                and config_var_name != var.__name__
                # and issubclass(var, AutoConfigurable) \

    @staticmethod
    def get_type_of_autoconfigurable_class_or_instance(variable):
        """
        Result is undefined if variable is neither a subclass of AutoConfigurable or its instance.
        
        >>> ConfigTools.get_type_of_autoconfigurable_class_or_instance(Test.ac_instance).__name__
        'Testee'
        >>> ConfigTools.get_type_of_autoconfigurable_class_or_instance(Test.ac_class).__name__
        'Testee'
        """
        if ConfigTools.is_autoconfigurable_object(variable):
            return type(variable)
        else:
            return variable

    @classmethod
    def get_config_variables_single(cls, module):
        def __module_config_vars_by_name(module):
            warnings.warn("deprecated", DeprecationWarning)
            return [config_var_name for config_var_name in dir(module)
                    if config_var_name.startswith('config_')]

        def __module_config_vars_by_type(module):
            return [config_var_name for config_var_name in dir(module)
                    if cls.is_autoconfigurable_object(getattr(module, config_var_name, None))
                    or cls.is_autoconfigurable_class(module, config_var_name)]
        # TODO make this configurable
        return __module_config_vars_by_type(module)

    @classmethod
    def get_config_variables_iter(cls, modules):
        """
        Returns a list of pairs of a module and a name of a configuration variables in that module. 
        """
        config_variable_iter = compatchain.from_iterable(((module, config_var_name)
                                 for config_var_name in cls.get_config_variables_single(module))
                                for module in modules)
        return config_variable_iter

    @classmethod
    def get_abstract_adapter_types_for_config_variables_iter(cls, module_config_var_pairs):
        return (ConfigTools.get_type_of_autoconfigurable_class_or_instance(getattr(module, config_var))
                for module, config_var in module_config_var_pairs)

    @classmethod
    def get_abstract_adapter_types_for_config_variables_set(cls, module_config_var_pairs):
        return set(cls.get_abstract_adapter_types_for_config_variables_iter(module_config_var_pairs))

    @staticmethod
    def decode_parameter_value(parameter_value_dict, load_class_func):
        # TODO this must be revised... and documented
        parameter_type = parameter_value_dict["type"]
        parameter_value_string = parameter_value_dict["value"]
        try:
            if parameter_type == "class":
                parameter_value = load_class_func(*ConfigTools.fqn_to_pair(parameter_value_string))
            elif parameter_type == "object": # TODO parameter_value_string is either a name of an object reference, or a class name
                parameter_value = load_class_func(*ConfigTools.fqn_to_pair(parameter_value_string))()
            else:
                parameter_value = eval(parameter_type)(parameter_value_string) # TODO instantiation should also be done by the load_class_func (it might be a singleton!)
        except Exception, e:
            raise ValueError("Invalid value: type=%s, value=%s" % (parameter_type, parameter_value_string), e)
        return parameter_value

    @staticmethod
    def decode_parameters(parameters, load_class_func):
        decoded_parameters = dict()
        errors = list()
        if parameters:
            for (parameter_name, parameter_value_dict) in parameters.iteritems():
                try:
                    decoded_parameters[parameter_name] = ConfigTools.decode_parameter_value(parameter_value_dict, load_class_func)                                      
                except ValueError, e:
                    errors.append("Error for parameter %s" % parameter_name, e)
            if len(errors):
                raise ValueError("Erroneous parameters", errors)
        
        return decoded_parameters

class ModuleEnumerator(object):
    PYTHON_MODULE_FILE_EXTENSION = '.py'
    PACKAGE_SEPARATOR = '.'

    @classmethod
    def get_package_prefix_for_dirname(cls, directory):
        normdirectory = os.path.normpath(directory)
        if normdirectory == os.path.curdir:
            return ""
        elif normdirectory.startswith(os.path.pardir):
            raise ValueError("directory %s=%s is not within directory hierarchy" % (directory, normdirectory))
        else:
            return cls.PACKAGE_SEPARATOR.join(normdirectory.split(os.path.sep)) + "."

    @classmethod
    def find_modules(cls, basedir, startdir="."):
        """
        Finds Python module sources in a directory.
        
        @param basedir: base directory of the python modules, relative to the current working directory
        @param startdir: directory where to start to descent finding modules, relative to basedir
                
        >>> modules = ModuleEnumerator.find_modules("..")
        >>> len(modules) > 10
        True
        >>> gen = AutoWireConfigGenerator()
        >>> for x in modules: gen.scan_module(x)
        >>> sorted(gen.find_concretes_for_abstract('cpp.incl_deps.include_list_generator.HeaderCanonicalSorter'))
        ['cpp.incl_deps.include_list_generator.StandardGroupCanonicalSorter', 'prins.repair_includes_prins.PrinsCanonicalSorter']
        """
        # TODO this contains duplication with python.modules.OnTheFlyPythonModuleListSupply
        
        base_package = cls.get_package_prefix_for_dirname(startdir)
        walkbase = os.path.normpath(os.path.join(basedir, startdir))
        walk_result = os.walk(walkbase)
        modules = []
        for (dirpath, _dirnames, filenames) in walk_result: #@UnusedVariable
            relative_path = dirpath.replace(walkbase, '').strip(os.path.sep)
            for filename in filenames:
                (module_name, ext) = os.path.splitext(filename)
                if ext == cls.PYTHON_MODULE_FILE_EXTENSION:
                    #if len(relative_path) > 0:
                    modules.append(base_package + cls.PACKAGE_SEPARATOR.join(relative_path.split(os.path.sep) + [module_name]).strip(cls.PACKAGE_SEPARATOR))
                    #else:
                    #    pass
                        #modules.append(module_name)
        return modules

class AbstractsToConcreteMap(object):
    def __init__(self, autoconfigurables):
        self.__abstract_to_concrete = dict()
        self.__autoconfigurables = set(autoconfigurables)
        self.__regenerate_map()

    def __regenerate_map(self):
        while len(self.__autoconfigurables) > 0:
            symbol = self.__autoconfigurables.pop()
            parents = self.__find_abstract_baseclasses(symbol)
            if len(parents) > 0:
                for parent in parents:
                    if not parent in self.__abstract_to_concrete:
                        self.__abstract_to_concrete[parent] = set()
                    self.__abstract_to_concrete[parent].add(symbol)
            else:
                self.__abstract_to_concrete[symbol] = set()

    def __find_abstracts_for_concrete(self, subtype):
        abstracts = []
        for abstract in self.__abstract_to_concrete:
            if issubclass(subtype, abstract):
                abstracts.append(abstract)
        return abstracts

    def __find_abstract_baseclasses(self, symbol):
        # TODO kann hier nicht auch __bases__ benutzt werden?
        parents = set()
        for potential_baseclass in self.__autoconfigurables:
            if issubclass(symbol, potential_baseclass) and ConfigTools.is_class_abstract_autoconfigurable(potential_baseclass):
                parents.add(potential_baseclass)
        self.__autoconfigurables.difference_update(parents)
        parents.update(self.__find_abstracts_for_concrete(symbol))
        return parents

    def find_abstract(self, abstract_name):
        for (abstract, concretes) in self.__abstract_to_concrete.iteritems():
            if ConfigTools.to_fqn(abstract) == abstract_name:
                return (abstract, concretes)
        return (None, None)

    def find_concretes_for_abstract(self, abstract_name):
        (abstract, concrete_lists) = self.find_abstract(abstract_name)
        if abstract != None:
            return list(map(ConfigTools.to_fqn, concrete_lists))
        else:
            return ()

    def get_map(self):
        return self.__abstract_to_concrete

class AutoWireConfigParserBase(IAutoWireConfigParser):
    def __init__(self, entry_hook=lambda entry, context: True):
        self._current_resource = None
        self._errors = list()
        self._process_entry = entry_hook

    def parse_files_ex(self, filenames):
        #TODO extract into interface
        #TODO merge impl. with parse_files
        for name in filenames:
            self._current_resource = FileResource(name)
            for entry in self.parse_lines(open(name, 'r')):
                yield (self._current_resource, entry)
            self._current_resource = None

    def parse_files(self, filenames):
        for name in filenames:
            self._current_resource = FileResource(name)
            for entry in self.parse_lines(open(name, 'r')):
                yield entry
            self._current_resource = None

    def has_errors(self):
        return len(self._errors) > 0

    def get_errors(self):
        return iter(self._errors)

class AutoWireConfigChecker(object):
    def __init__(self):
        self.__entries = dict()
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__problems = list()
        
    def __add_problem(self, severity, description, context):
        self.__problems.append((severity, description, context))
        
    def log_problems(self):
        for (severity, description, context) in self.__problems:
            self.__logger.log(severity, "%s at %s" % (description, context))
            
    def get_problems(self):
        return tuple(self.__problems)
    
    def has_problems(self):
        return len(self.__problems) > 0
    
    def __check_abstract_exists(self, entry, context):
        (abstract, (_concrete, _concrete_parameters)) = entry
        try:
            return ClassLoader.get_class_split(*abstract)            
        except Exception, exc:
            self.__add_problem(logging.ERROR, "Abstract class %s cannot be loaded (exception: %s)" % (abstract, exc), context)
            return None
        
    def __check_concrete_exists(self, entry, context):
        (_abstract, (concrete, _concrete_parameters)) = entry
        try:
            return ClassLoader.get_class_split(*concrete)            
        except Exception, exc:
            self.__add_problem(logging.ERROR, "Abstract class %s cannot be loaded (exception: %s)" % (concrete, exc), context)
            return None
    
    def __check_abstract_autoconfigurable(self, class_obj, context):
        if not ConfigTools.is_class_abstract_autoconfigurable(class_obj):
            self.__add_problem(logging.WARNING, "Abstract class %s is not abstract-autoconfigurable" % (class_obj.__name__), context)
            return False
        else:
            return True

    def __check_concrete_autoconfigurable(self, class_obj, context):
        if not ConfigTools.is_class_concrete_autoconfigurable(class_obj):
            self.__add_problem(logging.WARNING, "Concrete class %s is not concrete-autoconfigurable" % (class_obj.__name__), context)
            return False
        else:
            return True

    def __check_type_compatibility(self, abstract_class, concrete_class, context):
        if not issubclass(concrete_class, abstract_class):
            self.__add_problem(logging.WARNING, "Concrete class %s is not a subclass of abstract class %s" % (concrete_class.__name__, abstract_class.__name__), context)
            return False
        else:
            return True

    def __check_no_duplicate(self, entry, context):
        if entry[0] in self.__entries:
            if entry[1] == self.__entries[entry[0]][0]:
                self.__add_problem(logging.INFO, "Entry %s duplicates earlier entry at %s" % (entry, self.__entries[entry[0]][1]), context)
            else:
                self.__add_problem(logging.INFO, "Entry %s overrides earlier entry at %s" % (entry, self.__entries[entry[0]][1]), context)

    def check_entry(self, entry, context="Unknown context"):
        """
        
        @param entry:
        @param context: the context where the entry was parsed from 
        @type context: commons.config_extension_if.ParseContext
        """
        abstract_class = self.__check_abstract_exists(entry, context)
        if abstract_class:
            self.__check_abstract_autoconfigurable(abstract_class, context)
        concrete_class = self.__check_concrete_exists(entry, context)
        if concrete_class:
            self.__check_concrete_autoconfigurable(concrete_class, context)
            # self.__check_parameters(entry, context)
        if abstract_class and concrete_class:
            self.__check_type_compatibility(abstract_class, concrete_class, context)
        self.__check_no_duplicate(entry, context)
        
        self.__entries[entry[0]] = (entry[1], context) # TODO store context too?

class ModuleScanner(object):
    def __init__(self):
        self.__autoconfigurables = set()
        self.__modified = False

    def gather_autoconfigurables_by_name(self, start_module_name):
        if not start_module_name in sys.modules:
            __import__(start_module_name, globals=globals(), level=0)
        start_module = sys.modules[start_module_name]
        return self.gather_autoconfigurables(start_module)

    def gather_autoconfigurables(self, start_module):
        for symbol_name in dir(start_module):
            symbol = start_module.__dict__[symbol_name]
            # TODO packages müssen anders behandelt werden, dazu müsste man wohl das Dateisystem durchsuchen
            #if isinstance(symbol, ModuleType) and not symbol_name.startswith('_'):
            #    self.scan_module("%s.%s" % (start_module_name, symbol_name))
            #el
            # TODO Nur wirklich in module enthaltene Symbole, nicht reexportierte
            if isinstance(symbol, TypeType) and \
               ConfigTools.is_class_any_autoconfigurable(symbol) and \
               symbol not in self.__autoconfigurables:
                # and \
                #symbol not in self.__abstract_to_concrete():
                self.__autoconfigurables.add(symbol)
                self.__modified = True

    def get_autoconfigurables(self):
        self.__modified = False
        return self.__autoconfigurables

    def modified(self):
        """
        Queries whether get_autoconfigurables will return a different result than in the previous call, 
        i.e. if a call to gather_autoconfigurables has found any new autoconfigurable variables. 
        """
        return self.__modified

class AutoWireConfigFileFinder(object):
    def __init__(self, flavors=[], exists_func=os.path.exists):
        self.__logger = logging.getLogger(self.__module__)
        self.__flavors = list(flavors)
        self.__exists = exists_func

        basename = 'autowire.config'
        self.__autowire_configs_in = list()
        self.add_autowire_config_in(basename)                                  

    def __try_autowire_config(self, path):
        result = []
        if self.__exists(path):
            result.append((False, path))
        for flavor in self.__flavors:
            if self.__exists(path + "-" + flavor):
                result.append((True, path + "-" + flavor))
        return result

    def __extend_normed_unique(self, result, paths):
        inputs = imap(os.path.normpath, paths)        
        CollectionTools.extend_unique(result, inputs)

    def find_autowire_configs(self):
        self.__logger.debug("Finding autowire configuration files with flavors=%s" % (self.__flavors,))
        autowire_configs = []
        for filename in self.__autowire_configs_in:
            autowire_configs.extend(self.__try_autowire_config(filename)) # current dir
        self.__logger.debug("Using autowire configuration files %s" % (autowire_configs,))

        result = []
        self.__extend_normed_unique(result, (path for flavored, path in autowire_configs if not flavored))
        self.__extend_normed_unique(result, (path for flavored, path in autowire_configs if flavored))
        result = [os.path.abspath(p) for p in result]

        return result

    def add_autowire_config_in(self, in_filename):
        #Try current dir
        self.__autowire_configs_in.append(os.path.join(os.path.curdir, in_filename))
        
        #Try application config dir
        self.__autowire_configs_in.append(os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), os.path.pardir, "configuration" ,in_filename)) # base dir    

    def add_flavors(self, flavors):
        self.__flavors.extend(flavors)

    def flavors_count(self):
        return len(self.__flavors)

class ModuleLoader(object):
    # TODO this assumes that the base path is the directory above this module. 
    # This will not be true if the ModuleLoader (and the Configurator) is used
    # outside the RevEngTools!
    BASE_PATH = os.path.normpath(os.path.join(__file__, os.path.pardir, os.path.pardir))

    @classmethod
    def is_local_module(cls, module):
        """
        
        @param module: an instance of types.ModuleType
        
        >>> import commons.configurator
        >>> ModuleLoader.is_local_module(sys.modules["commons.configurator"])
        True
        >>> import sys
        >>> ModuleLoader.is_local_module(sys.modules["sys"])
        False
        """
        if module == sys.modules["__main__"]:
            return True
        else:
            path = getattr(module, "__file__", "")
            if path:
                normedpath = os.path.normpath(path)
                return normedpath.startswith(cls.BASE_PATH) or (not os.path.isabs(path) and not normedpath.startswith(os.path.pardir))
            else:
                return False

    @classmethod
    def get_cached_local_modules_iter(cls):
        """
        A compound query, which returns an iterator over all cached modules, i.e. those in sys.modules, 
        which are local in the sense of is_local_module.
        
        @rtype: types.IteratorType
        """
        return (module for module in sys.modules.itervalues() if cls.is_local_module(module))

class ClassLoader(object):
    @staticmethod
    def get_class(qualified_class_name):
        """
        Returns the class object corresponding to a qualified class name (in the Java sense).
        
        @param qualified_class_name: a string containing a qualified class name, i.e. of the form 
            module.class. Example: commons.core_util.ClassLoader
        @rtype: an instance of types.TypeType
        @raise ImportError: if the specified module cannot be found
        @raise RuntimeError: if the class cannot be found in the specified module 
        """
        module_name, class_name = ConfigTools.fqn_to_pair(qualified_class_name)
        return ClassLoader.get_class_split(module_name, class_name)
        
    @staticmethod
    def get_class_split(module_name, class_name):
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            module = __import__(name=module_name, fromlist=[class_name])
        if class_name in dir(module):
            class_var = eval('module.%s' % class_name)
        else:
            # TODO is RuntimeError suitable?
            raise RuntimeError("Class %s not found in module %s" % (class_name, module_name))
        return class_var

    @staticmethod
    def get_instance(qualified_class_name, arguments=dict()):
        return ClassLoader.get_class(qualified_class_name)(**arguments)

    @staticmethod
    def get_constructor_args(qualified_class_name):
        return ClassTools.get_constructor_args(ClassLoader.get_class(qualified_class_name))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
