"""Renderer for BlurText component."""
from .base_renderer import BaseComponentRenderer


class BlurTextRenderer(BaseComponentRenderer):
    """Handles rendering of BlurText Vue component."""
    
    @property
    def component_type(self):
        return 'BlurText'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render BlurText as an actual Vue component.
        Based on Vue Bits API from BlurTextDemo.vue
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
        
        # Add delay (number, in ms)
        delay = node.get('props', {}).get('delay', 200)
        component_props.append(f':delay="{delay}"')
        
        # Add stepDuration (number, in seconds)
        step_duration = node.get('props', {}).get('stepDuration', 0.35)
        component_props.append(f':step-duration="{step_duration}"')
        
        # Add animateBy (string: 'words' or 'letters')
        animate_by = node.get('props', {}).get('animateBy', 'words')
        component_props.append(f'animate-by="{animate_by}"')
        
        # Add direction (string: 'top' or 'bottom')
        direction = node.get('props', {}).get('direction', 'top')
        component_props.append(f'direction="{direction}"')
        
        # Add threshold (number, 0-1)
        threshold = node.get('props', {}).get('threshold', 0.1)
        component_props.append(f':threshold="{threshold}"')
        
        # Add rootMargin (string)
        root_margin = node.get('props', {}).get('rootMargin', '0px')
        component_props.append(f'root-margin="{root_margin}"')
        
        # Add className if provided
        if 'class' in node.get('props', {}) or 'className' in node.get('props', {}):
            class_name = node['props'].get('className') or node['props'].get('class', '')
            if class_name:
                component_props.append(f'class-name="{class_name}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        return f"{indent}<BlurText\n    {props_str}\n  />"
