"""Renderer for ColorBends background component."""
import json
from .base_renderer import BaseComponentRenderer


class ColorBendsRenderer(BaseComponentRenderer):
    """Handles rendering of ColorBends Vue component."""
    
    @property
    def component_type(self):
        return 'ColorBends'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render ColorBends as an actual Vue component.
        Based on Vue Bits API from ColorBendsDemo.vue
        """
        indent = "  "
        
        # Build component props array
        component_props = []
        
        # rotation: number (default: 0)
        rotation = node.get('props', {}).get('rotation', 0)
        component_props.append(f':rotation="{rotation}"')
        
        # autoRotate: boolean (default: false)
        auto_rotate = node.get('props', {}).get('autoRotate', False)
        component_props.append(f':auto-rotate="{str(auto_rotate).lower()}"')
        
        # speed: number (default: 0.001)
        speed = node.get('props', {}).get('speed', 0.001)
        component_props.append(f':speed="{speed}"')
        
        # colors: string[] (default: ['#667eea', '#764ba2', '#f093fb', '#4facfe'])
        colors = node.get('props', {}).get('colors', ['#667eea', '#764ba2', '#f093fb', '#4facfe'])
        if isinstance(colors, list):
            colors_str = json.dumps(colors)
            component_props.append(f':colors=\'{colors_str}\'')
        
        # scale: number (default: 1)
        scale = node.get('props', {}).get('scale', 1)
        component_props.append(f':scale="{scale}"')
        
        # frequency: number (default: 0.5)
        frequency = node.get('props', {}).get('frequency', 0.5)
        component_props.append(f':frequency="{frequency}"')
        
        # warpStrength: number (default: 2)
        warp_strength = node.get('props', {}).get('warpStrength', 2)
        component_props.append(f':warp-strength="{warp_strength}"')
        
        # mouseInfluence: number (default: 0.5)
        mouse_influence = node.get('props', {}).get('mouseInfluence', 0.5)
        component_props.append(f':mouse-influence="{mouse_influence}"')
        
        # parallax: boolean (default: false)
        parallax = node.get('props', {}).get('parallax', False)
        component_props.append(f':parallax="{str(parallax).lower()}"')
        
        # noise: number (default: 0)
        noise = node.get('props', {}).get('noise', 0)
        component_props.append(f':noise="{noise}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        return f"{indent}<ColorBends\n    {props_str}\n  />"
