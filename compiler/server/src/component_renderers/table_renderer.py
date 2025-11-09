"""Renderer for Table component."""
from .base_renderer import BaseComponentRenderer


class TableRenderer(BaseComponentRenderer):
    """Handles rendering of Table components."""
    
    @property
    def component_type(self):
        return 'Table'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render a Table component with headers and rows."""
        tag = node.get('props', {}).get('as', manifest['componentName'])
        indent = "  "
        
        headers = node.get('props', {}).get('headers', [])
        rows = node.get('props', {}).get('rows', [])
        
        th_tags = "".join([f"<th>{h}</th>" for h in headers])
        tr_tags = ""
        for row in rows:
            td_tags = "".join([f"<td>{cell}</td>" for cell in row])
            tr_tags += f"{indent}  <tr>{td_tags}</tr>\n"
        
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        return (
            f"{indent}<{tag} {props_str}>\n"
            f"{indent}  <thead>\n{indent}    <tr>{th_tags}</tr>\n{indent}  </thead>\n"
            f"{indent}  <tbody>\n{tr_tags}{indent}  </tbody>\n"
            f"{indent}</{tag}>"
        )
