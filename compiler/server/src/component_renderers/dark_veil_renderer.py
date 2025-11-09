"""Renderer for DarkVeil overlay component."""
from .base_renderer import BaseComponentRenderer


class DarkVeilRenderer(BaseComponentRenderer):
    """Handles rendering of DarkVeil Vue component."""
    
    @property
    def component_type(self):
        return 'DarkVeil'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render DarkVeil as an actual Vue component.
        Based on Vue Bits API from DarkVeilDemo.vue
        """
        indent = "  "
        
        # Build component props array
        component_props = []
        
        # hueShift: number (default: 0)
        hue_shift = node.get('props', {}).get('hueShift', 0)
        component_props.append(f':hue-shift="{hue_shift}"')
        
        # noiseIntensity: number (default: 0)
        noise_intensity = node.get('props', {}).get('noiseIntensity', 0)
        component_props.append(f':noise-intensity="{noise_intensity}"')
        
        # scanlineIntensity: number (default: 0)
        scanline_intensity = node.get('props', {}).get('scanlineIntensity', 0)
        component_props.append(f':scanline-intensity="{scanline_intensity}"')
        
        # speed: number (default: 0.5)
        speed = node.get('props', {}).get('speed', 0.5)
        component_props.append(f':speed="{speed}"')
        
        # scanlineFrequency: number (default: 0)
        scanline_frequency = node.get('props', {}).get('scanlineFrequency', 0)
        component_props.append(f':scanline-frequency="{scanline_frequency}"')
        
        # warpAmount: number (default: 0)
        warp_amount = node.get('props', {}).get('warpAmount', 0)
        component_props.append(f':warp-amount="{warp_amount}"')
        
        # resolutionScale: number (default: 1)
        resolution_scale = node.get('props', {}).get('resolutionScale', 1)
        component_props.append(f':resolution-scale="{resolution_scale}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        return f"{indent}<DarkVeil\n    {props_str}\n  />"
