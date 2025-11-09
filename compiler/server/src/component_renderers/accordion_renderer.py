"""Renderer for Accordion component."""
from .base_renderer import BaseComponentRenderer


class AccordionRenderer(BaseComponentRenderer):
    """Handles rendering of Accordion components with collapsible content."""
    
    @property
    def component_type(self):
        return 'Accordion'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render an Accordion component with header and collapsible content."""
        indent = "  "
        
        title = node.get('props', {}).get('title', 'Accordion')
        is_open_binding = None
        
        # Get state binding for isOpen
        if 'props' in node and 'isOpen' in node['props']:
            is_open_prop = node['props']['isOpen']
            if isinstance(is_open_prop, dict) and is_open_prop.get('type') == 'stateBinding':
                is_open_binding = is_open_prop.get('stateKey')
        
        # Generate header
        header_id = f"{semantic_id}-header"
        header_props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        
        header = f'{indent}<div {header_props_str}>\n'
        header += f'{indent}  <div data-component-id="{header_id}" data-nav-id="{header_id}" style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #1a1a1a; border-radius: 8px;">\n'
        header += f'{indent}    <span style="font-weight: 600; font-size: 18px;">{title}</span>\n'
        header += f'{indent}    <span v-if="{is_open_binding}" style="transition: transform 0.3s;">▼</span>\n'
        header += f'{indent}    <span v-else style="transition: transform 0.3s;">▶</span>\n'
        header += f'{indent}  </div>\n'
        
        # Generate content container
        content_id = f"{semantic_id}-content"
        children_str = ""
        if 'slots' in node and 'default' in node['slots']:
            for idx, child_node in enumerate(node['slots']['default']):
                children_str += context.generate_node(child_node, semantic_id, idx) + "\n"
        
        content = f'{indent}  <div v-if="{is_open_binding}" data-component-id="{content_id}" data-nav-id="{content_id}" style="padding: 1rem; margin-top: 0.5rem;">\n'
        content += children_str
        content += f'{indent}  </div>\n'
        
        header += content
        header += f'{indent}</div>'
        
        return header
