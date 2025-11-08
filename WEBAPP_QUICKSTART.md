# Voice-First Web App - Quick Start Guide

This guide will help you get the new web application UI up and running quickly.

## What Was Built

A complete React-based UI with three main screens:

1. **Create Project Screen** - Minimal, centered design with voice control
2. **Template Selection Screen** - 2x2 grid showing 4 design options in iframes
3. **Canvas Editor Screen** - Main editing workspace with live preview

**Design Style**: Liquid glass aesthetics with frosted translucency, dark theme, and a single accent color (#6AA8FF).

## Quick Start

### Step 1: Install Dependencies

```bash
# Install React app dependencies
cd webapp
npm install

# Install Vue iframe content dependencies
cd ../iframe-content
npm install
```

### Step 2: Run Both Servers

You need **two terminal windows** running simultaneously:

**Terminal 1 - React App (Main UI):**
```bash
cd webapp
npm run dev
```
This starts the React app on `http://localhost:5173`

**Terminal 2 - Vue App (Iframe Content):**
```bash
cd iframe-content
npm run dev
```
This starts the Vue demo content on `http://localhost:5174`

### Step 3: Open Your Browser

Navigate to: `http://localhost:5173`

You should see the Create Project screen with a centered glass card.

## Navigation Flow

1. **Create Project** (`/`) 
   - Click "Get Started" to proceed
   
2. **Template Selection** (`/templates`)
   - View 4 design options in iframes
   - Hover over cards to see "Select" button
   - Click any card to continue
   
3. **Canvas Editor** (`/editor/a`)
   - Main editing workspace
   - Canvas with live preview
   - Voice control button at bottom center
   - History button in top bar (click to toggle sidebar)

## Project Structure

```
/webapp                      # React main application
  /src
    /components              # Reusable UI components
    /screens                 # Main application screens
    /styles                  # Design system (tokens, global styles)
    /router                  # React Router setup
  package.json
  vite.config.js

/iframe-content              # Vue demo app (displayed in iframes)
  /src
    /views                   # Demo website pages
    /router                  # Vue Router
  package.json
  vite.config.js
```

## Key Features Implemented

### Design System
- ✅ Liquid glass components with frosted blur effects
- ✅ Dark color palette with monochrome + single accent
- ✅ 8pt grid spacing system
- ✅ Smooth 180-240ms animations
- ✅ WCAG 2.1 AA contrast compliance

### Components
- ✅ `GlassCard` - Frosted glass container with hover effects
- ✅ `VoiceControl` - Microphone button with pulsing animation
- ✅ `StatusIndicator` - Connection status (green/amber/red)
- ✅ `CanvasFrame` - Glass-wrapped iframe with label and status
- ✅ `TopBar` - App navigation with back button

### Screens
- ✅ CreateProject - Minimal landing with CTA
- ✅ TemplateSelection - 2x2 grid of iframe previews
- ✅ CanvasEditor - Main workspace with voice control

### Routing
- ✅ React Router with 3 main routes
- ✅ Smooth transitions between screens
- ✅ Back navigation support

## Development Tips

### Ports
- React app: `5173`
- Vue iframe: `5174`

Both must be running for iframes to display content.

### Hot Reload
Both Vite servers support hot module replacement (HMR), so changes will reflect immediately.

### Voice Control
Voice control buttons are functional but currently log to console. Next steps:
- Integrate OpenAI Whisper API
- Add voice command processing
- Connect to AST compiler backend

### Iframe Content
The Vue app shows an iPhone landing page with:
- Home page with hero sections
- Features page
- Compare page  
- Pricing page with interactive toggle

## Troubleshooting

**Issue**: Iframes show blank or "connection refused"
- **Solution**: Make sure the Vue iframe server is running on port 5174

**Issue**: Styles not loading
- **Solution**: Check that both `tokens.css` and `global.css` are imported in `main.jsx`

**Issue**: Routes not working
- **Solution**: Ensure React Router is properly configured in `App.jsx`

## Next Steps

1. **Voice Integration**: Connect Whisper API for transcription
2. **postMessage**: Implement iframe communication
3. **Backend**: Connect to LLM AST compiler
4. **History Panel**: Populate with real voice commands
5. **Export**: Implement code export functionality

## Design System Reference

### Colors
- Background: `#0B0F14`
- Surface: `#12161C`
- Stroke: `#2A2F36`
- Text Primary: `#E8EDF3`
- Text Secondary: `#9AA3AE`
- Accent: `#6AA8FF`

### Spacing (8pt grid)
- `--space-1`: 8px
- `--space-2`: 16px
- `--space-3`: 24px
- `--space-4`: 32px
- `--space-6`: 48px
- `--space-8`: 64px

### Typography
- Display Large: 48px
- Display Medium: 36px
- Display Small: 28px
- Body Large: 16px
- Body: 14px

## Questions?

Check the full documentation in `/webapp/README.md` for more details.

---

**Built at MBZUAI Hackathon** 🚀

