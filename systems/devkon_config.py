from infrastructure.graph_layout.graphviz.graphviz_config import GraphvizConfiguration, RenderingConfiguration

class DEVKONGraphvizConfiguration(GraphvizConfiguration):
    def get_font(self):
        return "Helvetica"
    
    def get_graphviz_bin_dir(self):
        return "/usr/local/bin"
    
    def get_rendering_configurations(self):
        return (RenderingConfiguration(aspect_ratio='0', output_format='svg'),
                #RenderingConfiguration(aspect_ratio='0.5', output_format='pdf', file_extension='.l.pdf'),
                #RenderingConfiguration(aspect_ratio='2', output_format='pdf', file_extension='.p.pdf'),
                )
                
