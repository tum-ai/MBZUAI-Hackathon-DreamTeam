# Vue Bits Component Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    JSON AST INPUT                                │
│  (vue-bits-showcase.json)                                        │
│  - State definitions                                             │
│  - Component tree with props, slots, variants                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MANIFEST SYSTEM                                 │
│  (12 Component Manifests)                                        │
│  - BlurText      - Ribbons       - MagicBento                   │
│  - GradualBlur   - ColorBends    - ProfileCard                  │
│  - GradientText  - Plasma        - CardNav                      │
│  - DarkVeil      - Squares       - Stepper                      │
│                                   - CardSwap                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│               VUE GENERATOR (vue_generator.py)                   │
│  - Load manifests                                                │
│  - Generate semantic IDs                                         │
│  - Process variants                                              │
│  - Handle special components (V21)                               │
│  - Generate HTML template                                        │
│  - Generate Vue script (state, functions)                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│          PROJECT GENERATOR (project_generator.py)                │
│  - Create project skeleton                                       │
│  - Copy static files                                             │
│  - Generate App.vue with CSS animations                          │
│  - Generate router                                               │
│  - Generate package.json                                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│               OUTPUT (Vue.js Project)                            │
│  output/my-new-site/                                             │
│  ├── src/                                                        │
│  │   ├── App.vue (with animations)                              │
│  │   ├── main.js                                                │
│  │   ├── router/index.js                                        │
│  │   └── views/VueBitsShowcase.vue                              │
│  ├── public/automation_agent.js                                 │
│  ├── package.json                                                │
│  ├── vite.config.js                                              │
│  └── index.html                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Categories

```
Vue Bits Components (13 Total)
│
├── TEXT & TYPOGRAPHY
│   ├── BlurText ───────────► Animated blur-in reveal
│   ├── GradualBlur ────────► Gradient mask blur
│   └── GradientText ───────► Animated gradient colors
│
├── BACKGROUND EFFECTS
│   ├── Ribbons ────────────► Flowing animated ribbons
│   ├── ColorBends ─────────► Morphing color gradients
│   ├── Plasma ─────────────► Plasma orb effects
│   ├── Squares ────────────► Animated grid pattern
│   └── DarkVeil ───────────► Dark overlay gradient
│
└── INTERACTIVE COMPONENTS
    ├── MagicBento ─────────► Grid with hover effects
    ├── ProfileCard ────────► Profile display cards
    ├── CardNav ────────────► Card-style navigation
    ├── Stepper ────────────► Step wizard component
    └── CardSwap ───────────► 3D flip cards
```

## Data Flow

```
User Creates AST
      │
      ├─► Defines component type
      ├─► Sets props (content, style, etc.)
      ├─► Chooses variant (optional)
      ├─► Adds child components in slots
      └─► Binds state (optional)
      │
      ▼
Manifest Lookup
      │
      ├─► Validate component exists
      ├─► Load prop definitions
      ├─► Load variant presets
      └─► Check special rendering rules
      │
      ▼
Variant Processing
      │
      ├─► Apply variant props
      ├─► Merge with node props
      └─► Node props take precedence
      │
      ▼
Special Component Rendering
      │
      ├─► Check component type
      ├─► Apply custom HTML generation
      ├─► Generate child elements
      └─► Add animations/effects
      │
      ▼
HTML Generation
      │
      ├─► Generate opening tag
      ├─► Add semantic IDs
      ├─► Apply inline styles
      ├─► Render children recursively
      └─► Generate closing tag
      │
      ▼
Vue File Assembly
      │
      ├─► Build <template>
      ├─► Build <script setup>
      ├─► Generate state refs
      ├─► Generate event functions
      └─► Add <style scoped>
      │
      ▼
Output: VueBitsShowcase.vue
```

## Component Rendering Pipeline

