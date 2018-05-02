#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Contains the implementation of the IoC configurator. 

Created on 22.09.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable, ConfigDependent, ObjectFactory
from commons.config_plain import PlainAutoWireFormatSuite
from commons.config_util import (ConfigTools, AutoWireConfigFileFinder, 
    ModuleLoader)
from commons.core_util import frozendict
from functools import partial
from types import TypeType
import inspect
import logging
import sys
import traceback
import types
import warnings

# TODO 20120815 SGi All modules belonging to the IoC mechanism should be moved to another (sub)package, which may be released separately. 
# TODO 20120114 SGi It should be possible to present a diagnostic list of all configuration items in all autowire.configs and whether they are resolvable and active 
# TODO add possibility to filter packages to configure (by name, e.g. revengtools.* only)
# TODO add possibility to filter modules to configure (by name, e.g. *_wrapper only)
# TODO allow multiple named concrete adapters for the same type
# TODO it should be possible to verify the constructor parameter types of concrete adapters!
# TODO the type (XML or plain) of a config file should be autodetected
# TODO more accurate dependency cycle detection (as part of regular configuration or separate analysis)
# TODO 20120928 SGi could the Configurator keep only weak references to its injected objects? only for optional-singleton objects!
# TODO 20120928 SGi implement a tool to visualize object dependencies for a given IoC configuration   
# TODO 20120929 SGi distinguish different instantiation policies: always-singleton, optional-singleton/sharable, non-sharable
# TODO 20120929 SGi the current autowiring mechanism is not really type-based, but it is only based on the name of a type. the type hierarchy is ignored

default_autowire_format_parser = PlainAutoWireFormatSuite().get_parser()

class ConfigurationError(Exception):
    pass

class ObjectFactoryBase(ObjectFactory):
    def create_factory(self, xxclsxx, **kwargs):
        """
        Creates a factory function for a class that performs autowiring of any parameters when called 
        unless they are overridden by kwargs.
        
        @type xxclsxx: TypeType
        @rtype: xxclsxx
        """
        # TODO it could be checked here whether any arguments would be rewritten, and in any other case xxclsxx could be returned unmodified
        return partial(self.create_instance, xxclsxx=xxclsxx, **kwargs)    

class DefaultObjectFactory(ObjectFactoryBase):
    def create_instance(self, *args, **kwargs):
        xxclsxx = kwargs.pop('xxclsxx')
        return xxclsxx(*args, **kwargs)

class CollectingObjectFactory(ObjectFactory):
    def __init__(self):
        self.__log = set()
    
    def create_factory(self, *args, **kwargs):
        xxclsxx = kwargs.pop('xxclsxx')
        self.__log.add(xxclsxx)
        return None

    def create_instance(self, *args, **kwargs):
        xxclsxx = kwargs.pop('xxclsxx')
        self.__log.add(xxclsxx)
        return None
    
    def get_dependencies(self):
        return iter(self.__log)

class AutowiringObjectFactory(ObjectFactoryBase):
    def __init__(self, sub_object_factory, registry):
        self.__sub_object_factory = sub_object_factory
        # TODO this is not nice... this creates a cyclic dependency between AutowiringObjectFactory and ConcreteAdapterRegistry
        self.__registry = registry

    def create_instance(self, *args, **kwargs):
        """
        Creates an instance of a class and autowires any parameters unless they are overridden by kwargs.
        
        @type xxclsxx: TypeType
        @rtype: xxclsxx
        """
        xxclsxx = kwargs.pop('xxclsxx')
        # TODO support also that xxclsxx is a factory method (have a look at http://kbyanc.blogspot.de/2007/07/python-more-generic-getargspec.html)
        # TODO the inspection result could be cached, since the type can be assumed not to change
        if not isinstance(xxclsxx.__init__, type(object.__init__)): # check whether this is a native method (wrapper descriptor), TODO this is probably specific to CPython!
            (xargs, _varargs, _varkw, defaults) = inspect.getargspec(xxclsxx.__init__)
            if defaults:
                for (argname, defaultval) in zip(xargs[len(xargs)-len(defaults):], defaults):
                    # arguments specified in kwargs take precedence over autowire injection
                    if argname not in kwargs:
                        # TODO the following should be generalized such that it is not necessary for the type to subtype AutoConfigurable
                        defaultval_is_type = isinstance(defaultval, TypeType)
                        if ConfigTools.is_autoconfigurable_object(defaultval) or (defaultval_is_type and ConfigTools.is_class_abstract_autoconfigurable(defaultval)):
                            kwargs[argname] = self.__registry.get_concrete_adapter(defaultval)
                        elif defaultval_is_type and issubclass(defaultval, ConfigDependent):
                            kwargs[argname] = self.create_factory(defaultval)
                        elif isinstance(defaultval, ConfigDependent):
                            kwargs[argname] = self.create_instance(xxclsxx=type(defaultval))
                        elif isinstance(defaultval, ObjectFactory):
                            kwargs[argname] = self
        return self.__sub_object_factory.create_instance(xxclsxx=xxclsxx, *args, **kwargs)
        
        
