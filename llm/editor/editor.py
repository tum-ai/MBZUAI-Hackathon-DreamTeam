import json
from pathlib import Path
from .models import EditRequest, EditResponse
from .llm_client import decide_component_action, generate_or_edit_component
from .manifest_loader import load_all_manifests, get_component_manifest


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
    Process edit request through the editor agent using two-step LLM process.
    
    Steps:
    1. Load all component manifests
    2. Call LLM Step 1: Decide action (generate/edit) and component type
    3. Get specific component manifest for that type
    4. Load AST if action is "edit"
    5. Call LLM Step 2: Generate or edit the component
    6. Return EditResponse with component JSON as code
    
    Args:
        request: EditRequest with session_id, step_id, intent, context
    
    Returns:
        EditResponse with generated component JSON as string
    """
    manifests = load_all_manifests()

    decision = decide_component_action(
        intent=request.intent,
        context=request.context,
        manifests=manifests
    )
    
    action = decision.get("action", "generate")
    component_type = decision.get("component_type", "Box")
    
    component_manifest = get_component_manifest(component_type)
    
    if not component_manifest:
        component_manifest = get_component_manifest("Box")
    
    # AST if editing
    current_ast = None
    if action == "edit":
        current_ast = load_current_ast()
    
    component = generate_or_edit_component(
        intent=request.intent,
        context=request.context,
        action=action,
        component_manifest=component_manifest,
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