```
┌──────────────────┐
│  Component Node  │
└────────┬─────────┘
         │
         ├─► Has variant? ─► Load variant props
         │
         ├─► Special type? ─┐
         │                  │
         │                  ├─► BlurText ─────► Add blur animation
         │                  ├─► Ribbons ──────► Generate ribbons
         │                  ├─► ColorBends ───► Generate orbs
         │                  ├─► Plasma ───────► Generate plasma
         │                  ├─► Squares ──────► CSS grid pattern
         │                  ├─► DarkVeil ─────► Gradient overlay
         │                  ├─► ProfileCard ──► Structured HTML
         │                  ├─► Stepper ──────► Step elements
         │                  ├─► CardSwap ─────► Flip structure
         │                  ├─► CardNav ──────► Nav items
         │                  └─► MagicBento ───► Grid container
         │
         ├─► Has slots? ────► Render children recursively
         │
         ├─► Has events? ───► Generate event functions
         │
         └─► Generate HTML ─► Output template string
```

## Layering Strategy

```
TYPICAL SECTION STRUCTURE (z-index layers)

┌─────────────────────────────────────────┐ ▲
│                                         │ │
│        CONTENT (z-index: 10)           │ │ Top
│        - Text                           │ │
│        - Cards                          │ │
│        - Interactive elements           │ │
│                                         │ │
├─────────────────────────────────────────┤ │
│                                         │ │
│      VEIL/OVERLAY (z-index: 1)         │ │
│      - DarkVeil                         │ │
│      - Gradient masks                   │ │
│                                         │ │
├─────────────────────────────────────────┤ │
│                                         │ │
│    BACKGROUND EFFECT (z-index: 0)      │ │ Bottom
│    - Ribbons / ColorBends               │ │
│    - Plasma / Squares                   │ │
│                                         │ │
└─────────────────────────────────────────┘ ▼

position: relative on parent container
position: absolute on background/veil layers
```

## Animation Timeline

```
Page Load Sequence:

0.0s ─► Background effects start (continuous loop)
        - Ribbons flow
        - ColorBends morph
        - Plasma pulses
        - Squares animate

0.0s ─► GradientText appears with gradient animation

0.3s ─► BlurText reveals (if delay="0.3s")

Hover ─► MagicBento items lift
      ─► CardSwap flips
      ─► CardNav items transform

State Change ─► Stepper updates active step
```

## CSS Animation Reference

```css
/* GRADIENT TEXT */
@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50% }
  50% { background-position: 100% 50% }
}
Duration: 3s, infinite

/* BLUR TEXT */
@keyframes blur-in {
  0% { filter: blur(10px); opacity: 0 }
  100% { filter: blur(0); opacity: 1 }
}
Duration: 1s, forwards

/* RIBBONS */
@keyframes ribbon-flow {
  0% { transform: translateX(-50%) rotate(-15deg) }
  100% { transform: translateX(50%) rotate(-15deg) }
}
Duration: 20s, infinite

/* COLOR BENDS */
@keyframes color-flow {
  0%, 100% { transform: translate(0%, 0%) scale(1) }
  25% { transform: translate(-25%, 25%) scale(1.2) }
  50% { transform: translate(25%, -25%) scale(0.8) }
  75% { transform: translate(-25%, -25%) scale(1.1) }
}
Duration: 15s, infinite

/* PLASMA */
@keyframes plasma-flow {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.6 }
  33% { transform: translate(-30%, 30%) scale(1.3); opacity: 0.8 }
  66% { transform: translate(30%, -30%) scale(0.9); opacity: 0.5 }
}
Duration: 10s, infinite

/* SQUARES */
@keyframes square-animation {
  0%, 100% { opacity: 0.2 }
  50% { opacity: 0.4 }
}
Duration: 2s, infinite

/* CARD SWAP */
.card-swap-hover:hover .card-swap-inner {
  transform: rotateY(180deg);
}
Duration: 0.6s

/* MAGIC BENTO */
.magic-bento > *:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}
Duration: 0.3s
```

## State Management Flow

```
User Interaction
       │
       ▼
Event Trigger
       │
       ├─► click
       ├─► hover
       └─► input
       │
       ▼
Event Handler Function
       │
       └─► Generated by vue_generator.py
           function on{id}_{event}() {
             stateVar.value = newValue;
           }
       │
       ▼
Vue Reactivity
       │
       └─► ref() updates
       │
       ▼
Template Re-renders
       │
       ├─► :style bindings update
       ├─► v-if conditions evaluate
       └─► Visual changes appear

Example: Stepper
─────────────────
currentStep.value = 0 (initial)
       │
       ▼
User clicks "Next"
       │
       ▼
currentStep.value++ (now 1)
       │
       ▼
:style binding recalculates
background: currentStep.value === 1 ? 'blue' : 'gray'
       │
       ▼
Step 1 turns blue, Step 0 turns green (completed)
```

