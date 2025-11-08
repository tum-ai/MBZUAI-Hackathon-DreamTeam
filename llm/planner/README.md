# Planner Agent

Decides what the assistant should do next: **edit** (modify website) | **act** (scroll/click) | **clarify** (ambiguous).

## Quick Start

**1. Setup** (from project root)

```bash
cd llm
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
```

**2. Configure** (create `llm/.env`)

```
K2_API_KEY=your_k2_api_key
```

**3. Run** (from project root)

```bash
source llm/venv/bin/activate
python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000
```

Server: http://localhost:8000

**Note:** The planner now uses the unified server at `llm/server.py` which provides both `/decide` (planner) and `/clarify` (clarifier) endpoints.

## API

**POST /decide**

```bash
curl -X POST http://localhost:8000/decide \
  -H "Content-Type: application/json" \
  -d '{"sid": "session-123", "text": "Add a hero section"}'
```

Response: `{step_id, step_type, intent, context}`

**GET /health** → `{"status": "healthy"}`

## How It Works

1. **Classifies intent**: edit/act/clarify using K2 Think LLM
2. **Enriches prompt**: adds explanation for next agent
3. **Manages context**: stores last 2 prompts, summarizes if >100 chars
4. **Tracks steps**: generates unique step_id per request

## Notes
- Summarization is triggered only if `len(previous_context) > 100`
- Sessions stored in `llm/sessions/` (gitignored); venv in `llm/venv/` (gitignored)
- CORS enabled; ready for frontend integration




curl -X POST "http://localhost:8000/decide" \
  -H "Content-Type: application/json" \
  -d '{
    "sid": "demo-session-456",
    "text": "Scroll down to the footer"
  }'





┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  (User speaks: "Add a hero section with title and signup")      │
└────────────────────────┬────────────────────────────────────────┘
                         │ POST /decide
                         │ {sid: "session-123", text: "Add a hero..."}
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    llm/server.py                                │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  @app.post("/decide")                                │       │
│  │  async def decide(request: DecideRequest)            │       │
│  └──────────────────┬───────────────────────────────────┘       │
└─────────────────────┼───────────────────────────────────────────┘
                      │ calls
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    llm/planner.py                               │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  def process_user_request(request)                   │       │
│  │    ├─► Step 1: Get previous context                  │       │
│  │    ├─► Step 2: Call LLM to classify intent           │       │
│  │    ├─► Step 3: Generate step ID                      │       │
│  │    ├─► Step 4: Enrich intent                         │       │
│  │    ├─► Step 5: Save to session                       │       │
│  │    └─► Step 6: Return response                       │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           │ Step 1             │ Step 2             │ Step 3,5
           ▼                    ▼                    ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │session_     │     │llm_         │     │session_     │
    │manager.py   │     │client.py    │     │manager.py   │
    │             │     │             │     │             │
    │get_previous_│     │classify_    │     │generate_    │
    │context()    │     │intent()     │     │step_id()    │
    │             │     │     │       │     │add_prompt_  │
    └─────────────┘     └─────┼───────┘     │to_session() │
                              │             └─────────────┘
                              ▼
                    ┌─────────────────┐
                    │  K2 Think API   │
                    │  (LLM Service)  │
                    └─────────────────┘




Flow Overview (concise)

1) Request hits server
- File: `llm/server.py`
- `POST /decide` → validates `DecideRequest` → calls `process_user_request()`

2) Planner orchestrates
- File: `llm/planner.py`
- Steps:
  - Get previous context: `get_previous_context(sid)`
  - Classify + explain: `classify_intent(text, previous_context)`
  - Generate id: `generate_step_id(sid)`
  - Build intent: `"user text | explanation"`
  - Choose context: `context_summary` (if summarized) or `previous_context`
  - Persist: `add_prompt_to_session(sid, text)`
  - Return `DecideResponse`

3) Deterministic summarization
- Rule: summarize only if `len(previous_context) > 100`
- If true: prompt asks LLM to produce `context_summary`
- If false: `context_summary` is set to `""`

4) Files/functions used
- `llm/server.py`: `decide()` endpoint (unified server with `/decide` and `/clarify`)
- `llm/planner/planner.py`: `process_user_request()`
- `llm/planner/llm_client.py`: `classify_intent()`
- `llm/planner/session_manager.py`: `get_previous_context()`, `add_prompt_to_session()`, `generate_step_id()`
- `llm/planner/models.py`: `DecideRequest`, `DecideResponse`, `StepType`

Example response
```json
{
  "step_id": "uuid",
  "step_type": "edit",
  "intent": "Add a hero section with a title and signup button | Clear explanation for next agent",
  "context": "Previous short context or summarized previous context"
}
```


python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000

# Start unified server (from project root)
python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000

# Run tests
./llm/venv/bin/python llm/planner/tests/runner.py

Call /decide (Planner)
curl -X POST http://localhost:8000/decide \  -H "Content-Type: application/json" \  -d '{"sid": "session-123", "text": "Make the button bigger"}'
Call /clarify (Clarifier)
curl -X POST http://localhost:8000/clarify \  -H "Content-Type: application/json" \  -d '{    "session_id": "session-123",    "step_id": "uuid",    "intent": "Change that | Ambiguous...",    "context": "Previous actions..."  }'
