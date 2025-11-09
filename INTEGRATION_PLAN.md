# 🚀 INTEGRATION & DOCKERIZATION MASTER PLAN
**Version:** 2.0 (Post-Git Pull)  
**Date:** November 9, 2025  
**Status:** Planning Complete → Ready for Execution

---

## 📊 CURRENT STATE ASSESSMENT (After Git Pull)

### ✅ **What's Already Implemented:**

#### 1. **LLM Module - MOSTLY COMPLETE**
- ✅ **Planner Agent**: Multi-task splitting, queue management, session handling
- ✅ **Editor Agent**: Single-step component generation with manifest loader
- ✅ **Actor Agent**: DOM snapshot integration via `fetch_dom_snapshot()` in server.py
- ✅ **Clarifier Agent**: Jarvis-style clarifications
- ✅ **Orchestrator**: Routes tasks to agents with timing metadata
- ✅ **WebSocket Integration**: `fetch_dom_snapshot()` connects to frontend via WebSocket
  - Location: `llm/server.py` lines 439-488
  - Configurable via `DOM_SNAPSHOT_WS_URL`, `DOM_SNAPSHOT_WS_HOST`, `DOM_SNAPSHOT_WS_PORT`
  - Actor calls this in `llm/actor/actor.py` line 29
- ✅ **System Prompt Generation**: `get_system_prompt()` builds dynamic sitemap from DOM
- ✅ **Action Types**: 11 action types (navigate, scroll, type, focus, submit, etc.)
- ⚠️ **Gap**: No HTTP client to POST actions to automation server (Actor generates JSON but doesn't execute)

#### 2. **Compiler Module - FULLY DOCKERIZED**
- ✅ **Two-Container Setup**: API server + Variations viewer
- ✅ **JSON Patch Endpoints**: 
  - `PATCH /project` - patches project.json
  - `PATCH /ast/{page_name}` - patches page AST (e.g., home.json)
  - Both endpoints apply patches AND trigger generation synchronously
- ✅ **Template System**: 5 template types with 4 palette variations each
- ✅ **Docker Volumes**: Shared between containers for template selection
- ✅ **Port Allocation**: 8000 (API), 5173-5177 (variations)
- ⚠️ **Gap**: Editor agent doesn't POST patches to compiler (generates but doesn't apply)

#### 3. **WebApp - NEEDS DOCKERIZATION**
- ✅ **React UI**: Liquid glass design with 3 screens
- ✅ **Routing**: React Router setup
- ✅ **Components**: GlassCard, VoiceControl, StatusIndicator, CanvasFrame
- ⚠️ **Gap**: No API integration (no fetch/axios calls to LLM server)
- ⚠️ **Gap**: No WebSocket client for DOM snapshot bridge
- ⚠️ **Gap**: Not dockerized (runs locally on port 5173)

#### 4. **Iframe Content - NEEDS DOCKERIZATION**
- ✅ **Vue Demo**: iPhone landing page with routing
- ✅ **Multi-page**: Home, Features, Compare, Pricing
- ⚠️ **Gap**: Not dockerized (runs locally on port 5174)

#### 5. **Automation Server - NEEDS DOCKERIZATION**
- ✅ **Playwright Integration**: Browser automation with BrowserManager
- ✅ **API Endpoints**: `/api/browser/dom`, `/api/browser/action`, `/api/refresh-iframe`
- ✅ **CORS Enabled**: Allows cross-origin requests
- ✅ **Async Operations**: Background tasks for refresh webhook
- ⚠️ **Gap**: Not dockerized (needs Playwright base image)
- ⚠️ **Gap**: Actor doesn't call its endpoints (integration missing)

#### 6. **Executor - NEEDS DOCKERIZATION**
- ✅ **WebSocket Bridge**: `/dom-snapshot` endpoint
- ✅ **Configurable**: Environment variables for WS URL
- ⚠️ **Gap**: Not dockerized
- ⚠️ **Gap**: Appears to be duplicate of functionality in llm/server.py (needs clarification)

---

## 🎯 CRITICAL INTEGRATION GAPS TO FILL

### Gap 1: Editor → Compiler Integration
**Status:** NOT CONNECTED  
**What exists:**
- Editor generates component JSON in `llm/editor/editor.py`
- Compiler has `PATCH /ast/{page_name}` endpoint ready to receive patches

