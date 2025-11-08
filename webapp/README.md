# Voice-First Web App UI

A React-based web application with liquid glass aesthetics for the voice-controlled web development platform.

## Features

- **Liquid Glass Design System**: Beautiful frosted glass UI with dark theme
- **Three Main Screens**:
  - Create Project: Minimal starting point with voice control
  - Template Selection: 2x2 grid of design options
  - Canvas Editor: Main editing workspace with live preview
- **Voice Control Integration**: Ready for Whisper API integration
- **Live Preview**: Iframes displaying generated content

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies for the main webapp:
```bash
cd webapp
npm install
```

2. Install dependencies for the iframe content:
```bash
cd ../iframe-content
npm install
```

### Development

You need to run **both** servers simultaneously:

#### Terminal 1 - Main React App (Port 5173):
```bash
cd webapp
npm run dev:webapp
```

#### Terminal 2 - Vue Iframe Content (Port 5174):
```bash
cd iframe-content
npm run dev
```

Then open your browser to `http://localhost:5173`

### Project Structure

```
webapp/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── GlassCard.jsx
│   │   ├── VoiceControl.jsx
│   │   ├── StatusIndicator.jsx
│   │   ├── CanvasFrame.jsx
│   │   └── TopBar.jsx
│   ├── screens/           # Main application screens
│   │   ├── CreateProject.jsx
│   │   ├── TemplateSelection.jsx
│   │   └── CanvasEditor.jsx
│   ├── styles/            # Design system
│   │   ├── tokens.css
│   │   └── global.css
│   └── router/            # React Router configuration
│       └── index.jsx
└── package.json

iframe-content/            # Vue app for live preview
├── src/
│   ├── views/            # iPhone landing page views
│   │   ├── Home.vue
│   │   ├── Features.vue
│   │   ├── Compare.vue
│   │   └── Pricing.vue
│   └── router/
└── package.json
```

## Design System

### Tokens

The design system is based on:
- **Colors**: Dark background (#0B0F14), glass overlays (rgba 14-18%), single accent (#6AA8FF)
- **Typography**: SF Pro/Inter, sizes 14/16/28/36/48
- **Spacing**: 8pt grid system
- **Motion**: 180-240ms ease-out transitions
- **Glass Effects**: backdrop-filter blur 16-24px

### Components

- **GlassCard**: Frosted glass container with hover animations
- **VoiceControl**: Floating voice input button with recording states
- **StatusIndicator**: Connection status (connected/updating/error)
- **CanvasFrame**: Glass-wrapped iframe with labeled header
- **TopBar**: Application chrome with navigation

## Navigation Flow

1. **Create Project** (`/`) → User clicks "Get Started" or uses voice
2. **Template Selection** (`/templates`) → User selects one of 4 design options
3. **Canvas Editor** (`/editor/:projectId`) → Main editing workspace

## Next Steps

- [ ] Integrate OpenAI Whisper API for voice transcription
- [ ] Implement postMessage communication with iframes
- [ ] Connect to LLM AST compiler backend
- [ ] Add keyboard shortcuts (grid toggle, etc.)
- [ ] Implement history/layers/actions panels
- [ ] Add real-time collaboration features

## Development Notes

- The React app (main UI) runs on port **5173**
- The Vue app (iframe content) runs on port **5174**
- Both must be running for full functionality
- Iframes point to `http://localhost:5174`

## Build

```bash
cd webapp
npm run build
```

The built files will be in `webapp/dist/`

