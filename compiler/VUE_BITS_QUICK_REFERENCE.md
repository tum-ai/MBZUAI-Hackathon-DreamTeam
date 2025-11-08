# Vue Bits Components Quick Reference

## Component List

| Component | Purpose | Best For |
|-----------|---------|----------|
| BlurText | Animated blur-in text | Headlines, subtitles |
| GradualBlur | Gradient blur effect | Overflow text, fade effects |
| GradientText | Animated gradient text | Hero titles, branding |
| Ribbons | Flowing ribbon background | Hero sections, headers |
| ColorBends | Morphing color gradients | Section backgrounds |
| Plasma | Plasma effect background | Futuristic sections |
| Squares | Grid pattern background | Technical sections |
| DarkVeil | Dark overlay gradient | Adding depth to backgrounds |
| MagicBento | Grid with hover effects | Feature grids, portfolios |
| ProfileCard | Profile display | Team pages, about sections |
| CardNav | Card-style navigation | Dashboards, menus |
| Stepper | Step-by-step wizard | Forms, processes |
| CardSwap | Flip card animation | Product showcases, reveals |

## Common Patterns

### Landing Page Hero
```json
{
  "type": "Box",
  "slots": {
    "default": [
      {
        "type": "Ribbons",
        "props": {"variant": "diagonal", "opacity": 0.4},
        "style": {"position": "absolute", "inset": "0"}
      },
      {
        "type": "DarkVeil",
        "props": {"variant": "center-focus"},
        "style": {"position": "absolute", "inset": "0"}
      },
      {
        "type": "Box",
        "style": {"position": "relative", "zIndex": "10"},
        "slots": {
          "default": [
            {"type": "GradientText", "props": {"content": "Title", "variant": "sunset"}},
            {"type": "BlurText", "props": {"content": "Subtitle", "delay": "0.3s"}}
          ]
        }
      }
    ]
  }
}
```

### Feature Grid
```json
{
  "type": "Box",
  "slots": {
    "default": [
      {
        "type": "ColorBends",
        "props": {"variant": "subtle"},
        "style": {"position": "absolute", "inset": "0"}
      },
      {
        "type": "MagicBento",
        "props": {"variant": "hover-lift", "columns": 3},
        "style": {"position": "relative", "zIndex": "10"},
        "slots": {
          "default": [
            {"type": "Card", "props": {"variant": "elevated"}},
            {"type": "Card", "props": {"variant": "elevated"}},
            {"type": "Card", "props": {"variant": "elevated"}}
          ]
        }
      }
    ]
  }
}
```

### Team Section
```json
{
  "type": "Box",
  "slots": {
    "default": [
      {
        "type": "Plasma",
        "props": {"variant": "cosmic"},
        "style": {"position": "absolute", "inset": "0", "opacity": "0.4"}
      },
      {
        "type": "Box",
        "style": {"position": "relative", "display": "grid", "gridTemplateColumns": "repeat(3, 1fr)"},
        "slots": {
          "default": [
            {"type": "ProfileCard", "props": {"variant": "glass", "name": "...", "title": "..."}},
            {"type": "ProfileCard", "props": {"variant": "glass", "name": "...", "title": "..."}},
            {"type": "ProfileCard", "props": {"variant": "glass", "name": "...", "title": "..."}}
          ]
        }
      }
    ]
  }
}
```

## Variant Guide

### Background Components

**Ribbons**
- `default` - Standard horizontal flow
- `fast` - Quick movement (10s)
- `slow` - Relaxed flow (40s)
- `diagonal` - Angled ribbons
- `vertical` - Top-to-bottom

**ColorBends**
- `default` - Balanced flow
- `fast` - Energetic (8s)
- `slow` - Calming (30s)
- `subtle` - Understated (opacity 0.3)
- `vibrant` - Bold colors (opacity 0.8)

**Plasma**
- `default` - Neon colors
- `electric` - Blue/purple
- `cosmic` - Deep space
- `fire` - Orange/red
- `ocean` - Blue/green

**Squares**
- `default` - Standard animation
- `wave` - Wave pattern
- `pulse` - Pulsing effect
- `random` - Random timing
- `fade` - Fade in/out