**What's missing:**
- Editor outputs component JSON, not JSON Patch format (RFC 6902)
- No HTTP client in Editor to POST to compiler
- No error handling for compiler failures

**Required Work:**
1. Add `httpx` client to Editor module
2. Transform Editor output to JSON Patch format
3. POST to `http://compiler-api:8000/ast/home` (Docker network name)
4. Handle response and errors

---

### Gap 2: Actor → Automation Server Integration
**Status:** PARTIALLY CONNECTED (DOM fetch works, execution doesn't)  
**What exists:**
- Actor fetches DOM snapshot via `fetch_dom_snapshot()` ✅
- Actor generates action JSON via LLM ✅
- Automation server has `/api/browser/action` endpoint ready ✅

**What's missing:**
- Actor doesn't POST the generated action to automation server
- No HTTP client to execute actions

**Required Work:**
1. Add `httpx` client to Actor module
2. POST generated action to `http://automation:9000/api/browser/action`
3. Handle response (success/failure)
4. Return execution result to orchestrator

---

### Gap 3: WebApp → LLM Integration
**Status:** NOT CONNECTED  
**What exists:**
- LLM has `/plan` endpoint ready (orchestrator)
- WebApp has VoiceControl component

**What's missing:**
- No fetch/axios calls in WebApp
- No WebSocket client for DOM snapshot
- No environment variables for API URLs

**Required Work:**
1. Add API service layer in `webapp/src/services/api.js`
2. Connect VoiceControl to POST to `/plan` endpoint
3. Add WebSocket client for DOM snapshot bridge
4. Add env vars: `VITE_LLM_API_URL`, `VITE_WS_URL`

---

### Gap 4: Orchestrator → Services Integration
**Status:** ROUTES TO AGENTS BUT DOESN'T EXECUTE  
**What exists:**
- Orchestrator calls Editor, Actor, Clarifier agents ✅
- Returns unified AgentResult format ✅

**What's missing:**
- Orchestrator doesn't trigger actual service calls
- Editor results not sent to Compiler
- Actor results not sent to Automation Server

**Required Work:**
1. After Editor agent, POST patch to Compiler
2. After Actor agent, POST action to Automation Server
3. Add service URLs as environment variables
4. Add timeout and retry logic

---

## 🐳 DOCKERIZATION PLAN

### Service Inventory (7 Services Total)

| Service | Port(s) | Status | Dependencies |
|---------|---------|--------|--------------|
| **llm** | 8000 | ❌ Not dockerized | K2_API_KEY |
| **compiler-api** | 8001 (mapped from 8000) | ✅ Dockerized | - |
| **compiler-variations** | 5173-5177 | ✅ Dockerized | compiler-api, volumes |
| **automation** | 9000 | ❌ Not dockerized | Playwright, Node.js |
| **executor** | 8100 | ❌ Not dockerized | - |
| **webapp** | 5173 (80 internal) | ❌ Not dockerized | llm, executor |
| **iframe-content** | 5174 | ❌ Not dockerized | - |

---

## 📋 EXECUTION PLAN (11 Phases)

### **PHASE 1: Analyze Current State** ✅ COMPLETE
- [x] Read all README files
- [x] Analyze code after git pull
- [x] Identify implemented vs stubbed integrations
- [x] Document gaps

---

### **PHASE 2: Create Master Plan** 🔄 IN PROGRESS
- [x] Document current state
- [x] Define integration gaps
- [x] Plan dockerization strategy
- [ ] Save plan to repo (INTEGRATION_PLAN.md)

---

### **PHASE 3: Dockerize LLM Module** ⏳ READY
**Estimated Time:** 2 hours

**Files to Create:**
1. `llm/Dockerfile`
2. `llm/.dockerignore`
3. `llm/.env.docker` (template)

**Dockerfile Structure:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy LLM module
COPY llm/ ./llm/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["python", "-m", "uvicorn", "llm.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variables Needed:**
- `K2_API_KEY` (required for LLM calls)
- `DOM_SNAPSHOT_WS_HOST=webapp` (Docker network)
- `DOM_SNAPSHOT_WS_PORT=5173`
- `COMPILER_URL=http://compiler-api:8000` (for Editor integration)
- `AUTOMATION_URL=http://automation:9000` (for Actor integration)

**Testing:**
```bash
cd llm
docker build -t llm-service .
docker run -p 8000:8000 -e K2_API_KEY=$K2_API_KEY llm-service
curl http://localhost:8000/health
```

---

### **PHASE 4: Dockerize WebApp & Iframe** ⏳ READY
**Estimated Time:** 3 hours

#### WebApp Dockerfile (Multi-stage)
**File:** `webapp/Dockerfile`

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf** (for SPA routing):
```nginx
server {
  listen 80;
  location / {
    root /usr/share/nginx/html;
    index index.html;
    try_files $uri $uri/ /index.html;
  }
}
```

#### Iframe Content Dockerfile
**File:** `iframe-content/Dockerfile`

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5174
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5174"]
```

**Environment Variables:**
- `VITE_LLM_API_URL=http://llm:8000`
- `VITE_EXECUTOR_WS_URL=ws://executor:8100`

---

### **PHASE 5: Dockerize Automation Server** ⏳ READY
**Estimated Time:** 2 hours

**File:** `container/automation_server/Dockerfile`

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Install Node.js (for Vite subprocess)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy automation server code
COPY container/automation_server/ ./automation_server/

WORKDIR /app/automation_server

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:9000/ || exit 1

CMD ["python", "run_automation_server.py"]
```

**Environment Variables:**
- `AUTOMATION_SERVER_HOST=0.0.0.0`
- `AUTOMATION_SERVER_PORT=9000`
- `VUE_PROJECT_PATH=/tmp/active` (mounted volume)

---

### **PHASE 6: Dockerize Executor** ⏳ READY
**Estimated Time:** 1 hour

**File:** `executor/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY executor/server.py .
RUN pip install --no-cache-dir fastapi uvicorn websockets httpx

EXPOSE 8100

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8100/health || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8100"]
```

**Note:** May be redundant with llm/server.py WebSocket functionality. Need to clarify if this should be merged or kept separate.

---

### **PHASE 7: Create Root docker-compose.yml** ⏳ READY
**Estimated Time:** 3 hours

**File:** `/docker-compose.yml`

```yaml
version: '3.8'

services:
  # LLM Agent Orchestrator
  llm:
    build: ./llm
    container_name: llm-service
    ports:
      - "8000:8000"
    environment:
      - K2_API_KEY=${K2_API_KEY}
      - DOM_SNAPSHOT_WS_HOST=webapp
      - DOM_SNAPSHOT_WS_PORT=5173
      - COMPILER_URL=http://compiler-api:8000
      - AUTOMATION_URL=http://automation:9000
    depends_on:
      compiler-api:
        condition: service_healthy
      automation:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Compiler API (from existing Docker setup)
  compiler-api:
    build:
      context: .
      dockerfile: compiler/Dockerfile
    container_name: compiler-api
    ports:
      - "8001:8000"  # Map to 8001 to avoid conflict with LLM
    environment:
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - compiler-output:/app/compiler/output
      - compiler-inputs:/app/compiler/server/inputs
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/project"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Compiler Variations (from existing Docker setup)
  compiler-variations:
    build:
      context: .
      dockerfile: compiler/Dockerfile.variations
    container_name: compiler-variations
    ports:
      - "5173:5173"
      - "5174:5174"
      - "5175:5175"
      - "5176:5176"
      - "5177:5177"
    volumes:
      - template-variations:/tmp/selection
      - active-project:/tmp/active
    depends_on:
      compiler-api:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  # Automation Server (Browser Control)
  automation:
    build:
      context: .
      dockerfile: container/automation_server/Dockerfile
    container_name: automation-server
    ports:
      - "9000:9000"
    environment:
      - AUTOMATION_SERVER_HOST=0.0.0.0
      - AUTOMATION_SERVER_PORT=9000
      - VUE_PROJECT_PATH=/tmp/active
    volumes:
      - active-project:/tmp/active:ro
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Executor (WebSocket Bridge) - Optional if redundant
  executor:
    build: ./executor
    container_name: executor-service
    ports:
      - "8100:8100"
    environment:
      - EXECUTOR_SERVER_HOST=0.0.0.0
      - EXECUTOR_SERVER_PORT=8100
      - DOM_SNAPSHOT_WS_URL=ws://webapp:5173/dom-snapshot
    depends_on:
      - webapp
    networks:
      - app-network
    restart: unless-stopped

  # WebApp (React UI)
  webapp:
    build: ./webapp
    container_name: webapp-ui
    ports:
      - "5173:80"  # nginx serves on 80
    environment:
      - VITE_LLM_API_URL=http://localhost:8000
      - VITE_EXECUTOR_WS_URL=ws://localhost:8100
    depends_on:
      llm:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  # Iframe Content (Vue Demo)
  iframe-content:
    build: ./iframe-content
    container_name: iframe-content
    ports:
      - "5174:5174"
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  compiler-output:
  compiler-inputs:
  template-variations:
  active-project:
```

**Environment File:** `.env`
```bash
K2_API_KEY=your_api_key_here
```

**Start Script:** `docker-start.sh`
```bash
#!/bin/bash
set -e

case "$1" in
  up)
    docker-compose up -d
    echo "✅ All services started"
    echo "🌐 WebApp: http://localhost:5173"
    echo "🤖 LLM API: http://localhost:8000"
    echo "🏗️  Compiler: http://localhost:8001"
    ;;
  down)
    docker-compose down
    ;;
  logs)
    docker-compose logs -f ${2:-}
    ;;
  restart)
    docker-compose restart ${2:-}
    ;;
  clean)
    docker-compose down -v
    docker system prune -f
    ;;
  *)
    echo "Usage: $0 {up|down|logs|restart|clean}"
    exit 1
    ;;
