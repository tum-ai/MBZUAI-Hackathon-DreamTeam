"""Renderer for Squares background component."""
from .base_renderer import BaseComponentRenderer


class SquaresRenderer(BaseComponentRenderer):
    """Handles rendering of Squares Vue component."""
    
    @property
    def component_type(self):
        return 'Squares'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render Squares as an actual Vue component.
        Based on Vue Bits API from SquaresDemo.vue
        """
        indent = "  "
        
        # Build component props array
        component_props = []
        
        # direction: "diagonal" | "up" | "right" | "down" | "left" (default: "right")
        direction = node.get('props', {}).get('direction', 'right')
        component_props.append(f'direction="{direction}"')
        
        # speed: number (default: 1)
        speed = node.get('props', {}).get('speed', 1)
        component_props.append(f':speed="{speed}"')
        
        # borderColor: string (default: "#999")
        border_color = node.get('props', {}).get('borderColor', '#999')
        component_props.append(f'border-color="{border_color}"')
        
        # squareSize: number (default: 40)
        square_size = node.get('props', {}).get('squareSize', 40)
        component_props.append(f':square-size="{square_size}"')
        
        # hoverFillColor: string (default: "#222")
        hover_fill_color = node.get('props', {}).get('hoverFillColor', '#222')
        component_props.append(f'hover-fill-color="{hover_fill_color}"')
        
        # Add data attributes for navigation
        component_props.append(f'data-component-id="{semantic_id}"')
        component_props.append(f'data-nav-id="{semantic_id}"')
        
        props_str = "\n    ".join(component_props)
        
        return f"{indent}<Squares\n    {props_str}\n  />"
