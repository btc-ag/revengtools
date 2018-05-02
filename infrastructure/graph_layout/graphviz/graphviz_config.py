# -*- coding: UTF-8 -*-
'''
Created on 03.11.2010

@author: SIGIESEC
'''
from commons.config_if import AutoConfigurable

# TODO das sind größtenteils Aspekte, die nicht spezifisch für Graphviz sind

class GraphvizConfiguration(AutoConfigurable):
    def get_arrowhead_factor(self):
        return 3
    
    def get_font(self):
        return "Arial"
    
    def get_font_scale(self):
        return .8

    def get_node_scale(self):
        return 0.5
    
    def get_aspect_ratio(self):
        """
        @deprecated: use get_rendering_configurations instead
        """
        return 0.5

    def get_output_format(self):
        """
        @deprecated: use get_rendering_configurations instead
        """
        return "pdf"
    
    def get_graphviz_bin_dir(self):
        raise NotImplementedError
    
    def get_rendering_configurations(self):
        # TODO das ist so eigentlich spezifisch für process_hudson
        # TODO Feinere Konfiguration, da landscape fuer fast alle focused on Graphen fehlschlaegt
        return (RenderingConfiguration(aspect_ratio='0.5', output_format='dot'),
                RenderingConfiguration(aspect_ratio='0', output_format='svg'),
                RenderingConfiguration(aspect_ratio='0.5', output_format='pdf', file_extension='.l.pdf'),
                RenderingConfiguration(aspect_ratio='2', output_format='pdf', file_extension='.p.pdf'),
                )

class RenderingConfiguration(object):
    def __init__(self, aspect_ratio, output_format, file_extension=None):
        self.__aspect_ratio = aspect_ratio
        self.__output_format = output_format
        if file_extension!=None:
            self.__file_extension = file_extension
        else:
            self.__file_extension = '.%s' % output_format

    def get_file_extension(self):
        return self.__file_extension

    def get_aspect_ratio(self):
        return self.__aspect_ratio

    def get_output_format(self):
        return self.__output_format

    aspect_ratio = property(get_aspect_ratio, None, None, None)
    output_format = property(get_output_format, None, None, None)
    file_extension = property(get_file_extension, None, None, None)

