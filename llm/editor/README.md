# Editor Agent

The Editor Agent is responsible for generating JSON Patch arrays (RFC 6902) to modify the Abstract Syntax Tree (AST) of web components based on user's natural language requests.

## Overview

The Editor Agent acts as an "AI compiler" that translates user intent into precise code changes. It follows the same architectural pattern as the Planner and Clarifier agents, maintaining consistency across the system.

## Architecture

### Two-Step Flow

1. **Component Manifest Loading**
   - Loads all available component manifests from `/compiler/manifests/`
   - Understands component structure, props, slots, and events
   - Currently hardcoded, but designed for future API integration

2. **JSON Patch Generation**
   - Receives user intent and context
   - Loads current AST (from `home.json`) and project config (from `project.json`)
   - Uses K2 Think LLM to analyze and generate JSON Patch operations
   - Returns RFC 6902 compliant JSON Patch array

## Input/Output Format

### Input: `EditRequest`

```json
{
  "session_id": "session-123",
  "step_id": "step-456",
  "intent": "Add a button that says 'Click Me' | User wants to add an interactive button",
  "context": "User is building a landing page"
}
```

### Output: `EditResponse`

```json
{
  "session_id": "session-123",
  "step_id": "step-456",
  "intent": "Add a button that says 'Click Me' | User wants to add an interactive button",
  "context": "User is building a landing page",
  "code": "[{\"op\": \"add\", \"path\": \"/tree/slots/default/-\", \"value\": {...}}]"
}
```

The `code` field contains a JSON Patch array as a string. It can be parsed and applied to modify the AST.

## API Endpoint

### POST `/edit`

**Request:**
```bash
curl -X POST http://localhost:8000/edit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "step_id": "step-1",
    "intent": "Add a hero section with a dark gradient",
    "context": "User wants to create a modern landing page"
  }'
```

**Response:**
```json
{
  "session_id": "session-123",
  "step_id": "step-1",
  "intent": "Add a hero section with a dark gradient",
  "context": "User wants to create a modern landing page",
  "code": "[{\"op\": \"add\", \"path\": \"/tree/slots/default/-\", \"value\": {...}}]"
}
```

## File Structure

```
llm/editor/
├── __init__.py
├── models.py              # Pydantic models (EditRequest, EditResponse)
├── manifest_loader.py     # Component manifest loading utilities
├── llm_client.py         # K2 Think LLM interaction and prompt engineering
├── editor.py             # Main processing logic
├── tests/
│   ├── __init__.py
│   └── test_editor.py    # Test suite
└── README.md             # This file
```

## Component Capabilities

The editor can generate JSON Patches for:

- **Component Creation**: Add new components (Box, Text, Button, Image, etc.)
- **Component Editing**: Modify existing component properties and styles
- **State Management**: Add state variables and bind them to components
- **Event Handling**: Add click handlers, input events, etc.
- **Conditional Rendering**: Add v-if directives for show/hide logic
- **Layout**: Generate complex layouts with flexbox/grid
- **Styling**: Apply inline styles, gradients, positioning, etc.

## Available Components

- **Box**: Container/div for layouts
- **Text**: Text content with semantic tags (h1, h2, p, etc.)
- **Button**: Interactive button with click events
- **Image**: Images with src/alt
- **Link**: Hyperlinks (internal/external)
- **List**: Unordered/ordered lists
- **Table**: Data tables
- **Textbox**: Input fields
- **Icon**: SVG icons
- **Card**: Card components with variants
- **Accordion**: Collapsible content
- **GradientText**: Text with gradient effects

## Running Tests

```bash
cd llm/editor/tests
python test_editor.py
```

The test suite includes:
- Simple component creation (button)
- Component editing (modify existing elements)
- Stateful components (with events and state)
- Different component types (Image, Text, Card, etc.)

## Example Use Cases

### 1. Add a Simple Button
**Intent:** "Add a button that says 'Click Me'"

**Generated Patch:**
```json
[
  {
    "op": "add",
    "path": "/tree/slots/default/-",
    "value": {
      "id": "button-click-me",
      "type": "Button",
      "props": {
        "text": "Click Me",
        "style": {"padding": "10px 20px"}
      },
      "slots": {}
    }
  }
]
```

### 2. Make Title Larger
**Intent:** "Make the hero title larger"

**Generated Patch:**
```json
[
  {
    "op": "replace",
    "path": "/tree/slots/default/0/props/style/fontSize",
    "value": "96px"
  }
]
```

### 3. Add Stateful Component
**Intent:** "Add a button that shows 'Clicked' after you click it"

**Generated Patch:**
```json
[
  {
    "op": "add",
    "path": "/state/buttonText",
    "value": {"type": "string", "defaultValue": "Click Me"}
  },
  {
    "op": "add",
    "path": "/tree/slots/default/-",
    "value": {
      "id": "stateful-button",
      "type": "Button",
      "props": {
        "text": {"type": "expression", "value": "${state.buttonText}"}
      },
      "events": {
        "click": [{
          "type": "action:setState",
          "stateKey": "buttonText",
          "newValue": "Clicked!"
        }]
      }
    }
  }
]
```

## Design Principles

1. **Component-Level Editing**: Focuses on component creation and modification
2. **Minimal & Clean**: Simple, readable code following existing patterns
3. **Hardcoded for Now**: Manifest/AST loading is hardcoded, designed for future API integration
4. **RFC 6902 Compliance**: All patches follow the JSON Patch standard
5. **Prompt-Driven**: Uses the compiler prompt from `prompt.md` as the foundation
6. **Error Handling**: Graceful fallbacks for parsing errors

## Future Enhancements

- [ ] API integration for dynamic AST loading
- [ ] Page-level operations (add pages, modify global styles)
- [ ] Multi-component operations in a single request
- [ ] AST validation before returning patches
- [ ] Patch preview/simulation
- [ ] Session-based AST caching

## Integration with Other Agents

The Editor Agent works alongside:
- **Planner Agent** (`/decide`): Classifies requests and routes "edit" tasks to the editor
- **Clarifier Agent** (`/clarify`): Handles ambiguous requests before they reach the editor
- **Action Agent** (future): Handles user interactions with the UI (scroll, click, navigate)

## Notes

- Currently uses hardcoded paths to `compiler/server/inputs/home.json` and `project.json`
- Requires `K2_API_KEY` environment variable for LLM access
- Follows K2 Think's response format with `<think>` and `<answer>` tags
- All component IDs are auto-generated as human-readable strings (e.g., "hero-section", "hero-title")

