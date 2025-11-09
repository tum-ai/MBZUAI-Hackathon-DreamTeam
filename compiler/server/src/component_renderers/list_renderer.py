"""Renderer for List component."""
from .base_renderer import BaseComponentRenderer


class ListRenderer(BaseComponentRenderer):
    """Handles rendering of List components."""
    
    @property
    def component_type(self):
        return 'List'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render a List component with items and children."""
        tag = node.get('props', {}).get('as', manifest['componentName'])
        indent = "  "
        
        items_str = node.get('props', {}).get('items', [])
        li_tags = ""
        if items_str:
            # Auto-generate IDs for simple list items
            for idx, item in enumerate(items_str):
                item_id = f"{semantic_id}.item-{idx}"
                li_tags += f'{indent}  <li data-component-id="{item_id}" data-nav-id="{item_id}">{item}</li>\n'
        
        children_str = ""
        if 'slots' in node and 'default' in node['slots']:
            # Pass context for hierarchical IDs
            for idx, child_node in enumerate(node['slots']['default']):
                children_str += context.generate_node(child_node, semantic_id, idx) + "\n"
        
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        return f"{indent}<{tag} {props_str}>\n{li_tags}{children_str}{indent}</{tag}>"