esac
```

---

### **PHASE 8: Connect Editor to Compiler** ⏳ READY
**Estimated Time:** 3 hours

**File to Modify:** `llm/editor/editor.py`

**Changes Needed:**
1. Add httpx client
2. Convert component JSON to JSON Patch format
3. POST to compiler
4. Handle response

**Implementation:**
```python
import httpx
import os

COMPILER_URL = os.getenv("COMPILER_URL", "http://localhost:8001")

def apply_component_to_compiler(component: dict, page_name: str = "home") -> dict:
    """
    Convert component to JSON Patch and POST to compiler.
    
    Args:
        component: Generated component JSON
        page_name: Target page (default: home)
    
    Returns:
        Compiler response
    """
    # Convert component to JSON Patch (add to tree)
    patch = [
        {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": component
        }
    ]
    
    url = f"{COMPILER_URL}/ast/{page_name}"
    
    try:
        response = httpx.patch(url, json=patch, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to apply component to compiler: {e}")
        raise

# Update process_edit_request to call this
def process_edit_request(request: EditRequest) -> EditResponse:
    # ... existing code ...
    component = generate_component_direct(...)
    
    # NEW: Apply to compiler
    compiler_result = apply_component_to_compiler(component)
    
    response = EditResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        code=json.dumps(component, indent=2),
        compiler_status=compiler_result.get("status")  # Add to model
    )
    return response