class ConcreteAdapterRegistry(ObjectFactory):
    # TODO this should finally be moved to config_util
    # TODO an interface should be defined that includes class_loader_func, ensure_configured_func and whatever else needed
    
    def __init__(self, name_map, class_loader_func, ensure_configured_func, sub_object_factory=DefaultObjectFactory()):
        """
        
        @param name_map: A list with the mapping between the abstract moduls
            and the concrete moduls with given parameters. Can be created with
            an C{IAutoWireConfigParser}.
        @param class_loader_func: a function that takes as parameter a pair of (module_name, type_name) and 
            returns the class object. In addition, it currently must call register_concrete_adapter for that 
            class. It also must ensure that the modules loaded as a result are configured properly.
        @param ensure_configured_func: a function that ensures a module with a given name has been configured
            (this is only necessary for modules with config_ variables)
        """
        # TODO: Why is this function a parameter?
        self.__logger = logging.getLogger(self.__module__)    
        self.__concrete_adapter_singletons = dict()
        self.__abstract_adapter_names_to_concrete_adapter_names = dict(name_map)
        self.__logger.debug("Initialized ConcreteAdapterRegistry with name map %s" % (self.__abstract_adapter_names_to_concrete_adapter_names, ))
        self.__load_class = class_loader_func
        self.__ensure_configured = ensure_configured_func
        self.__regular_object_factory = AutowiringObjectFactory(sub_object_factory=sub_object_factory, registry=self)
        # TODO: currently, register_concrete_adapter is called from _ConfiguratorInternal.__load_class
        # Is this really necessary? Is it possible that the adapter is required by modules loaded by 
        # the adapter? This would indicate some cyclic dynamic dependency.
        
    def get_name_map(self):
        return frozendict(self.__abstract_adapter_names_to_concrete_adapter_names)        

    def __get_concrete_class_for_abstract_name(self, module_name, type_name):
        (concrete_module_name, concrete_type_name) = self.__get_concrete_adapter_name(module_name, type_name)
        return self.__load_class(concrete_module_name, concrete_type_name)

    def register_concrete_adapter(self, concrete_adapter_class, ignore_multiple=False):
        #assert isinstance(concrete_adapter_class, AutoConfigurable)
        #existing_adapter = self.__find_concrete_adapter(concrete_adapter_class)
        if concrete_adapter_class in self.__concrete_adapter_singletons:
            if not ignore_multiple:
                raise RuntimeError("Trying to register adapters of type more than once %s" % (type(concrete_adapter_class)))
        else:
            self.__concrete_adapter_singletons[concrete_adapter_class] = None
    
    def __find_concrete_adapter(self, config_var):
        #for concrete_adapter in self.__concrete_adapter_singletons:
        #    # TODO: best match rather than first match? or use self.__abstract_adapter_names_to_concrete_adapter_names
        #    if (type(config_var) != TypeType and isinstance(concrete_adapter, type(config_var))) \
        #        or (isinstance(config_var, TypeType) and concrete_adapter == config_var):
        #        return concrete_adapter
        if isinstance(config_var, TypeType):
            config_var_type = config_var
        else:
            config_var_type = type(config_var)
        if (config_var_type.__module__, config_var_type.__name__) in self.__abstract_adapter_names_to_concrete_adapter_names:
            (module_name, type_name) = (config_var_type.__module__, config_var_type.__name__)
            return (self.__get_concrete_class_for_abstract_name(module_name, type_name), 
                    self.__get_parameters(module_name, type_name))
        else:
            return (None, None)

    def __get_concrete_adapter_singleton(self, adapter_class, parameters):
        if adapter_class not in self.__concrete_adapter_singletons or self.__concrete_adapter_singletons[adapter_class] == None:
            try:
                # ensure that adapter.__module__ has already been configured
                self.__ensure_configured(adapter_class.__module__)
                self.__concrete_adapter_singletons[adapter_class] = self.create_instance(xxclsxx=adapter_class, **parameters) 
                # TODO apply parameters if set (isn't this already the case?)
            except Exception, exc:
                raise ConfigurationError("Error when trying to instantiate class %s\n%s: %s" % (adapter_class, exc, traceback.format_exc()))
        return self.__concrete_adapter_singletons[adapter_class]

    def get_concrete_adapter(self, config_var):
        (adapter, parameters) = self.__find_concrete_adapter(config_var)
        if adapter != None:
            decoded_parameters = ConfigTools.decode_parameters(parameters, self.__load_class) # TODO self.__load_class is not sufficient here, should be based on create_factory/create_instance
            if ConfigTools.is_autoconfigurable_object(config_var):
                value = self.__get_concrete_adapter_singleton(adapter, decoded_parameters)
            else:
                value = self.create_factory(xxclsxx=adapter, **decoded_parameters) # TODO warn if parameters non-empty?
            return value
        return None
        # TODO improve error handling, raise a proper exception if the abstract type is unknown, for example:        
        # raise ConfigurationError("Cannot determine a concrete adapter for {0}".format(config_var))


    def __get_concrete_adapter_name(self, abstract_module_name, abstract_type_name):
        (a,c) = self.__abstract_adapter_names_to_concrete_adapter_names[abstract_module_name, abstract_type_name]
        if isinstance(a, tuple):
            return a # c contains parameters in this case
        else:
            return (a, c) # @deprecated
        
    def __get_parameters(self, abstract_module_name, abstract_type_name):
        (a,c) = self.__abstract_adapter_names_to_concrete_adapter_names[abstract_module_name, abstract_type_name]
        if isinstance(a, tuple):
            return c # TODO interpret parameter string, e.g. resolve class
        else:
            return dict() # @deprecated
    
    def __str__(self):
        return "ConcreteAdapterRegistry(%s)" % str(sorted(self.__abstract_adapter_names_to_concrete_adapter_names))

    def create_factory(self, *args, **kwargs):
        return self.__regular_object_factory.create_factory(*args, **kwargs)

    def create_instance(self, *args, **kwargs):
        return self.__regular_object_factory.create_instance(*args, **kwargs)
    
    
    
    
