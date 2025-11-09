"""Renderer for CardSwap (flip card) component."""
from .base_renderer import BaseComponentRenderer


class CardSwapRenderer(BaseComponentRenderer):
    """Handles rendering of CardSwap flip card components."""
    
    @property
    def component_type(self):
        return 'CardSwap'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render a CardSwap flip card component."""
        tag = node.get('props', {}).get('as', manifest['componentName'])
        indent = "  "
        
        width = node.get('props', {}).get('width', '300px')
        height = node.get('props', {}).get('height', '400px')
        duration = node.get('props', {}).get('duration', '0.6s')
        trigger = node.get('props', {}).get('trigger', 'hover')
        
        existing_style = props_map.get('style', '""').strip('"')
        container_style = f"width: {width}; height: {height}; perspective: 1000px"
        if existing_style:
            container_style = f"{existing_style}; {container_style}"
        props_map['style'] = f'"{container_style}"'
        
        # Add hover class if trigger is hover
        if trigger == 'hover':
            existing_class = props_map.get('class', '""').strip('"')
            props_map['class'] = f'"{existing_class} card-swap-hover"'
        
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        
        # Build flip card structure
        card_html = f'{indent}<{tag} {props_str}>\n'
        card_html += f'{indent}  <div class="card-swap-inner" style="position: relative; width: 100%; height: 100%; transition: transform {duration}; transform-style: preserve-3d;">\n'
        
        # Front side
        card_html += f'{indent}    <div class="card-swap-front" style="position: absolute; width: 100%; height: 100%; backface-visibility: hidden;">\n'
        if 'slots' in node and 'front' in node['slots']:
            for idx, child_node in enumerate(node['slots']['front']):
                card_html += context.generate_node(child_node, f"{semantic_id}.front", idx) + "\n"
        card_html += f'{indent}    </div>\n'
        
        # Back side
        card_html += f'{indent}    <div class="card-swap-back" style="position: absolute; width: 100%; height: 100%; backface-visibility: hidden; transform: rotateY(180deg);">\n'
        if 'slots' in node and 'back' in node['slots']:
            for idx, child_node in enumerate(node['slots']['back']):
                card_html += context.generate_node(child_node, f"{semantic_id}.back", idx) + "\n"
        card_html += f'{indent}    </div>\n'
        
        card_html += f'{indent}  </div>\n'
        card_html += f'{indent}</{tag}>'
        
        return card_html
