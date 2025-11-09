"""Renderer for CardNav component."""
from .base_renderer import BaseComponentRenderer


class CardNavRenderer(BaseComponentRenderer):
    """Handles rendering of CardNav components."""
    
    @property
    def component_type(self):
        return 'CardNav'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render a CardNav component."""
        tag = node.get('props', {}).get('as', manifest['componentName'])
        indent = "  "
        
        items = node.get('props', {}).get('items', [])
        card_style_variant = node.get('props', {}).get('cardStyle', 'elevated')
        
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        
        nav_html = f'{indent}<{tag} {props_str}>\n'
        
        for idx, item in enumerate(items):
            label = item.get('label', 'Nav Item')
            icon = item.get('icon', '')
            href = item.get('href', '#')
            
            # Apply card styling based on variant
            card_styles = {
                'elevated': 'background: #1a1a1a; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3); transition: transform 0.2s',
                'flat': 'background: #1a1a1a; padding: 1.5rem; border-radius: 12px',
                'outlined': 'background: transparent; border: 1px solid #333; padding: 1.5rem; border-radius: 12px',
                'glass': 'background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); padding: 1.5rem; border-radius: 12px'
            }
            
            card_style = card_styles.get(card_style_variant, card_styles['elevated'])
            
            nav_html += f'{indent}  <a href="{href}" data-component-id="{semantic_id}.item-{idx}" style="{card_style}; text-decoration: none; color: inherit; display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">\n'
            
            if icon:
                nav_html += f'{indent}    <span style="font-size: 24px;">{icon}</span>\n'
            
            nav_html += f'{indent}    <span style="font-weight: 600;">{label}</span>\n'
            nav_html += f'{indent}  </a>\n'
        
        # Add slot content
        if 'slots' in node and 'default' in node['slots']:
            for idx, child_node in enumerate(node['slots']['default']):
                nav_html += context.generate_node(child_node, semantic_id, idx) + "\n"
        
        nav_html += f'{indent}</{tag}>'
        
        return nav_html
