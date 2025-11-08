# Vue Bits Component Catalog

This document catalogs Vue Bits components we want to support, organized by category.

## Text Animations

### 1. SplitText
- **Purpose**: Animates text by splitting it into characters/words
- **Use Case**: Hero titles, dramatic text reveals, attention-grabbing headlines
- **Props**: text, animation-type (fade, slide, bounce), delay, duration
- **Interactive**: No

### 2. TypeWriter
- **Purpose**: Types text character by character
- **Use Case**: Terminal effects, code demos, dynamic messaging
- **Props**: text, speed, cursor, loop
- **Interactive**: No

### 3. TextReveal
- **Purpose**: Reveals text with mask/clip animations
- **Use Case**: Headlines, section introductions
- **Props**: text, direction, duration, delay
- **Interactive**: No

### 4. GradientText
- **Purpose**: Text with animated gradient
- **Use Case**: Hero titles, brand names, emphasis
- **Props**: text, gradient-colors, animated, duration
- **Interactive**: No
- **Status**: ✅ Already implemented

## Backgrounds

### 1. GridPattern
- **Purpose**: Animated grid background
- **Use Case**: Section backgrounds, hero sections, tech-themed pages
- **Props**: color, spacing, stroke-width, animated
- **Interactive**: No

### 2. DotPattern
- **Purpose**: Dot matrix background
- **Use Case**: Modern landing pages, tech sections
- **Props**: color, spacing, size, animated
- **Interactive**: No

### 3. Particles
- **Purpose**: Floating particle effects
- **Use Case**: Hero sections, immersive backgrounds
- **Props**: count, speed, color, size, interactive
- **Interactive**: Optional (mouse follow)

### 4. Meteors
- **Purpose**: Falling meteor animation
- **Use Case**: Dynamic backgrounds, space themes
- **Props**: count, speed, color, size
- **Interactive**: No

### 5. GridScan
- **Purpose**: Animated scanning grid
- **Use Case**: Tech demos, futuristic themes
- **Props**: color, scan-speed, grid-size
- **Interactive**: No

### 6. ColorBends
- **Purpose**: Flowing color gradients
- **Use Case**: Modern backgrounds, brand sections
- **Props**: colors, speed, blur
- **Interactive**: No

## Interactive Components

### 1. AnimatedCard (HoverCard)
- **Purpose**: Card with hover effects
- **Use Case**: Feature cards, product cards, portfolio items
- **Props**: variant (glow, lift, tilt), glow-color, shadow
- **Interactive**: Yes (hover effects)

### 2. Accordion
- **Purpose**: Collapsible content sections
- **Use Case**: FAQs, content organization, documentation
- **Props**: title, is-open (state), icon-type
- **Interactive**: Yes (click to expand/collapse)
- **Status**: ✅ Already implemented
- **Automation**: ⚠️ Needs to be recognized as clickable

### 3. Tabs
- **Purpose**: Tabbed content switcher
- **Use Case**: Content organization, settings panels
- **Props**: tabs (array), active-tab (state), variant
- **Interactive**: Yes (click tabs)
- **Automation**: ⚠️ Needs tab recognition

### 4. Dialog/Modal
- **Purpose**: Overlay dialog box
- **Use Case**: Forms, confirmations, detailed content
- **Props**: is-open (state), title, close-button
- **Interactive**: Yes (open, close, backdrop click)
- **Automation**: ⚠️ Needs modal detection

### 5. Tooltip
- **Purpose**: Hover information
- **Use Case**: Help text, additional info
- **Props**: content, position, trigger (hover/click)
- **Interactive**: Yes (hover/click)

### 6. Badge
- **Purpose**: Small label/indicator
- **Use Case**: Status, counts, labels
- **Props**: variant, color, size
- **Interactive**: No

### 7. Progress
- **Purpose**: Progress indicator
- **Use Case**: Loading, completion status
- **Props**: value, max, variant (linear, circular)
- **Interactive**: No

