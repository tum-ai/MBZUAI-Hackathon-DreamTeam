import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional
from uuid import uuid4
from urllib.parse import urlparse
import httpx
import websockets
from .models import EditRequest, EditResponse
from .llm_client import generate_component_direct, generate_vue_component_direct
from .manifest_loader import load_all_manifests

logger = logging.getLogger(__name__)

# Compiler URL (check if compiler is on different port via env var)
COMPILER_URL = os.getenv("COMPILER_URL", "http://localhost:8098")


def load_current_ast() -> dict:
    """
    Load the current page AST by querying the compiler for the selected variation.
    The compiler now tracks which variation is selected and reads/writes directly to it.
    """
    try:
        # Ask compiler which variation is selected
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{COMPILER_URL}/selected-variation")
            if response.status_code == 200:
                selection_info = response.json()
                if selection_info["status"] == "selected":
                    # Fetch AST from compiler (it will read from the selected variation)
                    ast_response = client.get(f"{COMPILER_URL}/ast/home")
                    if ast_response.status_code == 200:
                        ast = ast_response.json()
                        logger.info(f"Loaded AST from selected variation {selection_info['selected_variation']}")
                        return ast
    except Exception as e:
        logger.warning(f"Error loading AST from selected variation: {e}")
    
    # Return empty AST if nothing exists
    logger.warning("No selection or error, returning empty structure")
    return {"state": {}, "tree": {"id": "root", "type": "Box", "props": {}, "slots": {"default": []}}}


def extract_component_from_result(component: dict) -> dict:
    """
    Extract the actual component from LLM result.
    The LLM sometimes returns a full tree structure, we need just the component.
    
    Args:
        component: Generated component (might be wrapped in tree/state structure)
    
    Returns:
        The actual component to add
    """
    # If it has 'tree' key, it's a full AST - extract the last component
    if "tree" in component and "slots" in component["tree"]:
        default_slots = component["tree"]["slots"].get("default", [])
        if default_slots:
            # Get the last added component (usually the new one)
            return default_slots[-1]
    
    # If it has both 'id' and 'type', it's already a component
    if "id" in component and "type" in component:
        return component
    
    # Otherwise return as-is and let compiler handle it
    return component


async def apply_component_to_compiler(component: dict, page_name: str = "home") -> Optional[dict]:
    """
    Apply the generated component to the compiler via JSON Patch.
    
    Args:
        component: Component to add
        page_name: Target page name (default: home)
    
    Returns:
        Compiler response or None if failed
    """
    # Extract just the component (not the full tree)
    actual_component = extract_component_from_result(component)
    
    # Create JSON Patch to add component to the end of default slots
    patch = [
        {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": actual_component
        }
    ]
    
    url = f"{COMPILER_URL}/ast/{page_name}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Applying component to compiler: {url}")
            response = await client.patch(url, json=patch)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Compiler response: {result.get('status', 'unknown')}")
            return result
    except httpx.HTTPError as e:
        logger.error(f"Failed to apply component to compiler: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error applying to compiler: {e}")
        return {"status": "error", "message": str(e)}


async def fetch_dom_snapshot_simple() -> dict:
    """
    Fetch DOM snapshot to get current URL.
    """
    ws_url = os.getenv("DOM_SNAPSHOT_WS_URL", "ws://localhost:5173/dom-snapshot")
    try:
        async with websockets.connect(ws_url) as websocket:
            await websocket.send(json.dumps({"type": "register", "role": "backend"}))
            request_id = str(uuid4())
            await websocket.send(json.dumps({"type": "get_dom_snapshot", "requestId": request_id}))
            
            try:
                while True:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(msg)
                    if data.get("type") == "dom_snapshot_response" and data.get("requestId") == request_id:
                        return data
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for DOM snapshot")
                return {}
    except Exception as e:
        logger.error(f"Failed to fetch DOM snapshot: {e}")
        return {}


async def process_edit_request(request: EditRequest) -> EditResponse:
    """
    Process edit request by directly modifying the active Vue file.
    """
    # 1. Determine Target File
    response_data = await fetch_dom_snapshot_simple()
    snapshot = response_data.get("snapshot", {})
    
    # Prefer iframe location if available (since we are editing the iframe content)
    iframe_loc = snapshot.get("iframeLocation")
    if iframe_loc and iframe_loc.get("hash"):
        current_url = iframe_loc.get("hash")
    elif iframe_loc and iframe_loc.get("path"):
        current_url = iframe_loc.get("path")
    else:
        current_url = snapshot.get("currentUrl", "/")
    
    logger.info(f"Using URL for targeting: {current_url}")
    
    # Normalize URL to find the path
    path = "/"
    if current_url:
        if "http" in current_url:
            parsed = urlparse(current_url)
            # Check for hash routing
            if parsed.fragment:
                # fragment is like "/pricing" or "/pricing?foo=bar"
                path = parsed.fragment
                if path.startswith("#"):
                    path = path[1:]
            else:
                path = parsed.path
        elif current_url.startswith("#"):
             path = current_url[1:]
        else:
            path = current_url
            
    # Remove query params if any
    if "?" in path:
        path = path.split("?")[0]
        
    logger.info(f"Detected path from URL {current_url}: {path}")
    
    # Map to file
    repo_root = Path("/home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam")
    base_views = repo_root / "iframe-content/src/views"
    
    target_file = base_views / "Home.vue" # Default
    
    path_lower = path.lower()
    if "features" in path_lower:
        target_file = base_views / "Features.vue"
    elif "pricing" in path_lower:
        target_file = base_views / "Pricing.vue"
    elif "compare" in path_lower:
        target_file = base_views / "Compare.vue"
        
    logger.info(f"Targeting file: {target_file}")
    
    # 2. Read Existing Content
    if target_file.exists():
        existing_content = target_file.read_text()
    else:
        logger.warning(f"Target file {target_file} does not exist, using empty template")
        existing_content = "<template><div>Page not found</div></template>"
        
    # 3. Generate New Code
    # Note: generate_vue_component_direct is synchronous
    new_code = generate_vue_component_direct(request.intent, existing_content)
    
    # 4. Write to File
    target_file.write_text(new_code)
    logger.info(f"Successfully wrote updated code to {target_file}")
    
    # 5. Return Response
    return EditResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        code=new_code,
        compiler_status="bypassed_direct_write"
    )
