import json
from pathlib import Path
from .models import EditRequest, EditResponse
from .llm_client import generate_json_patch
from .manifest_loader import load_all_manifests


# Hardcoded paths for AST and project config
AST_PATH = Path(__file__).resolve().parents[2] / "compiler" / "server" / "inputs" / "home.json"
PROJECT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "compiler" / "server" / "project.json"


def load_current_ast() -> dict:
    """Load the current page AST from home.json."""
    try:
        with open(AST_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading AST: {e}")
        return {"state": {}, "tree": {"id": "root", "type": "Box", "props": {}, "slots": {"default": []}}}


def load_project_config() -> dict:
    """Load the project configuration from project.json."""
    try:
        with open(PROJECT_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading project config: {e}")
        return {"projectName": "My Site", "pages": [], "globalStyles": ""}


def process_edit_request(request: EditRequest) -> EditResponse:
    """
    Process edit request through the editor agent.
    
    Steps:
    1. Load all component manifests
    2. Load hardcoded AST from home.json
    3. Load hardcoded project config from project.json
    4. Call generate_json_patch() with all context
    5. Return EditResponse with generated JSON Patch array
    
    Args:
        request: EditRequest with session_id, step_id, intent, context
    
    Returns:
        EditResponse with generated JSON Patch array as string
    """
    # Step 1: Load all component manifests
    manifests = load_all_manifests()
    
    # Step 2: Load current AST
    current_ast = load_current_ast()
    
    # Step 3: Load project config
    project_config = load_project_config()
    
    # Step 4: Generate JSON Patch array
    patch_array = generate_json_patch(
        intent=request.intent,
        context=request.context,
        manifests=manifests,
        current_ast=current_ast,
        project_config=project_config
    )
    
    # Step 5: Return response with patch array as JSON string
    response = EditResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        code=json.dumps(patch_array, indent=2)
    )
    
    return response