class _ConfiguratorInternal(object):
    def __init__(self):
        self.__autowire_config_finder = AutoWireConfigFileFinder()
        self.__concrete_adapter_map = None
        self.fine = True
        self.__logger = logging.getLogger(self.__module__)
        self.__modules_configured = set()
        self.__modules_pending_configuration = set()
        
    def __ensured_module_configured(self, module_name):
        self.__logger.debug("Requesting configuration of module %s" % module_name)
        if not module_name in sys.modules:
            raise RuntimeError("Requested module %s not yet loaded, internal error" % module_name)
        self.configure_module(sys.modules[module_name])

    def configure_module(self, module):
        assert(isinstance(module, types.ModuleType))
        if module in self.__modules_pending_configuration:
            self.__logger.warning("Possible dependency cycle detected when requesting configuration of module %s involving %s. Trying to continue." % (module, list(x.__name__ for x in self.__modules_pending_configuration)))
            return
        if module in self.__modules_configured:
            return
        # config_var_names = [config_var_name for config_var_name in dir(module) if config_var_name.startswith('config_')]
        self.__logger.debug("Configuring module %s" % module)
        self.__modules_pending_configuration.add(module)
        config_var_names = ConfigTools.get_config_variables_single(module)
        for config_var_name in config_var_names:
            config_var = getattr(module, config_var_name)
            #if isinstance(config_var, AutoConfigurable):
            try:
                config_var_value = self.get_concrete_adapter(config_var)
            except ConfigurationError, exc:
                raise ConfigurationError("Error while configuring module %s" % module, exc)
            if config_var_value != None:
                #concrete_type = ConfigTools.get_type_of_autoconfigurable_class_or_instance(config_var_value)
                if isinstance(config_var_value, AutoConfigurable):
                    concrete_type = type(config_var_value)
                else:
                    concrete_type = config_var_value
                self.__logger.debug("Wiring variable %s in module %s to concrete %s" % (config_var_name, module, concrete_type))
                setattr(module, config_var_name, config_var_value)
            else:
                warnings.warn("No adapter found for assumed config variable %s %s in module %s" % (config_var_name, type(config_var), module))
                self.fine = False
        self.__modules_configured.add(module)
        self.__modules_pending_configuration.remove(module)

    def configure_modules(self, modules):
