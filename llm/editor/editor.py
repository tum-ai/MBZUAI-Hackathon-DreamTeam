import json
import logging
import os
from pathlib import Path
from typing import Optional
import httpx
from .models import EditRequest, EditResponse
from .llm_client import generate_component_direct
from .manifest_loader import load_all_manifests

logger = logging.getLogger(__name__)

# Compiler URL (check if compiler is on different port via env var)
COMPILER_URL = os.getenv("COMPILER_URL", "http://localhost:8000")


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


async def process_edit_request(request: EditRequest) -> EditResponse:
    """
    Process edit request through the editor agent using optimized single-step LLM process.
    
    Steps:
    1. Load all component manifests (from cache)
    2. Load current AST (provides context for edits)
    3. Call LLM once to generate component directly
    4. Apply component to compiler via JSON Patch
    5. Return EditResponse with component JSON and compiler status
    
    Args:
        request: EditRequest with session_id, step_id, intent, context
    
    Returns:
        EditResponse with generated component JSON as string and compiler status
    """
    # Get cached manifests
    manifests = load_all_manifests()
    
    # Load AST for context (helps LLM understand existing components)
    current_ast = load_current_ast()
    
    # Single LLM call to generate component directly
    component = generate_component_direct(
        intent=request.intent,
        context=request.context,
        manifests=manifests,
        current_ast=current_ast
    )
    
    # Apply to compiler
    compiler_result = await apply_component_to_compiler(component, page_name="home")
    compiler_status = compiler_result.get("status") if compiler_result else "not_applied"
    
    response = EditResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        code=json.dumps(component, indent=2),
        compiler_status=compiler_status
    )
    
    return response
