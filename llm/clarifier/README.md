# Clarifier Agent 🤖

A Jarvis-style clarification agent that generates contextual, witty responses when user requests are ambiguous.

## Overview

The Clarifier Agent receives ambiguous user requests (identified by the Planner Agent as `step_type: "clarify"`) and generates friendly, contextual clarification questions in the style of Jarvis from Iron Man - confident, helpful, with a touch of tech bro humor.

## Architecture

```
clarifier/
├── models.py          # Pydantic models for request/response
├── llm_client.py      # K2-Think LLM integration with Jarvis prompt
├── clarifier.py       # Main processing logic with session integration
└── README.md          # This file
```

### How It's Built

1. **`models.py`** - Defines the data structures:
   - `ClarifyRequest`: Input model with session_id, step_id, intent, context
   - `ClarifyResponse`: Output model that adds the `reply` field

2. **`llm_client.py`** - LLM integration:
   - Reuses K2-Think client setup from planner
   - Custom Jarvis-style prompt that emphasizes:
     - Context awareness (references previous actions)
     - Clear, direct questions
     - Personality (witty but professional)
   - Handles model output parsing (including XML tags)

3. **`clarifier.py`** - Core logic:
   - Calls LLM to generate clarification reply
   - Saves clarifications to session file under `clarifications` object
   - Returns complete response with reply

## Usage

### API Endpoint

**POST** `/clarify`

Accessible from the unified server at `/llm/server.py`

### Request Format

```json
{
  "session_id": "session-123",
  "step_id": "02974b8d-73e5-53f3-aac0-c35de1a1217a",
  "intent": "Change that | User intends to modify a website element but refers to it as 'that', which is ambiguous. The previous context mentions the footer section and submit button, so clarification is needed to identify exactly which element the user wants to change.",
  "context": "Scroll down to the footer section | Click on the submit button"
}
```

> **Tip:** The `step_id` should match the identifier emitted by the planner. When the clarifier
> responds through the orchestrator, this same `step_id` is broadcast to the frontend so a
> follow-up user reply can resume the task queue from the correct point.

### Response Format

```json
{
  "session_id": "session-123",
  "step_id": "02974b8d-73e5-53f3-aac0-c35de1a1217a",
  "intent": "Change that | User intends to modify...",
  "context": "Scroll down to the footer section | Click on the submit button",
  "reply": "Got it, but which 'that' are we working on? The footer section you scrolled to or the submit button you clicked? Let me know so I can get the right element adjusted."
}
```

### Example cURL

```bash
# Usually invoked automatically by the orchestrator, but can be called directly for testing.
curl -X POST http://localhost:8000/clarify \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-a",
    "step_id": "02974b8d-73e5-53f3-aac0-c35de1a1217a",
    "intent": "Change that | User intends to modify a website element but refers to it as 'that', which is ambiguous.",
    "context": "Scroll down to the footer section | Click on the submit button"
  }'
```

### Example Python

```python
import requests

response = requests.post(
    "http://localhost:8000/clarify",
    json={
        "session_id": "my-session",
        "step_id": "unique-step-id",
        "intent": "Make it bigger | User wants to increase size but doesn't specify what",
        "context": "Added logo image | Changed header text"
    }
)

print(response.json()["reply"])
# Output: "Alright, just to make sure I've got this right - you want to make 
# the logo image or the header text bigger? Let me know which one."
```

## Integration Flow

1. **Planner Agent** (`/plan` orchestrator) classifies user intent.
2. If `step_type == "clarify"`, the orchestrator invokes the Clarifier Agent directly.
3. Clarifier generates a Jarvis-style question, saves it to the session file, and returns the reply.
4. The server broadcasts the clarification text (with `session_id`/`step_id`) over the DOM websocket bridge so the frontend can play TTS immediately.
5. The frontend collects the user’s clarification and calls `/plan` again with the same `session_id` and the clarifier `step_id`, allowing the planner to resume the queue from that point.

## Session Storage

Clarifications are automatically saved to the session file:

```json
{
  "sid": "session-123",
  "prompts": [...],
  "clarifications": {
    "step-id-1": {
      "intent": "...",
      "context": "...",
      "reply": "..."
    }
  }
}
```

## Jarvis Personality

The agent is designed to sound like Jarvis from Iron Man:
- **Confident**: "Alright, let me get this straight..."
- **Contextual**: References previous actions naturally
- **Clear**: Gets straight to the point
- **Witty**: Light humor but stays professional
- **Helpful**: Makes it easy for users to answer

Example responses:
- "Got it, but which 'that' are we working with?"
- "Okay, I need a quick clarification here..."
- "Just to make sure I've got this right..."

## Dependencies

- FastAPI (HTTP server)
- Pydantic (data validation)
- OpenAI Python SDK (K2-Think API client)
- dotenv (environment variables)

Requires `K2_API_KEY` in environment (loaded from `.env` file).

## Running the Server

**Important:** Run from the project root directory, not from the `llm` folder.

```bash
# From project root
cd /path/to/MBZUAI-Hackathon-DreamTeam

# Using venv python
./llm/venv/bin/python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000

# Or if you have the venv activated
python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000
```

Both `/decide` and `/clarify` endpoints will be available.

**Note:** The old server at `llm.planner.server:app` only has the `/decide` endpoint. Use `llm.server:app` to get both endpoints.

