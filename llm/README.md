# LLM Agent Orchestration System

A robust multi-agent system that processes user requests through intelligent planning and specialized execution agents.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUEST                           │
│             POST /plan {sid, text, step_id?}                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                                │
│                   (orchestrator.py)                              │
│                                                                   │
│  • Coordinates full pipeline execution                           │
│  • Manages sequential task processing                            │
│  • Logs every step                                               │
│  • Fail-fast error handling                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PLANNER                                  │
│                    (planner/planner.py)                          │
│                                                                   │
│  • Classifies user intent                                        │
│  • Splits multi-task requests                                    │
│  • Enriches prompts with context                                 │
│  • Manages task queue per session                                │
│  • Returns: List[DecideResponse]                                 │
│    └─> {step_id, step_type, intent, context}                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────┴────────┐
                    │  Route by Type  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    EDITOR    │    │    ACTOR     │    │  CLARIFIER   │
│  StepType    │    │  StepType    │    │  StepType    │
│    EDIT      │    │     ACT      │    │   CLARIFY    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       │ Returns           │ Returns            │ Returns
       │ EditResponse      │ ActionResponse     │ ClarifyResponse
       │ {code: str}       │ {action: str}      │ {reply: str}
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATOR NORMALIZATION                  │
│  Converts agent-specific responses to AgentResult:      │
│  • EditResponse.code → AgentResult.result               │
│  • ActionResponse.action → AgentResult.result           │
│  • ClarifyResponse.reply → AgentResult.result           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              UNIFIED AGENT RESULTS                      │
│         List[AgentResult]                                │
│         {session_id, step_id, intent,                   │
│          context, result, agent_type}                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  RESPONSE TO CLIENT                     │
│       PlanResponse {sid, results: List[AgentResult]}    │
└─────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
llm/
├── README.md                    # This file
├── server.py                    # FastAPI server with all endpoints
├── orchestrator.py              # Main orchestration logic
│
├── planner/                     # Intent classification & task splitting
│   ├── planner.py              # Core planner logic
│   ├── models.py               # Data models (PlanRequest, PlanResponse, etc.)
│   ├── llm_client.py           # LLM integration for task splitting
│   ├── queue_manager.py        # Task queue management per session
│   └── session_manager.py      # Session history management
│
├── editor/                      # UI component generation agent
│   ├── editor.py               # Editor agent logic
│   ├── models.py               # EditRequest, EditResponse
│   ├── llm_client.py           # LLM integration for component generation
│   └── manifest_loader.py      # Component manifest loading
│
├── actor/                       # Browser action generation agent
│   ├── actor.py                # Actor agent logic
│   ├── models.py               # ActionRequest, ActionResponse
│   └── llm_client.py           # LLM integration for action generation
│
└── clarifier/                   # Clarification question agent
    ├── clarifier.py            # Clarifier agent logic
    ├── models.py               # ClarifyRequest, ClarifyResponse
    └── llm_client.py           # LLM integration for clarifications
```

## 🚀 Quick Start

### Start the Server

```bash
cd llm
python server.py
```

The server runs on `http://0.0.0.0:8000` (accessible at `http://localhost:8000`)

### Testing the `/plan` Endpoint

Once the server is running, you can test the `/plan` endpoint using any of these methods:

#### Using curl

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "sid": "session-123",
    "text": "Create a login form and make the submit button blue"
  }'
```

#### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/plan",
    json={
        "sid": "session-123",
        "text": "Create a login form and make the submit button blue",
        "step_id": "session-123-root-0",
    }
)

print(response.json())
```

#### Using httpie

```bash
http POST http://localhost:8000/plan \
  sid="session-123" \
  text="Create a login form and make the submit button blue" \
  step_id="session-123-root-0"
```

#### Using the FastAPI Interactive Docs

1. Start the server
2. Open your browser to `http://localhost:8000/docs`
3. Find the `/plan` endpoint
4. Click "Try it out"
5. Enter your request body:
   ```json
   {
     "sid": "session-123",
     "text": "Create a login form and make the submit button blue",
     "step_id": "session-123-root-0"
   }
   ```
