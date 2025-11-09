# Editor Agent

The Editor Agent generates component code based on user's natural language requests using an optimized single-step LLM process.

## How It Works

### Single-Step LLM Process (Optimized)

1. **Generate Component Directly**
   - LLM receives user intent, context, and structured component definitions
   - LLM also receives current AST for context (if editing)
   - LLM decides component type AND generates component in one call
   - Prompt structure inspired by compiler's `prompt.md` for maximum efficiency
   - Output: Complete component JSON object with id, type, props, slots

**Performance**: ~2.2s per request (70% faster than original two-step approach)

## Workflow

```
User Request
    ↓
server.py (/edit endpoint)
    ↓
editor.py
    ├─→ manifest_loader.py (get cached manifests - no disk I/O)
    ├─→ Load AST for context
    ↓
    ├─→ llm_client.py: generate_component_direct()
    │   └─→ Single LLM Call: Returns component JSON directly
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
1. LLM generates component directly in one call:
```json
{
  "id": "submit-button",
  "type": "Button",
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
1. LLM analyzes AST context and generates modified component in one call

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

- **Single-Step Process**: Optimized for speed with one LLM call
- **Structured Prompts**: Inspired by compiler's prompt.md for clear component definitions
- **Minimal Code**: Simple, clean implementation
- **Component-Focused**: Works at component level
- **Cached Resources**: Manifests and HTTP client cached at module level
- **Modern Styling**: Generates professional, modern components

## Performance Metrics

From test suite (`llm/tests/results/`):

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| EDIT agent | 7.4s | 2.2s | **70% faster** |
| Total test suite | 231.8s | 94.5s | **59% faster** |
| Average per task | 6.1s | 2.5s | **59% faster** |

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
