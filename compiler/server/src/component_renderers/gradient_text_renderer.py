"""Renderer for GradientText component."""
import json
from .base_renderer import BaseComponentRenderer


class GradientTextRenderer(BaseComponentRenderer):
    """Handles rendering of GradientText Vue component."""
    
    @property
    def component_type(self):
        return 'GradientText'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render GradientText as an actual Vue component.
        Based on Vue Bits API from GradientTextDemo.vue
        """
        indent = "  "
        
        # Get text content (required)
        text = node.get('props', {}).get('text') or node.get('props', {}).get('content', '')
        
        # Build component props array
        component_props = []
        
        # Add text prop
        if isinstance(text, str):
            component_props.append(f'text="{text}"')
        elif isinstance(text, dict) and text.get('type') == 'expression':
            resolved_text, _ = context.resolve_expression(text, is_event_handler=False)
            cleaned_text = resolved_text.strip('"')
            component_props.append(f':text="{cleaned_text}"')        
        # Add colors array
        colors = node.get('props', {}).get('colors', ['#ffaa40', '#9c40ff', '#ffaa40'])
        if isinstance(colors, list):
            colors_str = json.dumps(colors)
            component_props.append(f":colors='{colors_str}'")
        
        # Add animationSpeed (number, in seconds)
        animation_speed = node.get('props', {}).get('animationSpeed', 8)
        component_props.append(f':animation-speed="{animation_speed}"')
        
        # Add showBorder (boolean)
        show_border = node.get('props', {}).get('showBorder', False)
        component_props.append(f':show-border="{str(show_border).lower()}"')
        
        # Add className if provided
        if 'class' in node.get('props', {}) or 'className' in node.get('props', {}):
            class_name = node['props'].get('className') or node['props'].get('class', '')
            if class_name:
                component_props.append(f'class-name="{class_name}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        return f"{indent}<GradientText\n    {props_str}\n  />"
