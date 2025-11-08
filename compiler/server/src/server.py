# src/server.py
import json
from fastapi import FastAPI, HTTPException, Request
import jsonpatch

import config
from .project_generator import ProjectGenerator

app = FastAPI()

# --- Lock and Generation Task REMOVED ---
# This server's only job is to apply patches and write files.

# --- API Endpoints ---

@app.get("/project", summary="Get the main project configuration")
async def get_project_config():
    """
    Returns the main project.json file.
    V4: Returns a default config if the file doesn't exist.
    """
    if not config.PROJECT_CONFIG_FILE.exists():
        print("Info: project.json not found. Returning default config.")
        return config.DEFAULT_PROJECT_CONFIG
    
    try:
        with open(config.PROJECT_CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
        return config_data
    except json.JSONDecodeError:
        print(f"Warning: {config.PROJECT_CONFIG_FILE.name} is corrupted. Returning default.")
        return config.DEFAULT_PROJECT_CONFIG
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@app.patch("/project", summary="Patch the main project configuration")
async def patch_project_config(
    patch: Request, 
    # BackgroundTasks and trigger_build REMOVED
):
    """
    Applies a JSON patch to the project.json file.
    V4: Creates project.json from a default if it doesn't exist.
    V5: REMOVED build trigger. This endpoint only writes files.
    """
    try:
        patch_ops = await patch.json()
        
        # --- V4: "Empty-Aware" Read ---
        current_config = config.DEFAULT_PROJECT_CONFIG
        if config.PROJECT_CONFIG_FILE.exists():
            try:
                with open(config.PROJECT_CONFIG_FILE, 'r') as f:
                    current_config = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {config.PROJECT_CONFIG_FILE.name} corrupted. Starting from default.")
        else:
             print(f"Info: {config.PROJECT_CONFIG_FILE.name} not found. Creating new one from patch.")
        
        patched_config = jsonpatch.apply_patch(current_config, patch_ops)

        with open(config.PROJECT_CONFIG_FILE, 'w') as f:
            json.dump(patched_config, f, indent=2)

        # --- Handle side-effects (e.g., creating new blank AST files) ---
        for op in patch_ops:
            if op['op'] == 'add' and op['path'].startswith('/pages/'):
                new_page_config = op.get('value', {})
                ast_file = new_page_config.get('astFile')
                if ast_file:
                    ast_file_lower = ast_file.lower()
                    ast_path = config.AST_INPUT_DIR / ast_file_lower
                    if not ast_path.exists():
                        blank_ast = {
                            "state": {},
                            "tree": {
                                "id": "root", "type": "Box",
                                "props": {"style": {"padding": "2rem"}},
                                "slots": {
                                    "default": [{
                                        "id": "title-1", "type": "Text",
                                        "props": {"content": f"New Page: {new_page_config.get('name')}", "as": "h1"},
                                        "slots": {}
                                    }]
                                }
                            }
                        }
                        with open(ast_path, 'w') as f:
                            json.dump(blank_ast, f, indent=2)
                        print(f"Created new blank AST: {ast_path}")
                    
                    new_page_config['astFile'] = ast_file_lower
        
        # --- Run the generator SYNCHRONOUSLY ---
        # The request will hang until the files are written, which is what we want.
        print("Patch applied to /project. Running generator...")
        project_gen = ProjectGenerator()
        project_gen.generate_project()
        print("File generation complete.")
        # --- End V5 change ---

        return {"status": "success", "data": patched_config}

    except jsonpatch.JsonPatchException as e:
        raise HTTPException(status_code=400, detail=f"Invalid patch: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@app.get("/ast/{page_name}", summary="Get the AST for a specific page")
async def get_page_ast(page_name: str):
    """
    Returns the AST JSON for a single page (e.g., 'home.json').
    """
    ast_file_path = config.AST_INPUT_DIR / f"{page_name.lower()}.json"
    
    if not ast_file_path.exists():
        print(f"Info: AST file not found: {ast_file_path.name}. Returning blank AST.")
        return {
            "state": {},
            "tree": {
                "id": "root", "type": "Box",
                "props": {"style": {"padding": "2rem"}},
                "slots": {
                    "default": [{
                        "id": "title-1", "type": "Text",
                        "props": {"content": f"New Page: {page_name}", "as": "h1"},
                        "slots": {}
                    }]
                }
            }
        }
        
    try:
        with open(ast_file_path, 'r') as f:
            ast_data = json.load(f)
        return ast_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"AST file corrupted: {ast_file_path.name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@app.patch("/ast/{page_name}", summary="Patch the AST for a specific page")
async def patch_page_ast(
    page_name: str, 
    patch: Request, 
    # BackgroundTasks and trigger_build REMOVED
):
    """
    Applies a JSON patch to a specific page's AST file (e.g., 'home.json').
    V5: REMOVED build trigger. This endpoint only writes files.
    """
    page_name_lower = page_name.lower()
    ast_file_path = config.AST_INPUT_DIR / f"{page_name_lower}.json"
    
    try:
        patch_ops = await patch.json()
        
        # --- V4: "Empty-Aware" Read for Page AST ---
        current_ast = {
            "state": {},
            "tree": {
                "id": "root", "type": "Box",
                "props": {"style": {"padding": "2rem"}},
                "slots": {
                    "default": [{
                        "id": "title-1", "type": "Text",
                        "props": {"content": f"Page: {page_name_lower}", "as": "h1"},
                        "slots": {}
                    }]
                }
            }
        }
        if ast_file_path.exists():
            try:
                with open(ast_file_path, 'r') as f:
                    current_ast = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {ast_file_path.name} corrupted. Starting from default.")
        else:
            print(f"Info: {ast_file_path.name} not found. Creating new one from patch.")

        patched_ast = jsonpatch.apply_patch(current_ast, patch_ops)

        with open(ast_file_path, 'w') as f:
            json.dump(patched_ast, f, indent=2)

        # --- Run the generator SYNCHRONOUSLY ---
        print(f"Patch applied to /ast/{page_name_lower}. Running generator...")
        project_gen = ProjectGenerator()
        project_gen.generate_project()
        print("File generation complete.")
        # --- End V5 change ---
        
        return {"status": "success", "data": patched_ast}

    except jsonpatch.JsonPatchException as e:
        raise HTTPException(status_code=400, detail=f"Invalid patch: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")