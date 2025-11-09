"""Renderer for MagicBento grid component."""
from .base_renderer import BaseComponentRenderer


class MagicBentoRenderer(BaseComponentRenderer):
    """Handles rendering of MagicBento Vue component."""
    
    @property
    def component_type(self):
        return 'MagicBento'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render MagicBento as an actual Vue component.
        Based on Vue Bits API from MagicBentoDemo.vue
        """
        indent = "  "
        
        # Build component props array
        component_props = []
        
        # enableStars: boolean (default: true)
        enable_stars = node.get('props', {}).get('enableStars', True)
        component_props.append(f':enable-stars="{str(enable_stars).lower()}"')
        
        # enableSpotlight: boolean (default: true)
        enable_spotlight = node.get('props', {}).get('enableSpotlight', True)
        component_props.append(f':enable-spotlight="{str(enable_spotlight).lower()}"')
        
        # spotlightRadius: number (default: 300)
        spotlight_radius = node.get('props', {}).get('spotlightRadius', 300)
        component_props.append(f':spotlight-radius="{spotlight_radius}"')
        
        # enableTilt: boolean (default: true)
        enable_tilt = node.get('props', {}).get('enableTilt', True)
        component_props.append(f':enable-tilt="{str(enable_tilt).lower()}"')
        
        # clickEffect: "ripple" | "none" | "highlight" (default: "ripple")
        click_effect = node.get('props', {}).get('clickEffect', 'ripple')
        component_props.append(f'click-effect="{click_effect}"')
        
        # enableMagnetism: boolean (default: false)
        enable_magnetism = node.get('props', {}).get('enableMagnetism', False)
        component_props.append(f':enable-magnetism="{str(enable_magnetism).lower()}"')
        
        # magnetismDistance: number (default: 100)
        magnetism_distance = node.get('props', {}).get('magnetismDistance', 100)
        component_props.append(f':magnetism-distance="{magnetism_distance}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        # MagicBento requires slot content
        children_str = ""
        if 'slots' in node and 'default' in node['slots']:
            for idx, child_node in enumerate(node['slots']['default']):
                child_output = context.generate_node(child_node, semantic_id, idx)
                children_str += f"    {child_output}\n"
        
        if children_str:
            return f"{indent}<MagicBento\n    {props_str}\n  >\n{children_str}  </MagicBento>"
        else:
            return f"{indent}<MagicBento\n    {props_str}\n  />"