#        for module in ifilter(ModuleLoader.is_local_module, modules):
#            self.configure_module(module)            
        for module in modules:
            if ModuleLoader.is_local_module(module):
                self.configure_module(module)
            else:
                self.__logger.debug("Skipping non-local module %s" % module)

    def find_config_variables(self):
        # TODO Mögliche Optimierung: Das Ergebnis zwischenspeichern für nachfolgenden Aufruf von 
        # configure_loaded_modules. Mit dem Profiler sollte mal geprüft werden, wie sehr das
        # ins Gewicht fällt.
        config_variables = tuple(ConfigTools.get_config_variables_iter(modules=ModuleLoader.get_cached_local_modules_iter()))
        self.__logger.debug("config variables %s" % (config_variables, ))
        return config_variables

    def find_abstract_adapter_types(self):
        """
        Returns a set of all abstract adapter classes used in a config variable in any loaded module.
        """
        module_config_var_pairs = self.find_config_variables()
        return ConfigTools.get_abstract_adapter_types_for_config_variables_set(module_config_var_pairs)
       
    def get_autowire_config_finder(self):
        return self.__autowire_config_finder
    
    def get_adapter_map(self):
        return self.__concrete_adapter_map.get_name_map()
    
    def get_concrete_adapter(self, config_var):
        concrete_adapter = self.__concrete_adapter_map.get_concrete_adapter(config_var)
        if concrete_adapter:
            return concrete_adapter
        else:
            # TODO workaround... returning None should be defined okay
            if not config_var.__module__.startswith("test.commons.testdata"):
                raise ConfigurationError("No concrete adapter found for %s" % (config_var))            
    
    def create_factory(self, cls, **kwargs):
        return self.__concrete_adapter_map.create_factory(xxclsxx=cls, **kwargs)
    
    def create_instance(self, cls, *args, **kwargs):
        return self.__concrete_adapter_map.create_instance(xxclsxx=cls, *args, **kwargs)
    

    ###### The following methods depend on sys or module the set of loaded modules indirectly

    def load_configuration(self, flavors):
        if len(flavors) > 0:
            if self.__autowire_config_finder.flavors_count() > 0:
                self.__logger.warning(("Some flavors have already been registered, flavors %s "
                        "passed to default() will be processed afterwards") % 
                    flavors)
            self.__autowire_config_finder.add_flavors(flavors)
        self.__import_configuration_package()
        configs = self.__autowire_config_finder.find_autowire_configs()
        if len(configs) > 0:
            self.__logger.info("Reading autowire config files %s" % (configs, ))
            parser = default_autowire_format_parser
            self.__concrete_adapter_map = ConcreteAdapterRegistry(name_map=dict(parser.parse_files(configs)), 
                                                                  class_loader_func=self.__load_class,
                                                                  ensure_configured_func=self.__ensured_module_configured)
            if parser.has_errors():
                self.__logger.warning("Errors during autowire.config parsing:\n" + "\n".join(parser.get_errors()))
                self.fine = False 
        else:
            raise ConfigurationError("No autowire config file found")

    def default(self, flavors = ()):
        """
        Performs the default configuration of all loaded modules using the autowire.config files.
        """
        self.__logger.info("Configuring script %s" % (traceback.extract_stack(limit=2)[0][0],))
        if not self.__concrete_adapter_map:
            self.load_configuration(flavors)
        self.configure_loaded_modules()
        return self.fine
        
    ###### The following methods depend on sys or the set of loaded modules directly

    def __import_configuration_package(self):
        try:
            __import__(name='configuration')
        except ImportError, exc:
            self.__logger.warning("Package 'configuration' could not be imported, cause: %s", exc)

    def __get_module(self, module_name, class_name):
        # TODO is it necessary to pass and use class name here?
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            try:
                self.__logger.debug("Importing module %s (class=%s)" % (module_name, class_name))
                module = __import__(name=module_name, fromlist=[class_name])
            except ImportError, exc:
                raise ConfigurationError(exc)
        return module

    def __load_concrete_adapter(self, module_name, class_name):
        # TODO check first if the given adapter has already been loaded?
        modules_loaded_previously = set(sys.modules.itervalues())
        module = self.__get_module(module_name, class_name)
        if class_name in dir(module):
            try:
                # concrete_adapter_class = eval('module.%s' % class_name)
                # TODO stattdessen  verwenden:
                concrete_adapter_class = getattr(module, class_name)
            except Exception, exc:
                raise ConfigurationError(exc)
            self.__logger.debug("Registering concrete adapter %s" % (concrete_adapter_class))
            # TODO registering the adapter should be moved inside ConcreteAdapterRegistry
            self.__concrete_adapter_map.register_concrete_adapter(concrete_adapter_class, ignore_multiple=True)
        else:
            raise ConfigurationError("No class named %s in module %s" % (class_name, module_name))
        # wenn neue Module geladen wurden, müssen diese jetzt konfiguriert werden.
        while len(modules_loaded_previously) != len(set(sys.modules.itervalues())):
            modules_loaded_now = set(sys.modules.itervalues())
            new_modules = modules_loaded_now - modules_loaded_previously
            modules_loaded_previously = modules_loaded_now
            self.configure_modules(new_modules)

    def __load_class(self, concrete_module_name, concrete_type_name):
        self.__load_concrete_adapter(concrete_module_name, concrete_type_name)
        return sys.modules[concrete_module_name].__dict__[concrete_type_name]

    def configure_loaded_modules(self):
        # TODO find_config_variables verwenden
        self.__logger.debug("configuration map is %s" % (str(self.__concrete_adapter_map),))
        #self.__logger.debug("Performing configuration using registered concrete adapters: %s" % (self.__concrete_adapter_singletons))
        # iterator must be converted to a list, since sys.modules might be modified during configure_modules
        self.configure_modules(set(sys.modules.itervalues()))    

