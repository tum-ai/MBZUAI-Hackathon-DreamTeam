"""Renderer for ProfileCard component."""
from .base_renderer import BaseComponentRenderer


class ProfileCardRenderer(BaseComponentRenderer):
    """Handles rendering of ProfileCard components."""
    
    @property
    def component_type(self):
        return 'ProfileCard'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render a ProfileCard component."""
        tag = node.get('props', {}).get('as', manifest['componentName'])
        indent = "  "
        
        name = node.get('props', {}).get('name', 'Name')
        title = node.get('props', {}).get('title', '')
        bio = node.get('props', {}).get('bio', '')
        avatar_url = node.get('props', {}).get('avatarUrl', '')
        variant = node.get('props', {}).get('variant', 'default')
        border_radius = node.get('props', {}).get('borderRadius', '16px')
        
        # Apply variant styling
        variant_styles = {
            'default': f'background: #1a1a1a; border-radius: {border_radius}; padding: 2rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3)',
            'minimal': f'background: transparent; border: 1px solid #333; border-radius: 12px; padding: 1.5rem',
            'detailed': f'background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); border-radius: 20px; padding: 2.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4)',
            'glass': f'background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4)'
        }
        
        # Merge variant style with existing style
        existing_style = props_map.get('style', '""').strip('"')
        variant_style = variant_styles.get(variant, variant_styles['default'])
        if existing_style:
            combined_style = f"{variant_style}; {existing_style}"
        else:
            combined_style = variant_style
        props_map['style'] = f'"{combined_style}"'
        
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        
        # Build profile card HTML
        card_html = f'{indent}<{tag} {props_str}>\n'
        
        if avatar_url:
            card_html += f'{indent}  <div style="text-align: center; margin-bottom: 1.5rem;">\n'
            card_html += f'{indent}    <img src="{avatar_url}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;" />\n'
            card_html += f'{indent}  </div>\n'
        
        card_html += f'{indent}  <div style="text-align: center;">\n'
        card_html += f'{indent}    <h3 style="font-size: 24px; font-weight: bold; margin-bottom: 0.5rem;">{name}</h3>\n'
        
        if title:
            card_html += f'{indent}    <p style="color: #888; margin-bottom: 1rem;">{title}</p>\n'
        
        if bio:
            card_html += f'{indent}    <p style="color: #aaa; line-height: 1.6;">{bio}</p>\n'
        
        card_html += f'{indent}  </div>\n'
        
        # Add slots for socials and actions
        if 'slots' in node and 'socials' in node['slots']:
            card_html += f'{indent}  <div style="margin-top: 1.5rem;">\n'
            for idx, child_node in enumerate(node['slots']['socials']):
                card_html += context.generate_node(child_node, f"{semantic_id}.socials", idx) + "\n"
            card_html += f'{indent}  </div>\n'
        
        if 'slots' in node and 'actions' in node['slots']:
            card_html += f'{indent}  <div style="margin-top: 1rem;">\n'
            for idx, child_node in enumerate(node['slots']['actions']):
                card_html += context.generate_node(child_node, f"{semantic_id}.actions", idx) + "\n"
            card_html += f'{indent}  </div>\n'
        
        card_html += f'{indent}</{tag}>'
        
        return card_html