```

**Model Update:** `llm/editor/models.py`
```python
class EditResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    code: str
    compiler_status: Optional[str] = None  # NEW
```

---

### **PHASE 9: Connect Actor to Automation Server** ⏳ READY
**Estimated Time:** 2 hours

**File to Modify:** `llm/actor/actor.py`

**Changes Needed:**
1. Add httpx client
2. POST generated action to automation server
3. Handle response

**Implementation:**
```python
import httpx
import os
import json

AUTOMATION_URL = os.getenv("AUTOMATION_URL", "http://localhost:9000")

async def execute_browser_action(action_json: str) -> dict:
    """
    Execute generated action via automation server.
    
    Args:
        action_json: JSON string of browser action
    
    Returns:
        Automation server response
    """
    try:
        action = json.loads(action_json)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid action JSON: {e}")
        return {"status": "error", "message": "Invalid action format"}
    
    url = f"{AUTOMATION_URL}/api/browser/action"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=action)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to execute browser action: {e}")
        return {"status": "error", "message": str(e)}

# Update process_action_request
async def process_action_request(request: ActionRequest) -> ActionResponse:
    # ... existing code ...
    action = generate_action(...)
    
    # NEW: Execute action
    execution_result = await execute_browser_action(action)
    
    session["actions"][request.step_id] = {
        "intent": request.intent,
        "context": request.context,
        "action": action,
        "execution": execution_result  # NEW
    }
    
    response = ActionResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        action=action,
        execution_status=execution_result.get("status")  # NEW
    )
    return response
