# Component Renderers Architecture

This directory contains the refactored component rendering logic for the Vue Generator. Each component type has its own dedicated renderer class, making the codebase more maintainable and scalable.

## Structure

```
component_renderers/
├── __init__.py                  # Auto-imports all renderers & provides registry
├── base_renderer.py             # Abstract base class for all renderers
├── list_renderer.py             # Renderer for List component
├── table_renderer.py            # Renderer for Table component
├── icon_renderer.py             # Renderer for Icon component
├── gradient_text_renderer.py   # Renderer for GradientText component
├── accordion_renderer.py        # Renderer for Accordion component
├── blur_text_renderer.py        # Renderer for BlurText component
├── gradual_blur_renderer.py    # Renderer for GradualBlur component
├── ribbons_renderer.py          # Renderer for Ribbons background
├── color_bends_renderer.py      # Renderer for ColorBends background
├── plasma_renderer.py           # Renderer for Plasma background
├── squares_renderer.py          # Renderer for Squares background
├── dark_veil_renderer.py        # Renderer for DarkVeil overlay
├── profile_card_renderer.py    # Renderer for ProfileCard component
├── stepper_renderer.py          # Renderer for Stepper component
├── card_swap_renderer.py        # Renderer for CardSwap flip card
├── card_nav_renderer.py         # Renderer for CardNav component
└── magic_bento_renderer.py      # Renderer for MagicBento grid
```

## Benefits

1. **Maintainability**: Each component's rendering logic is isolated in its own file
2. **Scalability**: Adding new components is as simple as creating a new renderer file
3. **Readability**: The main `vue_generator.py` went from 1047 lines to 481 lines
4. **Testability**: Individual component renderers can be tested independently
5. **Reusability**: Renderers follow a consistent interface defined by `BaseComponentRenderer`

## How It Works

### 1. Base Renderer Class

All component renderers inherit from `BaseComponentRenderer`:

```python
from .base_renderer import BaseComponentRenderer

class MyComponentRenderer(BaseComponentRenderer):
    @property
    def component_type(self):
        return 'MyComponent'  # The component type this renderer handles
    
    def render(self, node, props_map, manifest, semantic_id, context):
        # Implementation here
        return html_string
```

### 2. Render Context

The `RenderContext` object provides access to helper methods from the main `VueGenerator`:

- `context.generate_node(node, parent_context, index)` - Recursively render child nodes
- `context.resolve_expression(expr, is_event_handler)` - Resolve Vue expressions
- `context.generate_style_string(style_obj)` - Convert style objects to CSS strings

### 3. Automatic Registration

The `__init__.py` file automatically imports and registers all renderers:

```python
from .component_renderers import get_renderer_for_component

# Usage in VueGenerator
renderer = get_renderer_for_component(node_type)
if renderer:
    return renderer.render(node, props_map, manifest, semantic_id, context)
```

## Adding a New Component Renderer

1. **Create a new file** in this directory (e.g., `my_component_renderer.py`)

2. **Implement the renderer class**:

```python
"""Renderer for MyComponent."""
from .base_renderer import BaseComponentRenderer


class MyComponentRenderer(BaseComponentRenderer):
    """Handles rendering of MyComponent."""
    
    @property
    def component_type(self):
        return 'MyComponent'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render MyComponent to HTML."""
        tag = node.get('props', {}).get('as', manifest['componentName'])
        indent = "  "
        
        # Your rendering logic here
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        
        # Handle children if needed
        children_str = ""
        if 'slots' in node and 'default' in node['slots']:
            for idx, child_node in enumerate(node['slots']['default']):
                children_str += context.generate_node(child_node, semantic_id, idx) + "\n"
        
        return f"{indent}<{tag} {props_str}>\n{children_str}{indent}</{tag}>"
```

3. **Register in `__init__.py`**:

```python
# Add import
from .my_component_renderer import MyComponentRenderer

# Add to COMPONENT_RENDERERS list
COMPONENT_RENDERERS = [
    # ... existing renderers ...
    MyComponentRenderer(),
]

# Add to __all__
__all__ = [
    # ... existing exports ...
    'MyComponentRenderer',
]
```

That's it! Your new component renderer will automatically be used by the VueGenerator.

## Component Renderer Examples

### Simple Component (Text, Button)
Uses default rendering path in `vue_generator.py` - no custom renderer needed.

### List Component
Custom renderer that generates `<li>` elements for items and handles child slots.

### Icon Component  
Renders as SVG with path data from props.

### Accordion Component
Complex component with multiple slots (header, content) and state binding.

### Background Effects (Ribbons, Plasma, ColorBends)
Generate multiple child elements for visual effects.

## Testing

To test an individual component renderer:

```python
from src.component_renderers import get_renderer_for_component
from src.vue_generator import VueGenerator, RenderContext

# Setup
gen = VueGenerator('manifests/')
context = RenderContext(gen)
renderer = get_renderer_for_component('List')

# Create test node
node = {
    'type': 'List',
    'props': {'items': ['A', 'B', 'C']},
    'slots': {}
}

# Test render
result = renderer.render(node, {}, manifest, 'test-list', context)
print(result)
```

## Migration Notes

The refactoring reduced `vue_generator.py` from **1047 lines to 481 lines** (54% reduction) by extracting all component-specific rendering logic into individual renderer classes. The main generator now focuses on:

- Loading manifests
- Managing state and functions  
- Handling generic props (id, class, style, events)
- Processing expressions
- Generating semantic IDs
- Coordinating the overall Vue file generation

All component-specific rendering logic has been moved to dedicated renderer classes, making the codebase much more maintainable.
