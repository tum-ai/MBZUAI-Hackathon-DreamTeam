"""Renderer for Plasma background component."""
from .base_renderer import BaseComponentRenderer


class PlasmaRenderer(BaseComponentRenderer):
    """Handles rendering of Plasma Vue component."""
    
    @property
    def component_type(self):
        return 'Plasma'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render Plasma as an actual Vue component.
        Based on Vue Bits API from PlasmaDemo.vue
        """
        indent = "  "
        
        # Build component props array
        component_props = []
        
        # color: string (default: '#8b5cf6')
        color = node.get('props', {}).get('color', '#8b5cf6')
        component_props.append(f'color="{color}"')
        
        # speed: number (default: 1)
        speed = node.get('props', {}).get('speed', 1)
        component_props.append(f':speed="{speed}"')
        
        # direction: number (default: 0)
        direction = node.get('props', {}).get('direction', 0)
        component_props.append(f':direction="{direction}"')
        
        # scale: number (default: 1)
        scale = node.get('props', {}).get('scale', 1)
        component_props.append(f':scale="{scale}"')
        
        # opacity: number (default: 0.5)
        opacity = node.get('props', {}).get('opacity', 0.5)
        component_props.append(f':opacity="{opacity}"')
        
        # mouseInteractive: boolean (default: false)
        mouse_interactive = node.get('props', {}).get('mouseInteractive', False)
        component_props.append(f':mouse-interactive="{str(mouse_interactive).lower()}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        return f"{indent}<Plasma\n    {props_str}\n  />"
