"""Renderer for Ribbons background component."""
import json
from .base_renderer import BaseComponentRenderer


class RibbonsRenderer(BaseComponentRenderer):
    """Handles rendering of Ribbons Vue component."""
    
    @property
    def component_type(self):
        return 'Ribbons'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render Ribbons as an actual Vue component.
        Based on Vue Bits API from RibbonsDemo.vue
        """
        indent = "  "
        
        # Build component props array
        component_props = []
        
        # colors: string[] (required)
        colors = node.get('props', {}).get('colors', ['#ff6b6b', '#4ecdc4', '#45b7d1'])
        if isinstance(colors, list):
            colors_str = json.dumps(colors)
            component_props.append(f':colors=\'{colors_str}\'')
        
        # baseThickness: number (default: 30)
        base_thickness = node.get('props', {}).get('baseThickness', 30)
        component_props.append(f':base-thickness="{base_thickness}"')
        
        # speedMultiplier: number (default: 0.5)
        speed_multiplier = node.get('props', {}).get('speedMultiplier', 0.5)
        component_props.append(f':speed-multiplier="{speed_multiplier}"')
        
        # maxAge: number (default: 500)
        max_age = node.get('props', {}).get('maxAge', 500)
        component_props.append(f':max-age="{max_age}"')
        
        # enableFade: boolean (default: true)
        enable_fade = node.get('props', {}).get('enableFade', True)
        component_props.append(f':enable-fade="{str(enable_fade).lower()}"')
        
        # enableShaderEffect: boolean (default: true)
        enable_shader = node.get('props', {}).get('enableShaderEffect', True)
        component_props.append(f':enable-shader-effect="{str(enable_shader).lower()}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        return f"{indent}<Ribbons\n    {props_str}\n  />"
