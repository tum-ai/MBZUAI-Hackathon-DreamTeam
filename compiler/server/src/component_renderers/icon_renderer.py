"""Renderer for Icon component."""
from .base_renderer import BaseComponentRenderer


class IconRenderer(BaseComponentRenderer):
    """Handles rendering of Icon components as SVG."""
    
    @property
    def component_type(self):
        return 'Icon'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render an Icon component as an SVG element."""
        indent = "  "
        
        # Extract the 'd' attribute for the SVG path
        path_d_attr = props_map.get('d', '""')
        
        # Remove 'd' from props_str to avoid duplicate
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items() if k != 'd'])
        
        return (
            f'{indent}<svg {props_str} fill="currentColor" width="1em" height="1em">\n'
            f'{indent}  <path d={path_d_attr}></path>\n'
            f'{indent}</svg>'
        )
