"""Renderer for GradualBlur component."""
from .base_renderer import BaseComponentRenderer


class GradualBlurRenderer(BaseComponentRenderer):
    """Handles rendering of GradualBlur Vue component."""
    
    @property
    def component_type(self):
        return 'GradualBlur'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render GradualBlur as an actual Vue component.
        Based on Vue Bits API from GradualBlurDemo.vue
        """
        indent = "  "
        
        # Build component props array
        component_props = []
        
        # position: "top" | "bottom" | "left" | "right" (default: "bottom")
        position = node.get('props', {}).get('position', 'bottom')
        component_props.append(f'position="{position}"')
        
        # strength: number (default: 10)
        strength = node.get('props', {}).get('strength', 10)
        component_props.append(f':strength="{strength}"')
        
        # height: string (default: "200px")
        height = node.get('props', {}).get('height', '200px')
        component_props.append(f'height="{height}"')
        
        # divCount: number (default: 40)
        div_count = node.get('props', {}).get('divCount', 40)
        component_props.append(f':div-count="{div_count}"')
        
        # exponential: boolean (default: false)
        exponential = node.get('props', {}).get('exponential', False)
        component_props.append(f':exponential="{str(exponential).lower()}"')
        
        # curve: "linear" | "bezier" | "ease-in" (default: "linear")
        curve = node.get('props', {}).get('curve', 'linear')
        component_props.append(f'curve="{curve}"')
        
        # opacity: number (default: 1)
        opacity = node.get('props', {}).get('opacity', 1)
        component_props.append(f':opacity="{opacity}"')
        
        # target: "parent" | "page" (default: "parent")
        target = node.get('props', {}).get('target', 'parent')
        component_props.append(f'target="{target}"')
        
        # animated: boolean | "scroll" (default: false)
        animated = node.get('props', {}).get('animated', False)
        if isinstance(animated, bool):
            component_props.append(f':animated="{str(animated).lower()}"')
        else:
            component_props.append(f'animated="{animated}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        # GradualBlur can have slot content
        children_str = ""
        if 'slots' in node and 'default' in node['slots']:
            for idx, child_node in enumerate(node['slots']['default']):
                child_output = context.generate_node(child_node, semantic_id, idx)
                children_str += f"    {child_output}\n"
        
        if children_str:
            return f"{indent}<GradualBlur\n    {props_str}\n  >\n{children_str}  </GradualBlur>"
        else:
            return f"{indent}<GradualBlur\n    {props_str}\n  />"