6. Click "Execute"

### API Endpoints

#### 1. `/plan` - Main Orchestration Endpoint (Recommended)

Execute the full pipeline: planner → agents → results.  
Optionally supply a `step_id` to continue a specific task thread (e.g., when replying to a
clarification). If omitted, the planner generates unique IDs for each downstream task.

**Request:**
```json
POST /plan
{
  "sid": "session-123",
  "text": "Create a login form and make the submit button blue",
  "step_id": "session-123-root-0"
}
```

**Response:**
```json
{
  "sid": "session-123",
  "results": [
    {
      "session_id": "session-123",
      "step_id": "session-123-step-1",
      "intent": "Create a login form | User wants to create a login UI component",
      "context": "Previous actions...",
      "result": "{\"type\": \"Form\", \"props\": {...}}",
      "agent_type": "edit"
    },
    {
      "session_id": "session-123",
      "step_id": "session-123-step-2",
      "intent": "Make submit button blue | User wants to change button color",
      "context": "Previous actions...",
      "result": "{\"type\": \"Button\", \"props\": {\"color\": \"blue\"}}",
      "agent_type": "edit"
    }
  ]
}
```

#### 2. `/decide` - Planner Only

Get task classification without executing agents

**Request:**
```json
POST /decide
{
  "sid": "session-123",
  "text": "Click the login button",
  "step_id": "session-123-root-0"
}
```

**Response:**
```json
[
  {
    "step_id": "session-123-step-1",
    "step_type": "act",
    "intent": "Click the login button | User wants to interact with login button",
    "context": "Previous actions in session..."
  }
]
```

> Provide `step_id` when you want the planner to reuse an existing identifier (e.g., when resuming
> after a clarification). If omitted, the planner generates a UUID.

#### 3. Individual Agent Endpoints

- `/edit` - Editor agent for UI components
- `/action` - Actor agent for browser actions
- `/clarify` - Clarifier agent for ambiguous requests

#### 4. Utility Endpoints

- `/queue/{sid}` - Get task queue status for a session
- `/health` - Health check

## 🔄 Request Flow

### Step-by-Step Execution

1. **Client sends request** to `/plan` with `sid` and `text`

2. **Orchestrator (`orchestrator.py`):**
   - Logs request received
   - Creates `DecideRequest` and calls planner

3. **Planner (`planner/planner.py`):**
   - Loads session history
   - Calls LLM to split text into tasks
   - Classifies each task as `edit`, `act`, or `clarify`
   - Enqueues tasks in session queue
   - Processes tasks sequentially
   - Returns `List[DecideResponse]`

4. **Orchestrator routes each task:**
   - `StepType.EDIT` → Editor agent → Returns `EditResponse` with `code` field
   - `StepType.ACT` → Actor agent → Returns `ActionResponse` with `action` field
   - `StepType.CLARIFY` → Clarifier agent → Returns `ClarifyResponse` with `reply` field and broadcasts the clarification text over the websocket bridge for frontend TTS playback

5. **Agent processes task:**
   - Receives intent and context
   - Calls LLM with agent-specific prompt
   - Saves result to session
   - Returns agent-specific response:
     - Editor: `EditResponse {code: str}` - Component JSON
     - Actor: `ActionResponse {action: str}` - Browser action
     - Clarifier: `ClarifyResponse {reply: str}` - Question (also streamed to the frontend over the DOM websocket so the UI can speak it immediately)

6. **Orchestrator normalizes and aggregates:**
   - Converts `EditResponse.code` → `AgentResult.result`
   - Converts `ActionResponse.action` → `AgentResult.result`
   - Converts `ClarifyResponse.reply` → `AgentResult.result`
   - Collects all into unified `List[AgentResult]`
   - Logs completion
   - Returns `PlanResponse` to client

## 📊 Data Models

### Core Request/Response Models

