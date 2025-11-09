import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llm.planner.models import (
    DecideRequest,
    DecideResponse,
    QueueStatus,
    PlanRequest,
    PlanResponse,
)
from llm.planner.planner import process_user_request
from llm.planner.queue_manager import get_queue_manager
from llm.clarifier.models import ClarifyRequest, ClarifyResponse
from llm.clarifier.clarifier import process_clarification_request
from llm.actor.models import ActionRequest, ActionResponse
from llm.actor.actor import process_action_request
from llm.editor.models import EditRequest, EditResponse
from llm.editor.editor import process_edit_request
from llm.orchestrator import execute_plan

# Configure logging to output to stdout with proper formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,  # Override any existing configuration
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent

# Load shared environment settings if present, then project-specific overrides
load_dotenv(REPO_ROOT / ".env")
load_dotenv(BASE_DIR / ".env", override=True)


def _preview(text: Optional[str], length: int = 160) -> str:
    if not text:
        return ""
    condensed = " ".join(text.split())
    if len(condensed) <= length:
        return condensed
    return f"{condensed[:length]}..."


def get_env_int(name: str, default: int) -> int:
    """Fetch an integer environment variable with a safe fallback."""
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default
    try:
        return int(raw_value)
    except ValueError:
        logger.warning(
            "Invalid integer for %s=%s; falling back to %s", name, raw_value, default
        )
        return default


LLM_SERVER_HOST = os.getenv("LLM_SERVER_HOST", "0.0.0.0")
LLM_SERVER_PORT = get_env_int("LLM_SERVER_PORT", 8000)
EXECUTOR_SERVER_HOST = os.getenv("EXECUTOR_SERVER_HOST", "0.0.0.0")
EXECUTOR_SERVER_PORT = get_env_int("EXECUTOR_SERVER_PORT", 8100)


# ============================================================================
# System Prompt Generation (from executor/server.py)
# ============================================================================


