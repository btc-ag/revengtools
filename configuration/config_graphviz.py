'''
Created on 06.09.2010

@author: SIGIESEC
'''
from base.basic_config_if import BasicConfig
from configuration.config_base import RevEngToolsBasicConfig
from configuration.revengtools_config import RevEngToolsConfigParser
from infrastructure.graph_layout.graphviz.graphviz_config import (
    GraphvizConfiguration)
import os.path

config_basic = BasicConfig()

class RevEngToolsGraphvizConfiguration(GraphvizConfiguration):
    def __init__(self):
        GraphvizConfiguration.__init__(self)
        self.__adaptee = RevEngToolsConfigParser()
        self.__adaptee.load_config("graphStyle.config")
    
    def get_arrowhead_factor(self):
        return float(self.__adaptee.get("ARROWHEADFACTOR", GraphvizConfiguration.get_arrowhead_factor(self)))

    def get_font(self):
        return self.__adaptee.get("FONTNAME", GraphvizConfiguration.get_font(self))
    
    def get_font_scale(self):
        return float(self.__adaptee.get("FONTSCALE", str(GraphvizConfiguration.get_font_scale(self))))
    
    def get_output_format(self):
        return self.__adaptee.get("IMGTYPE", GraphvizConfiguration.get_output_format(self))
    
    def get_aspect_ratio(self):
        return float(self.__adaptee.get("RATIO", str(GraphvizConfiguration.get_aspect_ratio(self))))
    
    def get_graphviz_bin_dir(self):
        return RevEngToolsBasicConfig.get_path(self.__adaptee, "GRAPHVIZ_BIN_DIR", os.path.join(config_basic.get_revengtools_basedir(), "graphviz", "bin"))

