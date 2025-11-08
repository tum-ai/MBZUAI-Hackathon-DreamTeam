# src/server.py
import asyncio
import json
import os
import requests
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
import jsonpatch

import config
from .project_generator import ProjectGenerator

app = FastAPI()

# --- Lock to prevent race conditions ---
generation_lock = asyncio.Lock()

# --- Background Generation Task ---

async def run_generation_task(page_name: str = "project"):
    """
    The background task that runs the full project generator.
    This is triggered *after* a patch is successfully applied.
    It uses a lock to prevent concurrent builds.
    """
    
    # Try to acquire the lock. If it's already held, this will wait.
    try:
        await asyncio.wait_for(generation_lock.acquire(), timeout=10.0)
    except asyncio.TimeoutError:
        print("WARNING: Could not acquire generation lock. Another build is likely in progress. Skipping.")
        return

    print(f"--- [Generator Lock Acquired for: {page_name}] ---")
    print("Starting background generation task...")
    
    try:
        # V4: Initialize the "Empty-Aware" generator.
        project_gen = ProjectGenerator()
        
        # Run the full project build
        project_gen.generate_project() 
        print("Background generation task complete.")

        # --- Send HTTP Webhook ---
        print(f"Sending refresh webhook to: {config.FRONTEND_REFRESH_WEBHOOK}")
        try:
            payload = {"status": "success", "updated": page_name}
            requests.post(config.FRONTEND_REFRESH_WEBHOOK, json=payload, timeout=3.0)
            print("Refresh webhook sent successfully.")
        except requests.exceptions.ConnectionError:
            print(f"WARNING: Could not connect to frontend server at {config.FRONTEND_REFRESH_WEBHOOK}. Is it running?")
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Failed to send refresh webhook: {e}")
        # --- End Webhook ---

    except Exception as e:
        print(f"ERROR during background generation: {e}")
    finally:
        # ALWAYS release the lock when done
        generation_lock.release()
        print(f"--- [Generator Lock Released for: {page_name}] ---")


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
    background_tasks: BackgroundTasks,
    trigger_build: bool = False  # <-- V5 FIX: Add query param
):
    """
    Applies a JSON patch to the project.json file.
    V4: Creates project.json from a default if it doesn't exist.
    """
    try:
        patch_ops = await patch.json()
        
        # --- V4: "Empty-Aware" Read ---
        current_config = config.DEFAULT_PROJECT_CONFIG
        if config.PROJECT_CONFIG_FILE.exists():
            try:
                with open(config.PROJECT_CONFIG_FILE, 'r') as f:
                    # Load file if it exists and is valid
                    current_config = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {config.PROJECT_CONFIG_FILE.name} corrupted. Starting from default.")
                # current_config is already the default, so we just proceed
        else:
             print(f"Info: {config.PROJECT_CONFIG_FILE.name} not found. Creating new one from patch.")
        # --- End V4 Fix ---

        # Apply the patch to the in-memory version
        patched_config = jsonpatch.apply_patch(current_config, patch_ops)

        # Write (or create) the new config back to disk
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
                        # Create a new blank AST file for the page
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
                    
                    # Also ensure the value in the config is lowercase
                    new_page_config['astFile'] = ast_file_lower

        # --- V5 FIX: Only trigger build if requested ---
        if trigger_build:
            print("Build triggered for /project patch.")
            background_tasks.add_task(run_generation_task, page_name="project_config")
        else:
            print("Patch applied to /project. Build not triggered.")

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
        # V4: Return a default blank page AST if not found
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
    background_tasks: BackgroundTasks,
    trigger_build: bool = True  # <-- V5 FIX: Add query param
):
    """
    Applies a JSON patch to a specific page's AST file (e.g., 'home.json').
    V4: Creates the file from a default if it doesn't exist.
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
        # --- End V4 Fix ---

        # Apply the patch
        patched_ast = jsonpatch.apply_patch(current_ast, patch_ops)

        # Write the new AST back to disk
        with open(ast_file_path, 'w') as f:
            json.dump(patched_ast, f, indent=2)

        # --- V5 FIX: Only trigger build if requested ---
        if trigger_build:
            print(f"Build triggered for /ast/{page_name_lower} patch.")
            background_tasks.add_task(run_generation_task, page_name=page_name_lower)
        else:
            print(f"Patch applied to /ast/{page_name_lower}. Build not triggered.")

        return {"status": "success", "data": patched_ast}

    except jsonpatch.JsonPatchException as e:
        raise HTTPException(status_code=400, detail=f"Invalid patch: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")