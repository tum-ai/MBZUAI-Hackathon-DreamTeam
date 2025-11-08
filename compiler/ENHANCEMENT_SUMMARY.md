# Enhancement Summary - Semantic IDs & Advanced Components

## Overview

This document summarizes the enhancements made to the MBZUAI-Hackathon DreamTeam project to support:
1. **Semantic, hierarchical ID generation** for better LLM understanding
2. **Advanced component support** (variants, animations) to prepare for reactbits/vuebits integration

## 1. Semantic ID System (V20)

### What Changed

**File: `compiler/server/src/vue_generator.py`**

#### New Features:
- Added `_generate_semantic_id()` method that creates hierarchical, meaningful IDs
- Added `_extract_semantic_hint()` to extract semantic meaning from component props
- Modified `_generate_node()` to accept `parent_context` and `index_in_parent` parameters
- Updated all recursive calls to pass context down the tree

#### ID Format:
```
parent-context.component-type[-semantic-hint][-index]
```

#### Examples:
```
Original ID (user-provided):  "hero-section"
Generated hierarchy:          "hero-section.box.hero-title.0"

Original ID:                  "feature-list" 
Generated for list items:     "feature-list.item-0"
                              "feature-list.item-1"
                              "feature-list.item-2"

Original ID:                  "contact-form"
Generated for children:       "contact-form.textbox.email-input"
                              "contact-form.button.submit"
```

### Benefits for LLM:
- **Hierarchy Understanding**: IDs show parent-child relationships (e.g., `navigation.menu.link-home`)
- **Type Identification**: Component type is embedded in ID (e.g., `.button`, `.textbox`)
- **Semantic Meaning**: Content hints help identify purpose (e.g., `.email-input`, `.submit-btn`)
- **Position Tracking**: Index numbers help with collections (e.g., `.item-0`, `.item-1`)

### List Component Enhancement:
- Simple list items (from `items` array) now get auto-generated IDs: `list-id.item-0`, `list-id.item-1`, etc.
- Complex list items (from slots) use the normal hierarchical ID system

## 2. Advanced Component System

### Enhanced Manifest Schema (V2.0)

**File: `compiler/manifests/MANIFEST_SCHEMA.md`**

New manifest fields:
- **`variants`**: Predefined style presets (e.g., "elevated", "outlined", "glow")
- **`animations`**: Animation type definitions and controlling props
- **`composition`**: Template patterns for complex nested components
- **`description`**: Human-readable descriptions for LLM understanding
- **`enum`**: Allowed values for props (helps validation)

### New Components Created:

#### 1. Card Component
**File: `compiler/manifests/Card.manifest.json`**

Variants:
- `default`: Standard card with subtle shadow
- `elevated`: Prominent shadow for emphasis
- `outlined`: Border, no shadow
- `flat`: Background only

Usage:
```json
{
  "id": "feature-card",
  "type": "Card",
  "props": {
    "variant": "elevated"
  }
}
```

#### 2. GradientText Component
**File: `compiler/manifests/GradientText.manifest.json`**

Features:
- Animated gradient backgrounds
- Multiple preset variants (sunset, ocean, neon, purple-haze)
- Customizable colors and animation duration

Usage:
```json
{
  "id": "hero-title",
  "type": "GradientText",
  "props": {
    "content": "Welcome",
    "as": "h1",
    "variant": "sunset"
  }
}
```

Generator support:
- Automatically applies gradient CSS
- Handles animation keyframes
- Supports text clipping for gradient effect

#### 3. Accordion Component
**File: `compiler/manifests/Accordion.manifest.json`**

Features:
- Collapsible content sections
- State-driven open/close
- Automatic header generation

Usage:
```json
{
  "id": "faq-item",
  "type": "Accordion",
  "props": {
    "title": "Question here?",
    "isOpen": {
      "type": "stateBinding",
      "stateKey": "faqOpen"
    }
  }
}
```

### Generator Enhancements

**File: `compiler/server/src/vue_generator.py`**

#### Variant Support:
- Added variant processing before prop handling
- Merges variant styles with node-specific styles
- Node styles take precedence over variant styles

#### Special Component Handlers:
- `GradientText`: Generates gradient CSS with optional animation
- `Accordion`: Creates header + collapsible content structure
- `Card`: Applies variant styles automatically

**File: `compiler/server/src/project_generator.py`**

- Added CSS animations (gradient-shift keyframe) to App.vue
- Ensures all advanced components have required styles

## 3. LLM Prompt Updates

**File: `compiler/server/prompt.md`**

### Updated Guidelines:
- New section on semantic ID requirements
- Examples showing proper ID naming conventions
- Documentation of new components (Card, GradientText, Accordion)
- Example showing hierarchical ID generation in practice

### New Example (Example 3):
Shows how to create a features section with semantic IDs:
- Main container: `features-section`
- Title: `features-title`
- Grid: `features-grid`
- Cards: `feature-speed`, `feature-quality`, `feature-support`

The LLM now understands:
- IDs should be descriptive, not generic
- Use kebab-case
- Keep IDs concise (2-3 words)
- Describe purpose, not just type

## 4. Test Files

### Test AST
**File: `compiler/server/inputs/test-enhanced.json`**

Demonstrates:
- Semantic IDs throughout hierarchy
- GradientText with variant
- Card components with elevated variant
- List with auto-ID generation
- Accordion with state binding
- Nested structure with meaningful IDs

## Migration Guide

### For Existing ASTs:
1. No breaking changes - old IDs still work
2. System will generate hierarchical IDs automatically
3. Consider updating manually-assigned IDs to be more semantic

### For Adding New Components:
1. Create a manifest.json file
2. Include `variants` if component has preset styles
3. Add `description` fields for LLM guidance
4. If custom rendering needed, add handler to `_generate_node()` in vue_generator.py

### For LLM Integration:
1. The prompt.md now includes all component documentation
2. LLM will automatically use semantic IDs
3. Variants simplify LLM decision-making (no need to specify all styles)

## Next Steps

### Immediate:
1. ✅ Test the enhanced system with test-enhanced.json
2. Run the generator and verify output
3. Check that IDs are hierarchical and semantic

### Future Enhancements:
1. Add more vuebits-inspired components:
   - AnimatedButton (with hover effects)
   - ParticleBackground
   - GlowingBorder
   - TextReveal
   - ScrollProgress
   
2. Enhance variant system:
   - Allow combining multiple variants
   - Add theme variants (dark/light)
   
3. Animation library:
   - More animation presets
   - Transition timing controls
   - Custom easing functions

4. Composition patterns:
   - Form builder patterns
   - Layout templates
   - Navigation patterns

## Technical Notes

### ID Generation Algorithm:
```python
def _generate_semantic_id(node, parent_context, index):
    # 1. Check if node has existing ID
    # 2. Extract semantic hint from props (content, text, etc.)
    # 3. Build parts: [parent, type, hint, index]
    # 4. Join with dots: "parent.type.hint.index"
    # 5. Ensure uniqueness with counter
```

### Variant Processing:
```python
# 1. Check if node has variant prop
# 2. Look up variant in manifest
# 3. Extract variant props (especially styles)
# 4. Merge with node props (node takes precedence)
# 5. Apply to component
```

### Why This Matters:
- **Debugging**: Easier to identify components in DOM
- **Automation**: Browser automation can target semantic IDs
- **LLM Understanding**: LLM can "see" the structure and make better decisions
- **Maintenance**: Developers can quickly understand component purpose
- **Scaling**: Adding new components is now simple and consistent
