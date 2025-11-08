# Quick Start Guide - Enhanced System

## What's New

### 1. Semantic IDs
IDs now show hierarchy and meaning:
```
Old: "btn-1", "text-2"
New: "hero-section.button.get-started", "features-grid.item-0"
```

### 2. Advanced Components
Three new components ready to use:
- **Card**: with variants (elevated, outlined, flat)
- **GradientText**: animated gradient text effects
- **Accordion**: collapsible content sections

### 3. Component Variants
Use presets instead of styling everything:
```json
{
  "type": "Card",
  "props": {
    "variant": "elevated"
  }
}
```

## Usage Examples

### Creating a Feature Card
```json
{
  "id": "feature-speed",
  "type": "Card",
  "props": {
    "variant": "elevated"
  },
  "slots": {
    "default": [
      {
        "id": "title",
        "type": "Text",
        "props": {
          "content": "Lightning Fast",
          "as": "h3"
        }
      }
    ]
  }
}
```

### Using Gradient Text
```json
{
  "id": "hero-title",
  "type": "GradientText",
  "props": {
    "content": "Welcome to the Future",
    "as": "h1",
    "variant": "sunset",
    "animated": true
  }
}
```

### Creating an Accordion
```json
{
  "id": "faq-item",
  "type": "Accordion",
  "props": {
    "title": "What is this?",
    "isOpen": {
      "type": "stateBinding",
      "stateKey": "faqOpen"
    }
  },
  "slots": {
    "default": [
      {
        "id": "answer",
        "type": "Text",
        "props": {
          "content": "This is the answer..."
        }
      }
    ]
  },
  "events": {
    "click": [
      {
        "type": "action:setState",
        "stateKey": "faqOpen",
        "newValue": {
          "type": "expression",
          "value": "!${state.faqOpen}"
        }
      }
    ]
  }
}
```

## ID Naming Guidelines

### ✅ Good IDs
- `hero-section` - clear purpose
- `contact-form` - describes function
- `feature-list` - semantic meaning
- `nav-menu` - concise and clear

### ❌ Bad IDs
- `box-1` - too generic
- `container-a` - no meaning
- `div-wrapper-thing` - too verbose
- `x` - not descriptive

## Testing Your Changes

1. Add your AST to `compiler/server/inputs/your-file.json`
2. Update `compiler/server/project.json` to reference it
3. Run the generator: `python compiler/server/src/project_generator.py`
4. Check output in `compiler/output/my-new-site/`
5. Inspect generated HTML for semantic IDs

## Adding New Components

1. Create `NewComponent.manifest.json` in `compiler/manifests/`
2. Follow the schema in `MANIFEST_SCHEMA.md`
3. Add variants if component has presets
4. If special rendering needed, add handler in `vue_generator.py`
5. Document in `prompt.md` for LLM

## Troubleshooting

### IDs not hierarchical?
- Check that you're passing `parent_context` in recursive calls
- Verify `_generate_semantic_id()` is being called

### Variant not applying?
- Confirm variant name exists in manifest
- Check that styles are in `manifest.variants[name].props.style`
- Ensure variant processing happens before other props

### Component not rendering?
- Verify manifest exists and is loaded
- Check componentName matches the type in AST
- Look for error messages in console

## Next Steps

1. **Test with existing ASTs**: Run generator on `home.json` and `contact.json`
2. **Create new components**: Add more vuebits-inspired components
3. **Enhance variants**: Add more presets to existing components
4. **LLM Testing**: Test the enhanced prompt with actual LLM calls

## Files Modified

- ✅ `compiler/server/src/vue_generator.py` - Core ID and variant logic
- ✅ `compiler/server/src/project_generator.py` - Added animations
- ✅ `compiler/server/prompt.md` - Updated LLM instructions
- ✅ `compiler/manifests/*.manifest.json` - New component manifests
- ✅ `compiler/manifests/MANIFEST_SCHEMA.md` - Schema documentation

## Resources

- Full details: See `ENHANCEMENT_SUMMARY.md`
- Schema reference: See `manifests/MANIFEST_SCHEMA.md`
- Test example: See `server/inputs/test-enhanced.json`
- Vue Bits: https://vue-bits.dev (for inspiration)
