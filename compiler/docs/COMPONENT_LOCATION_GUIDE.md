# Vue Bits Component Location Guide

Quick reference for finding each component in the multi-page showcase.

## 🏠 Home Page (`/`)

### Hero Section
- **Background**: `Ribbons` (diagonal, 5 ribbons, purple/pink gradient)
- **Overlay**: `DarkVeil` (bottom gradient with blur)
- **Left Column (60%)**:
  - Title: `BlurText` - "Build Amazing Experiences" (72px)
  - Subtitle: `GradualBlur` - Fade-blur effect on description text
  - CTA Button: Gradient purple button
- **Right Column (40%)**:
  - `CardSwap` - 3D flip card (hover to see back side)

### Features Section
- **Background**: `ColorBends` - 4-color morphing orbs
- **Title**: `GradientText` - "Powerful Features"
- **Grid**: `MagicBento` - 3-column grid with hover lift
  - 3 feature cards with icons

---

## 👥 About Page (`/about`)

### Team Section
- **Background**: `Plasma` - Cosmic variant with 3 plasma orbs
- **Overlay**: `DarkVeil` - Subtle overlay
- **Title**: `BlurText` - "Meet Our Team"
- **Team Grid**: 4x `ProfileCard` (glass variant)
  - Sarah Chen - Lead Designer
  - Alex Kumar - Senior Developer
  - Maya Rodriguez - UX Researcher
  - Jordan Smith - Creative Director
  - Each with avatar from pravatar.cc

### Process Section
- **Title**: `GradientText` - "Our Process"
- **Component**: `Stepper` - Horizontal layout
  - 4 steps: Discovery, Design, Development, Launch
  - Interactive with Previous/Next buttons
  - Uses state management (currentStep)

---

## 🛠️ Services Page (`/services`)

### Main Section
- **Background**: `Squares` - Wave variant grid pattern
- **Title**: `BlurText` - "What We Offer"
- **Subtitle**: `GradualBlur` - Description text
- **Navigation**: `CardNav` - 6 service cards
  - Web Design 🎨
  - Development 💻
  - UI/UX ✨
  - Consulting 💡
  - Support 🛠️
  - Training 📚
- **Details Grid**: 4 service detail cards (2x2)
  - Fast Deployment 🚀
  - Custom Solutions 🎯
  - Analytics & Insights 📊
  - Security First 🔒

---

## 📧 Contact Page (`/contact`)

### Contact Section
- **Background**: `ColorBends` - 4-color slow morphing (pink/red/blue)
- **Overlay**: `DarkVeil` - Radial center-focus with blur
- **Header**:
  - Title: `GradientText` - "Let's Build Something Amazing"
  - Subtitle: `BlurText` - "Get in touch with us today"
- **Left Column (50%)**: 3 info cards
  - Email Us 📧
  - Live Chat 💬
  - Visit Us 📍
- **Right Column (50%)**: Contact form card
  - 3x `Textbox` components (Name, Email, Message)
  - Submit button

---

## 🔍 Quick Component Search

**Looking for a specific component? Use this index:**

- **BlurText**: Home (title), About (title), Services (title), Contact (subtitle)
- **GradualBlur**: Home (subtitle), Services (subtitle)
- **Ribbons**: Home (hero background)
- **ColorBends**: Home (features bg), Contact (main bg)
- **Plasma**: About (background)
- **Squares**: Services (background)
- **DarkVeil**: Home (overlay), About (overlay), Contact (overlay)
- **MagicBento**: Home (features grid)
- **ProfileCard**: About (4 team members)
- **CardSwap**: Home (flip card on right)
- **CardNav**: Services (navigation grid)
- **Stepper**: About (process workflow)
- **GradientText**: Home (title), About (title), Contact (title)
- **Textbox**: Contact (form inputs)

---

## 🎨 Background Effects Summary

Each page has a distinct visual identity through background components:

| Page     | Primary Background | Overlay    | Effect Style     |
|----------|-------------------|------------|------------------|
| Home     | Ribbons           | DarkVeil   | Flowing diagonal |
| About    | Plasma            | DarkVeil   | Cosmic energy    |
| Services | Squares           | None       | Grid waves       |
| Contact  | ColorBends        | DarkVeil   | Morphing colors  |

---

## 💡 Usage Tips

1. **Testing Stepper**: Click Previous/Next buttons on About page to see state changes
2. **CardSwap Effect**: Hover over the card on Home page right side
3. **ProfileCard Variants**: All team cards use "glass" variant with backdrop blur
4. **CardNav Interaction**: Each service card is a clickable link
5. **Background Layers**: Use browser DevTools to inspect z-index layering

---

## 📱 Navigation

Use Vue Router links in the generated app:
- `/` - Home
- `/about` - About
- `/services` - Services
- `/contact` - Contact

Or manually navigate in browser:
- `http://localhost:5173/`
- `http://localhost:5173/about`
- `http://localhost:5173/services`
- `http://localhost:5173/contact`
