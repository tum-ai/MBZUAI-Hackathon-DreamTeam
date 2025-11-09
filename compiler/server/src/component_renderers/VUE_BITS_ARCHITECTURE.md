# Vue Bits Integration Architecture

## Overview

Our system implements **Vue Bits-inspired components** without requiring the actual Vue Bits library. Instead, we use **CSS-based implementations** that mimic the Vue Bits API and appearance.

## Why This Approach?

1. **No External Dependencies**: Avoids adding Vue Bits as a dependency
2. **Full Control**: We can customize behavior and styling
3. **Deterministic Output**: CSS animations are predictable and don't require JavaScript
4. **Simpler Architecture**: No need to manage external component imports
5. **LLM-Friendly**: LLMs can use Vue Bits documentation as reference

## How It Works

### Component Renderers

Each Vue Bits-style component has a dedicated renderer (e.g., `blur_text_renderer.py`) that:

1. **Accepts Vue Bits API props** (e.g., `delay`, `stepDuration`, `direction`)
2. **Generates inline CSS** with animations
3. **Outputs styled HTML elements** (not `<BlurText>` components)

### Example: BlurText

**Input AST:**
```json
{
  "type": "BlurText",
  "props": {
    "text": "Isn't this so cool?!",
    "delay": 200,
    "stepDuration": 0.35,
    "animateBy": "words",
    "direction": "top"
  }
}
```

**Generated Output:**
```html
<span 
  data-component-id="blur-text-1" 
  data-nav-id="blur-text-1"
  class="blur-text-words"
  style="filter: blur(10px); opacity: 0; transform: translateY(-20px); animation: blur-in-top 0.35s 0.2s forwards"
>
  Isn't this so cool?!
</span>
```

## Supported Vue Bits Components

### Animation Components
- **BlurText**: Text with blur-in animation
- **GradualBlur**: Gradual blur mask effect

### Visual Effects
- **GradientText**: Animated gradient text
- **Ribbons**: Flowing ribbon background
- **ColorBends**: Animated color orbs
- **Plasma**: Plasma effect background
- **Squares**: Animated grid pattern
- **DarkVeil**: Gradient overlay

### Interactive Components  
- **Accordion**: Collapsible content
- **ProfileCard**: User profile display
- **Stepper**: Step indicator
- **CardSwap**: Flip card animation
- **CardNav**: Card-based navigation
- **MagicBento**: Grid with hover effects

## Props Mapping

We map Vue Bits props to CSS properties:

| Vue Bits Prop | CSS Output |
|---------------|------------|
| `delay` (ms) | `animation-delay` (s) |
| `stepDuration` (s) | `animation-duration` (s) |
| `direction` | `transform: translate*()` |
| `animateBy` | CSS class for targeting |
| `threshold` | (Observer trigger - not CSS) |

## Adding New Vue Bits-Style Components

1. **Study the Vue Bits component** - Understand props and behavior
2. **Create renderer** - Implement in `component_renderers/`
3. **Map props to CSS** - Convert API props to inline styles
4. **Update manifest** - Define props matching Vue Bits API
5. **Test output** - Verify HTML matches expected appearance

## Benefits for LLMs

LLMs can reference actual Vue Bits documentation when generating ASTs:

- ✅ Same prop names (`delay`, `stepDuration`, etc.)
- ✅ Same component names (`BlurText`, `GradientText`, etc.)
- ✅ Same visual effects and animations
- ✅ No need to learn a custom API

## Limitations

- **No JavaScript interactivity** from Vue Bits components
- **CSS-only animations** (no Intersection Observer yet)
- **Static effects** for some complex components

## Future Enhancements

1. **Add Intersection Observer** via generated `<script>` blocks
2. **Support `@animation-complete` events** via callbacks
3. **Implement variant system** more fully
4. **Add CSS keyframe generation** to `<style>` blocks

## CSS Animations Required

The generated components rely on CSS animations that should be included in the app's global stylesheet:

```css
@keyframes blur-in-top {
  from { filter: blur(10px); opacity: 0; transform: translateY(-20px); }
  to { filter: blur(0); opacity: 1; transform: translateY(0); }
}

@keyframes blur-in-bottom {
  from { filter: blur(10px); opacity: 0; transform: translateY(20px); }
  to { filter: blur(0); opacity: 1; transform: translateY(0); }
}

/* ... more animations ... */
```

These keyframes are generated automatically by the system when Vue Bits components are used.