```

**Model Update:** `llm/actor/models.py`
```python
class ActionResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    action: str
    execution_status: Optional[str] = None  # NEW
```

---

### **PHASE 10: Test Full System** ⏳ READY
**Estimated Time:** 4 hours

**Test Scenarios:**

1. **Component Generation Flow:**
   ```bash
   # Start all services
   ./docker-start.sh up
   
   # Test Editor → Compiler
   curl -X POST http://localhost:8000/plan \
     -H "Content-Type: application/json" \
     -d '{"sid": "test-1", "text": "Add a hero section with a title"}'
   
   # Verify component appears in http://localhost:5177
   ```

2. **Browser Action Flow:**
   ```bash
   # Test Actor → Automation
   curl -X POST http://localhost:8000/plan \
     -H "Content-Type: application/json" \
     -d '{"sid": "test-2", "text": "Click the submit button"}'
   
   # Check automation logs
   docker logs automation-server -f
   ```

3. **Multi-Step Flow:**
   ```bash
   # Test complex workflow
   curl -X POST http://localhost:8000/plan \
     -H "Content-Type: application/json" \
     -d '{"sid": "test-3", "text": "Add a contact form and then fill it with name John"}'
   ```

4. **WebApp Integration:**
   ```javascript
   // In webapp VoiceControl component
   const handleVoiceCommand = async (transcript) => {
     const response = await fetch('http://localhost:8000/plan', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({sid: sessionId, text: transcript})
     });
     const result = await response.json();
     console.log('Plan result:', result);
   };
   ```

**Success Criteria:**
- [ ] All 7 containers start without errors
- [ ] Health checks pass for all services
- [ ] Editor → Compiler: Component appears in generated Vue files
- [ ] Actor → Automation: Browser actions execute
- [ ] WebApp can submit voice commands
- [ ] Logs show proper inter-service communication
- [ ] Can rebuild entire system with `docker-compose up --build`

---

### **PHASE 11: Production Readiness** ⏳ READY
**Estimated Time:** 4 hours

**Tasks:**

1. **Logging & Monitoring:**
   - [ ] Structured JSON logging in all services
   - [ ] Centralized log aggregation (optional: ELK stack)
   - [ ] Add Prometheus metrics endpoints
   - [ ] Create Grafana dashboards

2. **Security:**
   - [ ] API key authentication between services
   - [ ] Rate limiting on public endpoints
   - [ ] Input validation and sanitization
   - [ ] CORS configuration review
   - [ ] Secrets management (Docker secrets or HashiCorp Vault)

3. **Reliability:**
   - [ ] Retry logic for all HTTP calls
   - [ ] Circuit breakers for external services
   - [ ] Graceful degradation (if compiler down, still accept commands)
   - [ ] Database for persistent session storage (optional: Redis)

4. **Documentation:**
   - [ ] `/DEPLOYMENT.md` - Complete deployment guide
   - [ ] `/API_REFERENCE.md` - All endpoints documented
   - [ ] `/ARCHITECTURE.md` - System architecture diagram
   - [ ] `/TROUBLESHOOTING.md` - Common issues and solutions
   - [ ] Update all module READMEs with Docker instructions

5. **Testing:**
   - [ ] Integration test suite
   - [ ] Load testing (k6 or Artillery)
   - [ ] Chaos engineering (kill containers, test recovery)

---

## 📈 PROGRESS TRACKING

### Overall Progress: 18% Complete

- ✅ Phase 1: Analysis (100%)
- 🔄 Phase 2: Planning (90%)
- ⏳ Phase 3-11: Not Started (0%)

### Estimated Total Time: 24 hours (3 days)

---

## 🚨 CRITICAL NOTES

1. **Executor Service Redundancy:** 
   - `executor/server.py` has similar WebSocket functionality to `llm/server.py`
   - Need to decide: merge or keep separate?
   - If keeping separate, clarify roles

2. **Port Conflicts:**
   - LLM and Compiler API both want port 8000
   - Solution: Map compiler to 8001 externally

3. **Volume Sharing:**
   - `active-project` volume shared between compiler-variations and automation
   - Automation needs read-only access

4. **K2 API Key:**
   - Required for all LLM calls
   - Must be in `.env` file
   - Never commit to git

5. **Network Names:**
   - Use Docker network names (e.g., `compiler-api`) not `localhost`
   - Update all environment variables accordingly

---

## � HACKATHON SPRINT PLAN (3 HOURS)

**REVISED PRIORITIES - Focus on Demo-Ready Integration**

### Sprint 1: LLM Planning Integration ⏱️ 30 min
**Goal:** Ensure `/plan` endpoint orchestrator works end-to-end

**Tasks:**
1. ✅ Verify Planner → Editor/Actor/Clarifier routing works
2. ✅ Test with curl: `curl -X POST http://localhost:8000/plan -H "Content-Type: application/json" -d '{"sid":"test","text":"Add a button"}'`
3. ✅ Check logs show correct agent routing
4. ✅ Verify timing metadata is returned