```python
from typing import Optional

# Main orchestration
class PlanRequest(BaseModel):
    sid: str          # Session ID
    text: str         # User query
    step_id: Optional[str] = None  # Optional client-supplied step identifier

class PlanResponse(BaseModel):
    sid: str
    results: List[AgentResult]

# Unified agent result (after orchestrator normalization)
class AgentResult(BaseModel):
    session_id: str
    step_id: str
    intent: str       # Enriched user intent
    context: str      # Session context
    result: str       # Normalized output (from code/action/reply)
    agent_type: str   # "edit", "act", or "clarify"

# Planner classification
class DecideResponse(BaseModel):
    step_id: str
    step_type: StepType  # EDIT, ACT, or CLARIFY
    intent: str
    context: str

# Agent-specific response models (before normalization)
class EditResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    code: str         # Component JSON as string

class ActionResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    action: str       # Browser action description

class ClarifyResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    reply: str        # Clarification question
```

**Note:** Each agent returns its own response type (`EditResponse`, `ActionResponse`, `ClarifyResponse`). The orchestrator normalizes these into the unified `AgentResult` format for the final response.

## 🔍 Logging

The system logs at INFO level:

```
2024-01-15 10:00:00 - Received /plan request for session: session-123
2024-01-15 10:00:00 - Plan request received for session: session-123
2024-01-15 10:00:00 - Calling planner for session: session-123
2024-01-15 10:00:01 - Planner identified 2 task(s) for session: session-123
2024-01-15 10:00:01 - Processing task 1/2 - Step ID: session-123-step-1, Type: StepType.EDIT
2024-01-15 10:00:01 - Routing to EDIT agent for step: session-123-step-1
2024-01-15 10:00:02 - EDIT agent completed for step: session-123-step-1
2024-01-15 10:00:02 - Processing task 2/2 - Step ID: session-123-step-2, Type: StepType.ACT
2024-01-15 10:00:02 - Routing to ACT agent for step: session-123-step-2
2024-01-15 10:00:03 - ACT agent completed for step: session-123-step-2
2024-01-15 10:00:03 - Plan execution completed for session: session-123 with 2 result(s)
2024-01-15 10:00:03 - Successfully completed /plan request for session: session-123
```

## 🛡️ Error Handling

- **Fail-fast strategy:** Any error in planner or agents immediately stops execution
- **HTTP 500** returned with detailed error message
- All errors logged with session context
- Session state preserved for debugging

## 📝 Session Management

- Each session has unique `sid`
- Session history stored in `planner/sessions/{sid}.json`
- Includes:
  - All prompts/requests
  - Task queue state
  - Agent responses (actions, edits, clarifications)
  - Timestamps for each operation

## 🧪 Testing

Each component has its own test suite:

- `planner/tests/` - Planner classification tests
- `editor/tests/` - Component generation tests
- `clarifier/tests/` - Clarification generation tests

Run tests:
```bash
cd llm/planner/tests && python runner.py
cd llm/editor/tests && python runner.py
cd llm/clarifier/tests && python runner.py
```

## 🔧 Configuration

### Environment Variables

Set these in your environment or `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

### LLM Configuration

Each agent has its own `llm_client.py` with model configuration:
- Model: GPT-4 or similar
- Temperature varies by agent type
- Max tokens configured per use case

## 🎯 Use Cases

### Single Task Request
```json
POST /plan {"sid": "user-1", "text": "Click the submit button"}
→ Returns 1 result with ACT agent action
```

### Multi-Task Request
```json
POST /plan {"sid": "user-1", "text": "Create a form and submit it"}
→ Returns 2 results: EDIT for form, ACT for submission
```

### Ambiguous Request
```json
POST /plan {"sid": "user-1", "text": "Update the profile"}
→ Returns 1 result with CLARIFY agent question
```

## 📚 Additional Documentation

- [Planner README](planner/README.md) - Detailed planner documentation
- [Editor README](editor/README.md) - Component generation details
- [Clarifier README](clarifier/README.md) - Clarification agent details

## 🤝 Contributing

When adding new agents:
1. Create agent directory with standard structure
2. Implement request/response models
3. Add routing logic in `orchestrator.py`
4. Update this README with new agent type

## 📄 License

[Your License Here]