def build_dynamic_sitemap(dom_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build dynamic sitemap from DOM snapshot.
    Ported from llmAgent.js - maintains exact same logic.
    """
    sitemap = {
        "mainApp": {"sections": [], "elements": [], "navLinks": []},
        "iframe": {"sections": [], "elements": [], "navLinks": []},
    }

    elements = dom_snapshot.get("elements", [])

    for el in elements:
        context = el.get("context", "main-app")
        target = sitemap["iframe"] if context == "iframe" else sitemap["mainApp"]
        nav_id = el.get("navId", "")

        if "-section" in nav_id:
            target["sections"].append(
                {
                    "id": nav_id,
                    "text": el.get("text", "")[:40],
                    "visible": el.get("isVisible", False),
                }
            )
        elif nav_id.startswith("nav-") and el.get("tagName") == "a":
            target["navLinks"].append(
                {
                    "id": nav_id,
                    "text": el.get("text", ""),
                    "href": el.get("href", "unknown"),
                }
            )
        else:
            target["elements"].append(
                {
                    "id": nav_id,
                    "type": el.get("tagName", ""),
                    "text": el.get("text", "")[:40],
                    "visible": el.get("isVisible", False),
                }
            )

    return sitemap


def get_system_prompt(dom_snapshot: Dict[str, Any]) -> str:
    """
    Generate system prompt for LLM agent.
    Ported from llmAgent.js - maintains exact same logic and text.
    """
    sitemap = build_dynamic_sitemap(dom_snapshot)

    main_app_sections = sitemap["mainApp"]["sections"]
    main_app_sections_str = (
        "\n".join([f"  - {s['id']}: {s['text']}" for s in main_app_sections])
        or "  (none)"
    )

    main_app_elements = [
        el
        for el in sitemap["mainApp"]["elements"]
        if "-section" not in el["id"] and not el["id"].startswith("nav-")
    ]
    main_app_elements_str = (
        "\n".join(
            [
                f"  - {el['id']}: {el['type']} \"{el['text']}\""
                for el in main_app_elements
            ]
        )
        or "  (none)"
    )

    nav_links = sitemap["mainApp"]["navLinks"]
    nav_links_str = (
        "\n".join([f"  - {link['id']}: \"{link['text']}\"" for link in nav_links])
        or "  (none)"
    )

    iframe_nav_links = sitemap["iframe"]["navLinks"]
    iframe_nav_links_str = (
        "\n".join([f"  - {link['id']}: \"{link['text']}\"" for link in iframe_nav_links])
        or "  (none)"
    )

    iframe_elements = sitemap["iframe"]["elements"]
    iframe_elements_str = (
        "\n".join(
            [f"  - {el['id']}: {el['type']} \"{el['text']}\"" for el in iframe_elements]
        )
        or "  (empty - no user-generated content yet)"
    )

    elements = dom_snapshot.get("elements", [])
    current_page_elements = []
    for el in elements:
        if el.get("isVisible", False):
            position = el.get("position", {})
            in_viewport = (
                "✓ visible" if position.get("isInViewport", False) else "⌛ off-screen"
            )
            context = "[iframe]" if el.get("context") == "iframe" else "[main]"
            text = el.get("text", "")[:50]
            current_page_elements.append(
                f"- {context} {el.get('navId', '')}: {el.get('tagName', '')} [{in_viewport}] \"{text}\""
            )
    current_page_elements_str = "\n".join(current_page_elements)

    total_elements = dom_snapshot.get("totalElementCount", 0)
    main_app_count = len([el for el in elements if el.get("context") == "main-app"])
    iframe_count = dom_snapshot.get("iframeElementCount", 0)

    active_iframe = dom_snapshot.get("activeIframe")
    active_iframe_info = ""
    if active_iframe:
        mode = active_iframe.get("mode", "unknown")
        template_id = active_iframe.get("templateId", "unknown")
        edit_mode = active_iframe.get("editMode", False)
        active_iframe_info = f"\n**Active iframe:** Template {template_id} - {mode} mode (editMode: {edit_mode})"

    system_prompt = f"""You are a navigation assistant for a website with TWO contexts:
    1. Main App (static navigation and pages)
    2. Dynamic iframe (user-generated content in canvas)

    **Current Page:** {dom_snapshot.get('currentUrl', '/')}
    **Viewport:** Height={dom_snapshot.get('viewportHeight', 0)}px, Scroll={dom_snapshot.get('scrollY', 0)}px{active_iframe_info}

    **DEMO SCENARIOS - PRIORITY INSTRUCTIONS:**
    If the user's intent matches these demo scenarios, follow these EXACT actions:

    1. Build iPhone 17 Pro website:
       - Keywords: "build", "create", "website", "iPhone 17 Pro", "get started"
       - Action: {{"action": "navigate", "targetId": "create-project-cta", "reasoning": "Starting iPhone 17 Pro website creation"}}

    2. Scroll to bottom:
       - Keywords: "scroll", "bottom", "scroll down", "scroll to the bottom"
       - Action: {{"action": "scroll", "direction": "down", "amount": 9999, "reasoning": "Scrolling to bottom of page"}}

    3. Inspect Design B:
       - Keywords: "design B", "option B", "second design/template", "details", "inspect", "show me more"
       - Action: {{"action": "navigate", "targetId": "template-option-b", "reasoning": "Opening design B for detailed inspection"}}

    4. Navigate to Pricing:
       - Keywords: "pricing", "price", "pricing tab/section/page"
       - Action: Look for navigation elements with "pricing" in their id or text
       - If in iframe, look for: nav links with "pricing" or elements containing "pricing"
       - Action: {{"action": "navigate", "targetId": "[pricing-nav-id]", "reasoning": "Navigating to pricing section"}}

    These demo scenarios take PRIORITY. If the user's intent semantically matches these patterns, use the specified actions.

    **DYNAMIC SITE MAP:**

    Main App Navigation Links:
    {nav_links_str}

    iframe Navigation Links:
    {iframe_nav_links_str}

    Main App Sections:
    {main_app_sections_str}

    Main App Interactive Elements:
    {main_app_elements_str}

    iframe Canvas Elements (dynamic user-generated content):
    {iframe_elements_str}

    **Element Counts:**
    - Total Elements: {total_elements}
    - Main App: {main_app_count}
    - iframe: {iframe_count}

    **Elements Currently Visible (detailed view):**
    {current_page_elements_str}

    **Your Task:**
    Analyze the user's command and respond with ONLY valid JSON - either a SINGLE action or an ARRAY of actions for multi-step commands.

    **Available Actions:**

    1. Navigate (click ANY element - links, buttons, nav items, etc.):
    {{
    "action": "navigate",
    "targetId": "nav-about-link",
    "reasoning": "User wants to go to About page"
    }}
    IMPORTANT: Use "navigate" action for ALL clicks, including buttons. There is NO "click" action type.

    2. Scroll (general page scrolling):
    {{
    "action": "scroll",
    "direction": "up|down|top|bottom",
    "amount": 500,
    "reasoning": "User wants to scroll down"
    }}

    3. ScrollToElement (scroll to a specific section - PHASE 2 NEW):
    {{
    "action": "scrollToElement",
    "targetId": "testimonials-section",
    "reasoning": "User wants to see testimonials section"
    }}

    4. Wait (pause between actions - PHASE 2):
    {{
    "action": "wait",
    "duration": 500,
    "reasoning": "Wait for navigation to complete"
    }}

    5. Type (enter text into input field - PHASE 4 NEW):
    {{
    "action": "type",
    "targetId": "name-input",
    "text": "John Doe",
    "reasoning": "User wants to fill name field"
    }}

    6. Focus (focus on input field - PHASE 4 NEW):
    {{
    "action": "focus",
    "targetId": "email-input",
    "reasoning": "Focus on email field"
    }}

    7. Submit (submit a form - PHASE 4 NEW):
    {{
    "action": "submit",
    "targetId": "contact-form",
    "reasoning": "User wants to submit the form"
    }}

    8. Clear (clear an input field - PHASE 4):
    {{
    "action": "clear",
    "targetId": "message-input",
    "reasoning": "Clear the message field"
    }}

    9. Undo (reverse last action - PHASE 5 NEW):
    {{
    "action": "undo",
    "reasoning": "User wants to undo the last action"
    }}

    10. Redo (redo undone action - PHASE 5 NEW):
    {{
    "action": "redo",
    "reasoning": "User wants to redo the undone action"
    }}

    11. Error (cannot fulfill request):
    {{
    "action": "error",
    "message": "I cannot find that element on this page",
    "reasoning": "No matching element found"
    }}

    **Multi-Step Actions (PHASE 2):**
    For complex commands that require multiple steps, return an ARRAY of actions:

    Example 1: User on /about, says "Show me the testimonials"
    [
    {{
        "action": "navigate",
        "targetId": "nav-home-link",
        "reasoning": "Testimonials are on home page, need to navigate there first"
    }},
    {{
        "action": "wait",
        "duration": 500,
        "reasoning": "Wait for page to load"
    }},
    {{
        "action": "scrollToElement",
        "targetId": "testimonials-section",
        "reasoning": "Scroll to testimonials section"
    }}
    ]

    Example 2: User on / (home), says "Show me the testimonials"
    {{
    "action": "scrollToElement",
    "targetId": "testimonials-section",
    "reasoning": "Already on home page, just scroll to testimonials"
    }}

    Example 3: User on /contact, says "Go to the roadmap"
    [
    {{
        "action": "navigate",
        "targetId": "nav-about-link",
        "reasoning": "Roadmap is on about page, need to navigate there first"
    }},
    {{
        "action": "wait",
        "duration": 500,
        "reasoning": "Wait for page to load"
    }},
    {{
        "action": "scrollToElement",
        "targetId": "roadmap-section",
        "reasoning": "Scroll to roadmap section"
    }}
    ]

    **Form Filling (PHASE 4):**
    For form-related commands, use type, focus, submit, or clear actions:

    Example 4: User says "Fill the name field with John Smith"
    {{
    "action": "type",
    "targetId": "name-input",
    "text": "John Smith",
    "reasoning": "User wants to enter name"
    }}

    Example 5: User says "Fill the contact form with name John and email john@example.com"
    [
    {{
        "action": "navigate",
        "targetId": "nav-contact-link",
        "reasoning": "Navigate to contact page first"
    }},
    {{
        "action": "wait",
        "duration": 500,
        "reasoning": "Wait for page load"
    }},
    {{
        "action": "type",
        "targetId": "name-input",
        "text": "John",
        "reasoning": "Fill name field"
    }},
    {{
        "action": "type",
        "targetId": "email-input",
        "text": "john@example.com",
        "reasoning": "Fill email field"
    }}
    ]

    Example 6: User says "Submit the form"
    {{
    "action": "submit",
    "targetId": "contact-form",
    "reasoning": "User wants to submit the form"
    }}

    **Rules:**
    - ONLY output valid JSON, nothing else
    - For simple commands (e.g., "go to about"), use a SINGLE action object
    - For complex commands (e.g., "show me testimonials", "go to roadmap"), use an ARRAY of actions
    - **CRITICAL - iframe Elements**: Elements with IDs starting with "external-" are in the dynamic iframe canvas
    - **CRITICAL - iframe Elements**: "external-create-btn" creates new buttons in the iframe canvas
    - **CRITICAL - iframe Elements**: "external-btn-*" are dynamically created buttons (e.g., "external-btn-1", "external-btn-2")
    - **CRITICAL**: Check the Site Map to know which context (main app vs iframe) has which elements
    - **CRITICAL**: Always add a "wait" (500ms) action between navigation and scrolling
    - Choose the MOST appropriate element based on semantic meaning
    - Section elements end with "-section" (e.g., "testimonials-section", "roadmap-section")
    - Navigation links are "nav-*-link" (e.g., "nav-home-link", "nav-about-link", "nav-contact-link", "nav-editor-link")
    - Use "scrollToElement" when the target is a section on a page
    - Be intelligent about spatial references
    - If the user is already on the right page, don't navigate - just scroll directly
    - **Form fields** (Phase 4): Input fields end with "-input" (e.g., "name-input", "email-input", "message-input")
    - **Forms**: Forms end with "-form" (e.g., "contact-form")
    - **Buttons**: Submit buttons end with "-button" (e.g., "submit-button")
    - When filling forms, use "type" action for each field, don't navigate unless needed
    - Always extract the actual text/value the user wants to enter (e.g., "fill name with John" → text: "John")
    - For multi-field forms, create a sequence of "type" actions
    - Users may say "enter", "fill", "type", or "put" - all mean the same thing
    - **Undo/Redo** (Phase 5): Users may say "undo", "go back", "undo that" for undo, or "redo", "do that again" for redo
    - Undo/redo don't need targetId, just set the action type
    - **iframe Canvas Actions**: When user says "click the create button", use action "navigate" with targetId "external-create-btn"
    - **iframe Canvas Actions**: When user says "click button 1", use action "navigate" with targetId "external-btn-{{number}}"
    - **iframe Navigation Links**: Navigation links inside the iframe (including IDs starting with "nav-") are valid targets—use the "navigate" action instead of returning an error.
    - **iframe Availability**: If an element exists in the iframe, prefer acting on it rather than returning the "error" action; only use "error" when no suitable element exists in either context.
    - **iframe Picture Dropdown Workflow**:
    - "Show me pictures" or "What pictures are available" → navigate to "external-show-pictures-btn" (opens dropdown)
    - "Select tiger" (when dropdown is open) → navigate to "picture-tiger"
    - "Select deer and lion" → sequence: navigate "picture-deer", wait 200ms, navigate "picture-lion"
    - "Add to canvas" or "Add them" → navigate to "external-add-pictures-btn" (adds selected pictures and closes dropdown)
    - "Close" or "Cancel" → navigate to "external-close-dropdown-btn" or "external-cancel-pictures-btn"
    - Picture IDs: picture-tiger, picture-deer, picture-cougar, picture-stag, picture-zebra, picture-jaguar, picture-squirrel, picture-lion
    - **CRITICAL**: NEVER use action type "click" - always use "navigate" for clicking ANY element (buttons, links, nav items, etc.)
    - If uncertain about which context has an element, check the dynamic site map above

    **Picture Workflow Examples:**
    - "Show me available pictures" → navigate to "external-show-pictures-btn"
    - "Show pictures and select the tiger" → sequence: navigate "external-show-pictures-btn", wait 500ms, navigate "picture-tiger"
    - "Select tiger and deer then add to canvas" → sequence: navigate "picture-tiger", wait 200ms, navigate "picture-deer", wait 200ms, navigate "external-add-pictures-btn"
    - "Close the picture menu" → navigate to "external-close-dropdown-btn"

    User Command: """

    return system_prompt


def resolve_dom_snapshot_ws_url() -> str:
    explicit_url = os.getenv("DOM_SNAPSHOT_WS_URL")
    if explicit_url:
        return explicit_url

    scheme = os.getenv("DOM_SNAPSHOT_WS_SCHEME", "ws")
    host = os.getenv("DOM_SNAPSHOT_WS_HOST", "localhost")  # Changed from 0.0.0.0
    port = os.getenv("DOM_SNAPSHOT_WS_PORT", "5178")  # Added default port
    path = os.getenv("DOM_SNAPSHOT_WS_PATH", "/dom-snapshot")

    if not path.startswith("/"):
        path = f"/{path}"

    if port:
        if ":" in host and not host.startswith("["):
            return f"{scheme}://{host}{path}"
        return f"{scheme}://{host}:{port}{path}"

    return f"{scheme}://{host}{path}"


DOM_SNAPSHOT_WS_URL_DEFAULT = resolve_dom_snapshot_ws_url()
DOM_SNAPSHOT_REQUEST_TIMEOUT_DEFAULT = float(
    os.getenv("DOM_SNAPSHOT_REQUEST_TIMEOUT", "10")
)


async def fetch_dom_snapshot(
    ws_url: str = DOM_SNAPSHOT_WS_URL_DEFAULT,
    timeout: float = DOM_SNAPSHOT_REQUEST_TIMEOUT_DEFAULT,
    target_client_id: Optional[str] = None,
) -> dict:
    """
    Request a DOM snapshot from the frontend websocket bridge.
    """
    request_id = str(uuid4())
    request_payload = {
        "type": "get_dom_snapshot",
        "requestId": request_id,
    }
    if target_client_id:
        request_payload["targetClientId"] = target_client_id

    try:
        async with websockets.connect(ws_url, ping_interval=None) as websocket:
            await websocket.send(json.dumps({"type": "register", "role": "backend"}))
            await websocket.send(json.dumps(request_payload))

            while True:
                raw_message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError:
                    continue

                message_type = message.get("type")
                message_request_id = message.get("requestId")

                if message_type == "dom_snapshot_response" and message_request_id in {
                    None,
                    request_id,
                }:
                    if message.get("error"):
                        raise RuntimeError(message["error"])
                    return message

                if message_type == "dom_snapshot_error" and message_request_id in {
                    None,
                    request_id,
                }:
                    raise RuntimeError(message.get("error") or "DOM snapshot error")

    except asyncio.TimeoutError as exc:
        raise RuntimeError(
            f"Timed out waiting for DOM snapshot response after {timeout} seconds"
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"Unable to connect to DOM snapshot websocket at {ws_url}: {exc}"
        ) from exc


async def send_tts_message(
    text: str,
    session_id: str,
    step_id: str,
    ws_url: str = DOM_SNAPSHOT_WS_URL_DEFAULT,
    target_client_id: Optional[str] = None,
) -> None:
    """
    Broadcast a TTS message to the frontend via the websocket bridge.
    """
    if not text:
        return

    logger.info(
        "Dispatching TTS message for session=%s step=%s (len=%d)",
        session_id,
        step_id,
        len(text),
    )

    payload = {
        "type": "tts_broadcast",
        "text": text,
        "sessionId": session_id,
        "stepId": step_id,
    }
    if target_client_id:
        payload["targetClientId"] = target_client_id

    try:
        async with websockets.connect(ws_url, ping_interval=None) as websocket:
            await websocket.send(json.dumps({"type": "register", "role": "backend"}))

            # Best-effort read of register acknowledgement
            try:
                await asyncio.wait_for(websocket.recv(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

            await websocket.send(json.dumps(payload))

            # Best-effort read of acknowledgement
            try:
                await asyncio.wait_for(websocket.recv(), timeout=1.0)
            except asyncio.TimeoutError:
                pass
    except Exception as exc:
        logger.warning(
            "Failed to dispatch TTS message for session %s step %s: %s",
            session_id,
            step_id,
            exc,
        )


# ============================================================================
# FastAPI Apps
# ============================================================================

# LLM Agent API (port 8000)
app = FastAPI(title="LLM Agent API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/decide", response_model=List[DecideResponse])
async def decide(request: DecideRequest) -> List[DecideResponse]:
    """
    Planner agent endpoint that classifies user intent and enriches prompts.
    Supports multi-task requests and sequential processing per session.

    Input:
    - sid: Session ID
    - text: User query (can contain multiple tasks)

    Output:
    List of DecideResponse objects, one per task:
    - step_id: Unique step identifier
    - step_type: Intent classification (edit/act/clarify)
    - intent: Enriched user query with explanation
    - context: Summarized context from previous prompts
    """
    try:
        responses = await process_user_request(request)
        return responses
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest) -> PlanResponse:
    """
    Main orchestration endpoint that executes the full pipeline.

    Workflow:
    1. Accepts user request with session_id and text
    2. Calls planner to classify and split tasks
    3. Routes each task to appropriate agent (edit/act/clarify)
    4. Stores results in session
    5. Returns aggregated responses

    Input:
    - sid: Session ID
    - text: User query (can contain multiple tasks)

    Output:
    - sid: Session ID
    - results: List of AgentResult objects with unified format
      - session_id: Session ID
      - step_id: Step identifier
      - intent: User's request with explanation
      - context: Previous actions/prompts
      - result: Agent output (code/action/reply)
      - agent_type: Type of agent that processed the task
    """
    try:
        logger.info(f"Received /plan request for session: {request.sid}")
        response = await execute_plan(request)
        logger.info(f"Successfully completed /plan request for session: {request.sid}")
        return response
    except Exception as e:
        logger.error(
            f"Error processing /plan request for session {request.sid}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Error executing plan: {str(e)}")


@app.get("/queue/{sid}", response_model=QueueStatus)
async def get_queue_status(sid: str) -> QueueStatus:
    """
    Get the current status of a session's task queue.

    Input:
    - sid: Session ID (path parameter)

    Output:
    - sid: Session ID
    - pending: List of pending tasks
    - processing: List of currently processing tasks
    - completed: List of completed tasks
    """
    try:
        queue_manager = get_queue_manager()
        status = await queue_manager.get_queue_status(sid)
        return QueueStatus(sid=sid, **status)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting queue status: {str(e)}"
        )


@app.post("/edit", response_model=EditResponse)
async def edit(request: EditRequest) -> EditResponse:
    """
    Editor agent endpoint that generates JSON Patch arrays for AST modifications.

    Input:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: User's edit request with explanation
    - context: Previous actions/prompts

    Output:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: Original intent
    - context: Original context
    - code: JSON Patch array as string
    """
    try:
        response = process_edit_request(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing edit request: {str(e)}"
        )


@app.post("/clarify", response_model=ClarifyResponse)
async def clarify(request: ClarifyRequest) -> ClarifyResponse:
    """
    Clarification agent endpoint that generates Jarvis-style clarification replies.

    Input:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: User's ambiguous request with explanation
    - context: Previous actions/prompts

    Output:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: Original intent
    - context: Original context
    - reply: Jarvis-style clarification question
    """
    try:
        response = await process_clarification_request(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing clarification request: {str(e)}"
        )


@app.post("/action", response_model=ActionResponse)
async def action(request: ActionRequest) -> ActionResponse:
    """
    Actor agent endpoint that generates actions based on intent and context.

    Input:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: User's request with explanation
    - context: Previous actions/prompts

    Output:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: User's request with explanation
    - context: Previous actions/prompts
    - action: Generated action
    """
    logger.info(
        "API /action received: session=%s step=%s intent='%s' context='%s'",
        request.session_id,
        request.step_id,
        _preview(request.intent),
        _preview(request.context),
    )
    try:
        response = await process_action_request(request)
        logger.info(
            "API /action completed: session=%s step=%s actionLength=%s",
            response.session_id,
            response.step_id,
            len(response.action) if response.action else 0,
        )
        return response
    except Exception as e:
        logger.exception(
            "API /action failed: session=%s step=%s error=%s",
            request.session_id,
            request.step_id,
            e,
        )
        raise HTTPException(
            status_code=500, detail=f"Error processing action request: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "llm-agent"}


# ============================================================================
# Executor Bridge API (port 8100)
# ============================================================================

executor_app = FastAPI(title="Executor Bridge API", version="1.0.0")

executor_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@executor_app.get("/dom-snapshot")
async def dom_snapshot(
    target_client_id: Optional[str] = None,
    ws_url: Optional[str] = None,
    timeout: Optional[float] = None,
):
    """
    Connect to the frontend websocket bridge and return a DOM snapshot with system prompt.

    Query parameters:
    - target_client_id: optional websocket client id when multiple frontends are connected.
    - ws_url: override websocket endpoint url.
    - timeout: override request timeout (seconds).
    """
    resolved_ws_url = ws_url or DOM_SNAPSHOT_WS_URL_DEFAULT
    resolved_timeout = timeout or DOM_SNAPSHOT_REQUEST_TIMEOUT_DEFAULT

    try:
        snapshot_response = await fetch_dom_snapshot(
            ws_url=resolved_ws_url,
            timeout=resolved_timeout,
            target_client_id=target_client_id,
        )

        snapshot = snapshot_response.get("snapshot", {})

        system_prompt = get_system_prompt(snapshot)
        return {
            "snapshot": snapshot,
            "systemPrompt": system_prompt,
            "timestamp": snapshot_response.get("timestamp"),
            "activeIframe": snapshot.get("activeIframe"),
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@executor_app.get("/health")
async def executor_health():
    """Health check endpoint for executor service."""
    return {"status": "healthy", "service": "executor-bridge"}


# ============================================================================
# Server Startup Functions (must be at module level for multiprocessing)
# ============================================================================

# Configure uvicorn logging
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}


def run_llm_server():
    """Run LLM Agent API using configured host/port."""
    import uvicorn

    logger.info("Starting LLM Agent API on %s:%s", LLM_SERVER_HOST, LLM_SERVER_PORT)
    uvicorn.run(
        "llm.server:app",
        host=LLM_SERVER_HOST,
        port=LLM_SERVER_PORT,
        log_config=log_config,
        log_level="info",
        reload=bool(os.getenv("LLM_SERVER_RELOAD", "")),
    )


def run_executor_server():
    """Run Executor Bridge API using configured host/port."""
    import uvicorn

    logger.info(
        "Starting Executor Bridge API on %s:%s",
        EXECUTOR_SERVER_HOST,
        EXECUTOR_SERVER_PORT,
    )
    uvicorn.run(
        "llm.server:executor_app",
        host=EXECUTOR_SERVER_HOST,
        port=EXECUTOR_SERVER_PORT,
        log_config=log_config,
        log_level="info",
        reload=bool(os.getenv("EXECUTOR_SERVER_RELOAD", "")),
    )


if __name__ == "__main__":
    import multiprocessing

    # Start both servers in separate processes
    llm_process = multiprocessing.Process(target=run_llm_server, name="LLM-Server")
    executor_process = multiprocessing.Process(
        target=run_executor_server, name="Executor-Server"
    )

    print("=" * 60)
    print("🚀 Starting Unified Server")
    print("=" * 60)
    print(f"📡 LLM Agent API:       http://{LLM_SERVER_HOST}:{LLM_SERVER_PORT}")
    print(
        f"🔗 Executor Bridge API: http://{EXECUTOR_SERVER_HOST}:{EXECUTOR_SERVER_PORT}"
    )
    print("=" * 60)
    print("Press Ctrl+C to stop both servers")
    print("=" * 60)

    llm_process.start()
    executor_process.start()

    try:
        llm_process.join()
        executor_process.join()
    except KeyboardInterrupt:
        print("\n\n⏹  Shutting down servers...")
        llm_process.terminate()
        executor_process.terminate()
        llm_process.join()
        executor_process.join()
        print("✅ Servers stopped")