**Success:** Orchestrator returns AgentResult with code/action/reply

---

### Sprint 2: Frontend API Integration ⏱️ 45 min
**Goal:** WebApp can send commands to LLM and display results

**Files to Modify:**
- `webapp/src/services/api.js` (CREATE)
- `webapp/src/components/VoiceControl.jsx` (UPDATE)
- `webapp/src/hooks/useWebSocket.js` (CREATE - for DOM snapshot)

**Key Code:**
```javascript
// webapp/src/services/api.js
export const sendPlanRequest = async (sessionId, text) => {
  const response = await fetch('http://localhost:8000/plan', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({sid: sessionId, text})
  });
  return response.json();
};
```

**Success:** User can speak → See response in console → Show in UI

---

### Sprint 3: Editor → Compiler ⏱️ 30 min
**Goal:** Component generation actually modifies the site

**File to Modify:** `llm/editor/editor.py`

**Add:**
```python
import httpx
import os

COMPILER_URL = os.getenv("COMPILER_URL", "http://localhost:8001")

async def apply_to_compiler(component: dict, page: str = "home"):
    patch = [{"op": "add", "path": "/tree/slots/default/-", "value": component}]
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.patch(f"{COMPILER_URL}/ast/{page}", json=patch)
        return response.json()
```

**Success:** "Add a button" → Component appears in http://localhost:5177

---

### Sprint 4: Actor → Automation ⏱️ 30 min
**Goal:** Browser actions actually execute

**File to Modify:** `llm/actor/actor.py`

**Add:**
```python
import httpx
AUTOMATION_URL = os.getenv("AUTOMATION_URL", "http://localhost:9000")

async def execute_action(action_json: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{AUTOMATION_URL}/api/browser/action",
            json=json.loads(action_json)
        )
        return response.json()
```

**Success:** "Click the button" → Browser action executes

---

### Sprint 5: End-to-End Demo ⏱️ 30 min
**Goal:** Record working demo

**Test Workflow:**
1. Start all servers (compiler already running)
2. Start LLM: `cd llm && python -m uvicorn llm.server:app --port 8000`
3. Start WebApp: `cd webapp && npm run dev`
4. Start Automation: `cd container/automation_server && python run_automation_server.py`
5. Demo: Voice → "Add a hero section" → See it appear
6. Demo: Voice → "Click the submit button" → See action execute

**Success:** 2 working demos recorded

---

### Sprint 6: Buffer ⏱️ 15 min
**Reserved for critical bugs**

---

## ⚡ IMMEDIATE ACTION PLAN

**RIGHT NOW (Start Timer):**

1. **Verify LLM Server Works** (5 min)
   ```bash
   cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam
   source llm/venv/bin/activate
   python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000
   ```
   
   Test:
   ```bash
   curl -X POST http://localhost:8000/plan \
     -H "Content-Type: application/json" \
     -d '{"sid":"demo","text":"Add a button that says Click Me"}'
   ```

2. **If Test Works** → Move to Sprint 2 (Frontend)
3. **If Test Fails** → Debug orchestrator (Sprint 1)

---

**SKIP FOR DEMO:**
- ❌ Dockerization (no time)
- ❌ Production hardening
- ❌ Complete error handling
- ❌ Executor service (redundant with llm/server.py WebSocket)
- ❌ Full test coverage

**FOCUS ON:**
- ✅ One working component generation flow
- ✅ One working browser action flow
- ✅ Visible results in UI
- ✅ Demo video

---

**Last Updated:** November 9, 2025 (HACKATHON MODE)  
**Time Constraint:** 3 hours MAX  
**Goal:** Working demo, not production system
