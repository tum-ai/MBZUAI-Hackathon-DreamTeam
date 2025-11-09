"""
Base class for all component renderers.
Each component renderer handles the logic for rendering a specific component type.
"""
from abc import ABC, abstractmethod


class BaseComponentRenderer(ABC):
    """Abstract base class for component renderers."""
    
    @property
    @abstractmethod
    def component_type(self):
        """Return the component type this renderer handles (e.g., 'List', 'Table')."""
        pass
    
    @abstractmethod
    def render(self, node, props_map, manifest, semantic_id, context):
        """
        Render the component to HTML string.
        
        Args:
            node: The AST node for this component
            props_map: Dictionary of processed props (includes data-nav-id, etc.)
            manifest: The component's manifest definition
            semantic_id: The semantic ID generated for this node
            context: Rendering context with helper methods
            
        Returns:
            str: The rendered HTML string
        """
        pass
    
    def can_render(self, node_type):
        """Check if this renderer can handle the given node type."""
        return node_type == self.component_type