class InstanceConfigurator(object):
    """
    This is an implementation of a configurator (in fact, ObjectFactory) that does not modify global state,
    except for loading modules. 
    """
    
    def __init__(self, configuration):
        self.__logger = logging.getLogger(self.__module__)
        self.__configuration = dict(configuration) # TODO change this to a frozendict, but this doesn't work easily
        self.__concrete_adapter_map = ConcreteAdapterRegistry(name_map=self.__configuration, 
                                                              class_loader_func=self.__load_class,
                                                              ensure_configured_func=lambda x: None)
            
    # TODO the following methods have been copied from _ConfiguratorInternal, this should be unified!
    def __get_module(self, module_name, class_name):
        # TODO this could be extended in a way similar to http://code.activestate.com/recipes/159571-importing-any-file-without-modifying-syspath/
        # such that it allows the concurrent loading of different versions of modules with the same name.
        # sys.modules will probably still be modified, but it can be done in a way that is effectively
        # not-stateful. 
        
        # TODO is it necessary to pass and use class name here?
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            try:
                self.__logger.debug("Importing module %s (class=%s)" % (module_name, class_name))
                module = __import__(name=module_name, fromlist=[class_name])
            except ImportError, exc:
                raise ConfigurationError(exc)
        return module

    def __load_concrete_adapter(self, module_name, class_name):
        # TODO check first if the given adapter has already been loaded?