### 8. Toggle/Switch
- **Purpose**: On/off switch
- **Use Case**: Settings, feature toggles
- **Props**: checked (state), disabled, size
- **Interactive**: Yes (click to toggle)
- **Automation**: ⚠️ Needs switch recognition

## Layout Components

### 1. Container
- **Purpose**: Max-width content wrapper
- **Use Case**: Page layouts, content centering
- **Props**: max-width, padding
- **Interactive**: No

### 2. Stack
- **Purpose**: Vertical/horizontal layout
- **Use Case**: List layouts, form fields
- **Props**: direction, spacing, align
- **Interactive**: No

### 3. Grid
- **Purpose**: CSS Grid layout
- **Use Case**: Card grids, galleries
- **Props**: columns, gap, responsive
- **Interactive**: No

## Form Components

### 1. Input (Enhanced)
- **Purpose**: Styled text input
- **Use Case**: Forms, search bars
- **Props**: placeholder, variant, error, disabled
- **Interactive**: Yes (type, focus)
- **Automation**: ✅ Already supported

### 2. Select
- **Purpose**: Dropdown selector
- **Use Case**: Forms, filters
- **Props**: options, placeholder, variant
- **Interactive**: Yes (click, select)
- **Automation**: ⚠️ Needs dropdown recognition

### 3. Checkbox
- **Purpose**: Multi-select option
- **Use Case**: Forms, settings
- **Props**: checked (state), label, disabled
- **Interactive**: Yes (click)
- **Automation**: ⚠️ Needs checkbox recognition

### 4. Radio
- **Purpose**: Single-select option
- **Use Case**: Forms, quizzes
- **Props**: checked (state), name, value
- **Interactive**: Yes (click)
- **Automation**: ⚠️ Needs radio recognition

## Effects Components

### 1. SplashCursor
- **Purpose**: Animated cursor effect
- **Use Case**: Interactive pages, portfolios
- **Props**: color, size, fade-duration
- **Interactive**: Follows mouse

### 2. Spotlight
- **Purpose**: Moving spotlight effect
- **Use Case**: Hero sections, dramatic reveals
- **Props**: size, color, intensity
- **Interactive**: Follows mouse

### 3. Shimmer
- **Purpose**: Shimmer/shine effect
- **Use Case**: Loading states, attention
- **Props**: color, speed, width
- **Interactive**: No

## Priority Implementation Order

### Phase 1 (Immediate - High Impact)
1. ✅ Card (elevated, glow variants)
2. ✅ GradientText
3. ✅ Accordion
4. GridPattern (background)
5. DotPattern (background)
6. Badge
7. Tabs

### Phase 2 (Essential Interactivity)
8. Dialog/Modal
9. Toggle/Switch
10. Select (dropdown)
11. Checkbox
12. Radio

### Phase 3 (Visual Enhancement)
13. Particles (background)
14. Progress
15. Tooltip
16. Shimmer
17. AnimatedCard (hover effects)

### Phase 4 (Advanced Effects)
18. SplitText
19. TypeWriter
20. Meteors
21. SplashCursor
22. Spotlight

## Automation Considerations

### Currently Not Recognized (Need Updates):
1. **Accordion headers** - Should be clickable
2. **Tab buttons** - Should be clickable
3. **Modal close buttons** - Should be clickable
4. **Modal backdrops** - Should be clickable
5. **Toggle switches** - Should be clickable
6. **Select dropdowns** - Should be clickable/expandable
7. **Checkboxes** - Should be clickable
8. **Radio buttons** - Should be clickable
9. **Badge clicks** (if used as filters)
10. **Custom button variants** in complex components

### Update Needed in automation_agent.js:
```javascript
// Current: Only recognizes button, a, input, textarea
// Need to add:
- [role="button"]
- [data-component-type="accordion-header"]
- [data-component-type="tab"]
- [data-component-type="dialog-close"]
- [data-component-type="toggle"]
- select elements
- [type="checkbox"]
- [type="radio"]
- Custom click handlers on divs with specific patterns
```