## File Structure Map

```
MBZUAI-Hackathon-DreamTeam/
│
└── compiler/
    │
    ├── manifests/
    │   ├── BlurText.manifest.json ──────► Component definition
    │   ├── GradualBlur.manifest.json ───► Props, variants, slots
    │   ├── Ribbons.manifest.json ───────► Animation specs
    │   ├── ColorBends.manifest.json ────► Color presets
    │   ├── Plasma.manifest.json ────────► Effect parameters
    │   ├── Squares.manifest.json ───────► Grid patterns
    │   ├── DarkVeil.manifest.json ──────► Overlay settings
    │   ├── MagicBento.manifest.json ────► Grid layouts
    │   ├── ProfileCard.manifest.json ───► Card variants
    │   ├── CardNav.manifest.json ───────► Nav styles
    │   ├── Stepper.manifest.json ───────► Step configs
    │   └── CardSwap.manifest.json ──────► Flip animations
    │
    ├── server/
    │   ├── inputs/
    │   │   └── vue-bits-showcase.json ──► Test AST with all components
    │   │
    │   ├── src/
    │   │   ├── vue_generator.py ────────► V21: Special component rendering
    │   │   └── project_generator.py ────► V21: CSS animations
    │   │
    │   └── project.json ────────────────► Project config (points to showcase)
    │
    ├── output/
    │   └── my-new-site/ ────────────────► Generated Vue.js project
    │       ├── src/
    │       │   ├── App.vue ─────────────► Global styles + animations
    │       │   ├── main.js ─────────────► Vue initialization
    │       │   ├── router/index.js ─────► Vue Router
    │       │   └── views/
    │       │       └── VueBitsShowcase.vue ──► Generated from AST
    │       │
    │       ├── package.json ────────────► Dependencies (Vue 3, Vite)
    │       └── vite.config.js ──────────► Vite config
    │
    └── Documentation/
        ├── VUE_BITS_SUMMARY.md ─────────► This file
        ├── VUE_BITS_IMPLEMENTATION.md ──► Technical details
        ├── VUE_BITS_QUICK_REFERENCE.md ─► Usage guide
        ├── ENHANCEMENT_SUMMARY.md ──────► System architecture
        └── QUICK_START.md ──────────────► Getting started
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Output)                         │
│  Vue 3 (Composition API) + Vite + Vue Router                │
│  - Reactive state with ref()                                │
│  - Template-based rendering                                 │
│  - CSS animations (no JS animation libs)                    │
│  - Single File Components (.vue)                            │
└─────────────────────────────────────────────────────────────┘
                             ▲
                             │
┌─────────────────────────────────────────────────────────────┐
│                  GENERATOR (Backend)                         │
│  Python 3                                                    │
│  - JSON parsing (ast, manifests)                            │
│  - String templating (HTML, Vue, CSS)                       │
│  - File I/O (reading ASTs, writing Vue files)              │
│  - Recursive tree traversal                                 │
└─────────────────────────────────────────────────────────────┘
                             ▲
                             │
┌─────────────────────────────────────────────────────────────┐
│                   DATA (Configuration)                       │
│  JSON                                                        │
│  - AST files (component trees)                              │
│  - Manifest files (component specs)                         │
│  - Project config (global settings)                         │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Ready

The generated project is production-ready:

```bash
# Development
npm run dev     # ─► Vite dev server (HMR)

# Production
npm run build   # ─► Optimized bundle
npm run preview # ─► Preview production build

# Output
dist/
├── index.html
├── assets/
│   ├── index-[hash].js   # JS bundle
│   └── index-[hash].css  # CSS bundle
└── automation_agent.js
```

## Summary

This architecture enables:
✅ Component-based UI generation from JSON
✅ Reusable manifest system for consistency
✅ Special rendering for complex components
✅ CSS-based animations (performant)
✅ State management support
✅ Hierarchical semantic IDs
✅ Variant presets for easy theming
✅ LLM-friendly documentation

Result: **Professional landing pages from simple JSON definitions!**
