# Enhanced Component Manifest Schema v2.0

## Overview

This document describes the enhanced manifest schema that supports complex components including those from libraries like Vue Bits / React Bits.

## Core Schema

```json
{
  "componentName": "string",      // HTML tag or component name
  "friendlyName": "string",       // Human-readable name for LLM
  "module": "string",             // Optional: import path
  "description": "string",        // Optional: What this component does
  
  "props": {
    "propName": {
      "type": "string|number|boolean|array|object",
      "default": "any",           // Optional: default value
      "description": "string",    // Optional: what this prop does
      "required": false,          // Optional: is this required?
      "enum": ["value1", "value2"] // Optional: allowed values
    }
  },
  
  "slots": ["default", "header", "footer"],  // Slot names
  
  "events": ["click", "input", "change"],    // Supported events
  
  "variants": {                   // NEW: Predefined component styles/types
    "variantName": {
      "description": "string",
      "props": {
        "propName": "value"      // Props to apply for this variant
      }
    }
  },
  
  "animations": {                 // NEW: Animation support
    "animationType": {
      "description": "string",
      "props": ["prop1", "prop2"] // Props that control this animation
    }
  },
  
  "composition": {                // NEW: For complex nested components
    "template": "string",         // Template structure
    "requiredChildren": ["type1", "type2"]
  }
}
```

## Basic Example: Button

```json
{
  "componentName": "button",
  "friendlyName": "Button",
  "description": "A clickable button element",
  "props": {
    "text": {
      "type": "string",
      "description": "Button text content"
    },
    "style": {
      "type": "object"
    },
    "class": {
      "type": "string"
    },
    "id": {
      "type": "string"
    },
    "disabled": {
      "type": "boolean",
      "default": false
    }
  },
  "slots": ["default"],
  "events": ["click", "focus", "blur"]
}
```

## Advanced Example: AnimatedCard (Vue Bits style)

```json
{
  "componentName": "div",
  "friendlyName": "AnimatedCard",
  "description": "A card with hover animations and optional glow effects",
  "props": {
    "style": {
      "type": "object"
    },
    "class": {
      "type": "string"
    },
    "id": {
      "type": "string"
    },
    "variant": {
      "type": "string",
      "enum": ["default", "glow", "lift", "tilt"],
      "default": "default",
      "description": "Animation style for the card"
    },
    "glowColor": {
      "type": "string",
      "default": "#3b82f6",
      "description": "Color of the glow effect"
    },
    "borderRadius": {
      "type": "string",
      "default": "12px"
    },
    "padding": {
      "type": "string",
      "default": "2rem"
    }
  },
  "slots": ["default", "header", "footer"],
  "events": ["click", "mouseenter", "mouseleave"],
  "variants": {
    "default": {
      "description": "Simple card with subtle hover",
      "props": {
        "style": {
          "transition": "transform 0.3s ease"
        }
      }
    },
    "glow": {
      "description": "Card with glowing border on hover",
      "props": {
        "style": {
          "transition": "all 0.3s ease",
          "boxShadow": "0 0 20px var(--glow-color)"
        }
      }
    },
    "lift": {
      "description": "Card lifts up on hover",
      "props": {
        "style": {
          "transition": "transform 0.3s ease, box-shadow 0.3s ease",
          "transform": "translateY(-8px)"
        }
      }
    }
  },
  "animations": {
    "hover": {
      "description": "Hover animation",
      "props": ["variant", "glowColor"]
    }
  }
}
```

## Guidelines for Creating Manifests

### 1. Component Naming
- `componentName`: Use the actual HTML tag or Vue component name
- `friendlyName`: Use a clear, descriptive name the LLM can understand

### 2. Props
- Always include: `style`, `class`, `id` for maximum flexibility
- Add `description` for complex props to help the LLM understand usage
- Use `enum` for props with limited options (helps validation)
- Set sensible `default` values

### 3. Variants
- Create variants for common use cases (reduces LLM complexity)
- Each variant should have clear `props` overrides
- Variants help LLM generate consistent, good-looking components

### 4. Animations
- Document animation types the component supports
- List props that control animations
- This helps LLM understand how to create dynamic UIs

### 5. Composition
- For complex components that require specific child structures
- Define template patterns
- List required children types

## Migration from v1.0

Old manifests (v1.0) are fully compatible. New fields are optional:
- Add `variants` for preset styles
- Add `animations` for animated components
- Add `composition` for complex nested components
- Add `description` fields for better LLM understanding