#        modules_loaded_previously = set(sys.modules.itervalues())
        module = self.__get_module(module_name, class_name)
        if class_name in dir(module):
            try:
                # concrete_adapter_class = eval('module.%s' % class_name)
                # TODO stattdessen  verwenden:
                concrete_adapter_class = getattr(module, class_name)
            except Exception, exc:
                raise ConfigurationError(exc)
            self.__logger.debug("Registering concrete adapter %s" % (concrete_adapter_class))
            # TODO registering the adapter should be moved inside ConcreteAdapterRegistry
            self.__concrete_adapter_map.register_concrete_adapter(concrete_adapter_class, ignore_multiple=True)
        else:
            raise ConfigurationError("No class named %s in module %s" % (class_name, module_name))
        # wenn neue Module geladen wurden, müssen diese jetzt konfiguriert werden.
#        while len(modules_loaded_previously) != len(set(sys.modules.itervalues())):
#            modules_loaded_now = set(sys.modules.itervalues())
#            new_modules = modules_loaded_now - modules_loaded_previously
#            modules_loaded_previously = modules_loaded_now
#            self.configure_modules(new_modules)

    def __load_class(self, concrete_module_name, concrete_type_name):
        self.__load_concrete_adapter(concrete_module_name, concrete_type_name)
        return sys.modules[concrete_module_name].__dict__[concrete_type_name]
    
    def create_factory(self, cls, **kwargs):
        return self.__concrete_adapter_map.create_factory(xxclsxx=cls, **kwargs)
    
    def create_instance(self, cls, *args, **kwargs):
        return self.__concrete_adapter_map.create_instance(xxclsxx=cls, *args, **kwargs)

    def get_concrete_adapter(self, cls_or_obj):
        return self.__concrete_adapter_map.get_concrete_adapter(cls_or_obj)

    
    def get_required_concrete_adapters(self, cls):
        # TODO the result currently contains any concrete autoconfigurables, even if there are explicit dependencies on them        
        collector = CollectingObjectFactory()
        dummy_concrete_adapter_map = ConcreteAdapterRegistry(name_map=dict(self.__configuration), 
                                                              class_loader_func=self.__load_class,
                                                              ensure_configured_func=lambda x: None,
                                                              sub_object_factory=collector)
        if ConfigTools.is_class_abstract_autoconfigurable(cls):
            factory = dummy_concrete_adapter_map.get_concrete_adapter(cls)
        else:
            factory = dummy_concrete_adapter_map.create_factory(xxclsxx=cls)
        factory()
        return (cls for cls in collector.get_dependencies() if ConfigTools.is_class_concrete_autoconfigurable(cls))
    
    
#    def create_factory_or_instance(self, cls, **kwargs):
#        if isinstance(cls, TypeType):
#            return self.create_factory(cls, **kwargs)
#        else:
#            return self.create_instance(cls, **kwargs)
    
class Configurator(object):
    """
    Provides a singleton instance of the _ConfiguratorInternal class. For documentation of its
    interface, see _ConfiguratorInternal.
    
    It is NOT possible to use multiple instances of _ConfiguratorInternal in parallel 
    (with different configurations) when using injection via module-level configuration variables,
    since the loaded module instances (which are singletons by definition) are modified.
    """
    # TODO 20120815 SGi add interface for _ConfiguratorInternal and do not refer to _ConfiguratorInternal in the documentation!

    # Uses singleton implementation from http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/
    # It is not possible to let Configurator inherit from the implemented interface, since the __getattr__ mechanism is only used
    # for members not defined by the object itself.   
    
    __instance = None

    def __init__(self):
        if Configurator.__instance == None:
            Configurator.__instance = _ConfiguratorInternal()
        self.__dict__['_Configurator__instance'] = Configurator.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
