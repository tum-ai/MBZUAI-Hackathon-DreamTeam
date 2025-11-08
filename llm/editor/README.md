# Editor Agent

The Editor Agent generates component code based on user's natural language requests using a two-step LLM process.

## How It Works

### Two-Step LLM Process

1. **Step 1: Decide Action & Component Type**
   - LLM analyzes user intent
   - Decides: "generate" (create new) or "edit" (modify existing)
   - Chooses component type: Button, Text, Box, Image, etc.
   - Output: `{"action": "generate/edit", "component_type": "Button"}`

2. **Step 2: Generate/Edit Component**
   - LLM receives the specific component manifest
   - If editing: also receives current AST
   - Generates complete component JSON
   - Output: Component object with id, type, props, slots

## Workflow

```
User Request
    ↓
server.py (/edit endpoint)
    ↓
editor.py
    ├─→ manifest_loader.py (load all manifests)
    ↓
    ├─→ llm_client.py: decide_component_action()
    │   └─→ LLM Call 1: Returns {"action": "generate", "component_type": "Button"}
    ↓
    ├─→ Get specific component manifest (Button.manifest.json)
    ├─→ Load AST if action is "edit"
    ↓
    ├─→ llm_client.py: generate_or_edit_component()
    │   └─→ LLM Call 2: Returns component JSON
    ↓
editor.py (wrap in EditResponse)
    ↓
server.py (return to user)
```

## API Endpoint

### POST `/edit`

**Request:**
```json
{
  "session_id": "session-123",
  "step_id": "step-1",
  "intent": "Add a button that says Click Me",
  "context": "User is building a landing page"
}
```

**Response:**
```json
{
  "session_id": "session-123",
  "step_id": "step-1",
  "intent": "Add a button that says Click Me",
  "context": "User is building a landing page",
  "code": "{\"id\": \"button-click-me\", \"type\": \"button\", \"props\": {...}, \"slots\": {}}"
}
```

The `code` field contains a complete component JSON object (not JSON Patch).

## Available Components

- **Box** - Container/div for layouts
- **Text** - Text content (h1, h2, p, etc.)
- **Button** - Interactive button
- **Image** - Images
- **Link** - Hyperlinks
- **List** - Lists
- **Table** - Data tables
- **Textbox** - Input fields
- **Icon** - SVG icons
- **Card** - Card components
- **Accordion** - Collapsible content
- **GradientText** - Text with gradients

## File Structure

```
llm/editor/
├── models.py              # EditRequest/EditResponse
├── manifest_loader.py     # Load component manifests
├── llm_client.py         # Two LLM functions
├── editor.py             # Main orchestration
└── README.md             # This file
```

## Example Usage

### Generate a Button

**Request:**
```bash
curl -X POST http://localhost:8000/edit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo",
    "step_id": "step-1",
    "intent": "Add a button that says Submit",
    "context": "Building a contact form"
  }'
```

**What Happens:**
1. LLM decides: `{"action": "generate", "component_type": "Button"}`
2. LLM generates:
```json
{
  "id": "submit-button",
  "type": "button",
  "props": {
    "text": "Submit",
    "style": {
      "padding": "10px 20px",
      "fontSize": "16px",
      "backgroundColor": "#007bff",
      "color": "#fff"
    }
  },
  "slots": {}
}
```

### Edit a Component

**Request:**
```bash
curl -X POST http://localhost:8000/edit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo",
    "step_id": "step-2",
    "intent": "Make the title larger",
    "context": "User wants to emphasize the hero title"
  }'
```

**What Happens:**
1. LLM decides: `{"action": "edit", "component_type": "Text"}`
2. LLM finds title in AST and modifies fontSize

## Setup

1. **Set API Key:**
   ```bash
   echo "K2_API_KEY=your_key" > llm/.env
   ```

2. **Start Server:**
   ```bash
   cd llm && source venv/bin/activate
   python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000
   ```

3. **Run Tests:**
   ```bash
   cd llm/editor/tests
   python runner.py
   ```
   
   The test suite will:
   - Run 10 comprehensive tests in parallel
   - Test both generate and edit actions
   - Validate component structure
   - Save results to `results/run-N/`

4. **Manual Test:**
   ```bash
   curl -X POST http://localhost:8000/edit \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test", "step_id": "1", "intent": "Add a button", "context": ""}'
   ```

## Design Principles

- **Two-Step Process**: Clear separation of decision and generation
- **Minimal Code**: Simple, clean implementation
- **Component-Focused**: Works at component level
- **LLM-Driven**: Both steps use LLM intelligence
- **Modern Styling**: Generates professional, modern components

## Integration

The editor integrates with:
- **Planner** (`/decide`) - Routes "edit" requests
- **Clarifier** (`/clarify`) - Handles ambiguity
- **Compiler** (future) - Applies generated components to AST

## Notes

- Uses K2 Think API for LLM calls
- Hardcoded AST path: `compiler/server/inputs/home.json`
- 12 component types supported
- Returns complete component JSON (not JSON Patch)