**DarkVeil**
- `default` - Standard overlay
- `subtle` - Light (opacity 0.3)
- `strong` - Heavy (opacity 0.8)
- `center-focus` - Radial gradient
- `edge-fade` - Blurred edges

### Text Components

**BlurText**
- `default` - 1s animation
- `fast` - 0.5s quick reveal
- `slow` - 2s dramatic reveal
- `subtle` - Minimal blur (5px)

**GradualBlur**
- `default` - Standard gradient
- `fade-blur` - Heavy blur
- `edge-blur` - Light edge blur

**GradientText**
- `sunset` - Warm orange/yellow
- `ocean` - Cool blue/teal
- `neon` - Vibrant pink/red
- `purple-haze` - Purple/pink

### Interactive Components

**MagicBento**
- `default` - Subtle hover
- `hover-lift` - Lift on hover (-8px)
- `glow` - Glow effect
- `tilt` - 3D tilt

**ProfileCard**
- `default` - Standard card
- `minimal` - Clean, minimal
- `detailed` - Rich gradient
- `glass` - Glassmorphism

**CardNav**
- `default` / `horizontal` - Horizontal row
- `vertical` - Stacked column
- `grid` - Grid layout

**Stepper**
- `default` / `horizontal` - Horizontal steps
- `vertical` - Timeline style
- `numbered` - Number indicators
- `dots` - Minimal dots

**CardSwap**
- `default` / `3d` - 3D flip (0.6s)
- `3d` (enhanced) - Enhanced 3D (0.8s)
- `slide` - Slide transition
- `fade` - Cross-fade

## Styling Tips

### Layering Backgrounds
Always use z-index for proper layering:
1. Background effect (z-index: 0)
2. Veil/overlay (z-index: 1)
3. Content (z-index: 10)

### Animation Timing
- Fast: 8-10s (energetic, attention-grabbing)
- Medium: 15-20s (balanced, professional)
- Slow: 30-40s (calming, ambient)

### Opacity Guidelines
- Subtle backgrounds: 0.2-0.3
- Standard backgrounds: 0.4-0.6
- Prominent overlays: 0.7-0.8

### Color Combinations

**Professional**
```json
["#667eea", "#764ba2", "#667eea"]
```

**Vibrant**
```json
["#f857a6", "#ff5858", "#4facfe", "#00f2fe"]
```

**Cosmic**
```json
["#5f0a87", "#a4508b", "#00d4ff", "#ff00ff"]
```

**Ocean**
```json
["#00c9ff", "#0099ff", "#00ff88"]
```

## State Binding

Components that support state binding:
- **Stepper**: `currentStep` property
- **CardSwap**: `flipped` property
- **Accordion**: `isOpen` property

Example:
```json
{
  "state": {
    "currentStep": {"type": "number", "defaultValue": 0}
  },
  "tree": {
    "type": "Stepper",
    "props": {
      "currentStep": {
        "type": "stateBinding",
        "stateKey": "currentStep"
      }
    }
  }
}
```

## Performance Tips

1. **Limit animated elements**: Use 3-5 ribbons/orbs max
2. **Use blur sparingly**: High blur values are GPU-intensive
3. **Prefer CSS animations**: Over JavaScript for better performance
4. **Layer backgrounds**: One per section max
5. **Optimize colors**: Fewer gradient stops = better performance

## Accessibility

Consider adding:
- Reduced motion support
- High contrast alternatives
- Screen reader descriptions
- Keyboard navigation

## Browser Support

All components use modern CSS:
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (may need -webkit- prefixes)
- Mobile: ✅ Works well

## Examples by Use Case

### SaaS Landing Page
- Hero: Ribbons + GradientText
- Features: ColorBends + MagicBento
- Pricing: Cards in grid
- CTA: Plasma + DarkVeil

### Portfolio Site
- Hero: Plasma + BlurText
- Projects: MagicBento with CardSwap
- About: ProfileCard
- Process: Stepper

### Product Showcase
- Hero: ColorBends + GradientText
- Features: Squares + Cards
- Demo: CardSwap flip cards
- Navigation: CardNav

### Tech Documentation
- Header: Ribbons (subtle)
- Sections: Squares background
- Navigation: CardNav (vertical)
- Progress: Stepper

---

**Pro Tip**: Layer multiple backgrounds with varying opacities and blend modes for unique effects!
