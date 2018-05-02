# -*- coding: UTF-8 -*-

from commons.configurator import Configurator
from configuration.revengtools_config import RevEngToolsConfigParser
import os.path
import logging.config

# configure logging
logging.config.fileConfig(os.path.join(RevEngToolsConfigParser().revengtools_basepath(), "configuration", "logging.conf"))

# TODO das sollte noch etwas ausgeklügelter funktionieren, mit Sub-Technologien 
# (z.B. cpp.msvc vs. cpp.cmake u.ä.) bzw. Kombinationen von Technologien (cast+cpp vs. cdep+cpp)

# TODO Sicherstellen, dass spätere autowire-Konfigurationsdateien frühere Mappings überschreiben 

config_parser = RevEngToolsConfigParser()

# technology-specific config
Configurator().get_autowire_config_finder().add_autowire_config_in("autowire.config.%s" % (RevEngToolsConfigParser().get("LANGUAGE"),))


# system-specific config
Configurator().get_autowire_config_finder().add_autowire_config_in("autowire.config.%s" % (RevEngToolsConfigParser().get("SYSTEM"),))

if config_parser.has("FLAVORS"):
    flavors = config_parser.get("FLAVORS").split(",")
    Configurator().get_autowire_config_finder().add_flavors(flavors)
