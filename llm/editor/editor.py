import json
from pathlib import Path
from .models import EditRequest, EditResponse
from .llm_client import generate_component_direct
from .manifest_loader import load_all_manifests


# Hardcoded paths for AST and project config
AST_PATH = Path(__file__).resolve().parents[2] / "compiler" / "server" / "inputs" / "home.json"


def load_current_ast() -> dict:
    """Load the current page AST from home.json."""
    try:
        with open(AST_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading AST: {e}")
        return {"state": {}, "tree": {"id": "root", "type": "Box", "props": {}, "slots": {"default": []}}}


def process_edit_request(request: EditRequest) -> EditResponse:
    """
    Process edit request through the editor agent using optimized single-step LLM process.
    
    Steps:
    1. Load all component manifests (from cache)
    2. Load current AST (provides context for edits)
    3. Call LLM once to generate component directly
    4. Return EditResponse with component JSON as code
    
    Args:
        request: EditRequest with session_id, step_id, intent, context
    
    Returns:
        EditResponse with generated component JSON as string
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
    
    response = EditResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        code=json.dumps(component, indent=2)
    )
    
    return response
