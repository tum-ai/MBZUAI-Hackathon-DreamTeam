# src/server.py
import json
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jsonpatch

import config
from .project_generator import ProjectGenerator

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# --- Lock and Generation Task REMOVED ---
# This server's only job is to apply patches and write files.

# --- Template Generation Models ---
class TemplateGenerationRequest(BaseModel):
    template_type: str  # 'portfolio', 'product', 'gallery', 'ecommerce', 'blog'
    variables: dict  # Template-specific variables

class TemplateSelectionRequest(BaseModel):
    variation_index: int  # 0, 1, 2, or 3

# --- Template Generation Constants ---
TEMPLATE_SELECTION_DIR = Path("/home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server/inputs")
ACTIVE_PROJECT_DIR = Path("/tmp/active")  # DEPRECATED - no longer used
PALETTE_VARIATIONS = ["professional", "dark", "minimal", "energetic"]  # 4 variations

# Track which variation is selected (0-3, or None)
SELECTED_VARIATION_INDEX = None

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
        
        # --- Copy generated files to active project (for live preview) ---
        if ACTIVE_PROJECT_DIR.exists():
            print(f"Copying generated files to active project: {ACTIVE_PROJECT_DIR}")
            # Copy the generated views and updated files
            for item in config.OUTPUT_DIR.iterdir():
                if item.name in ['node_modules', 'dist', '.vite', 'package-lock.json']:
                    continue
                dest = ACTIVE_PROJECT_DIR / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            # Also copy project.json and jsrepo.json if they exist in the server directory
            for config_file in ['project.json', 'jsrepo.json']:
                src_config = config.BASE_DIR / config_file
                if src_config.exists():
                    shutil.copy2(src_config, ACTIVE_PROJECT_DIR / config_file)
            print("✓ Active project updated")
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
    V7: Reads from selected variation /tmp/selection/{index} when available.
    """
    page_name_lower = page_name.lower()
    
    # Check if we have a selected variation
    if SELECTED_VARIATION_INDEX is not None:
        selected_ast_dir = TEMPLATE_SELECTION_DIR / str(SELECTED_VARIATION_INDEX) / "src" / "ast"
        ast_file_path = selected_ast_dir / f"{page_name_lower}.json"
        print(f"Reading AST from selected variation {SELECTED_VARIATION_INDEX}: {ast_file_path}")
    else:
        ast_file_path = config.AST_INPUT_DIR / f"{page_name_lower}.json"
        print(f"Reading AST from default location: {ast_file_path}")
    
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
    V7: Works with selected variation /tmp/selection/{index} when available.
    Falls back to config.AST_INPUT_DIR for initial generation.
    """
    page_name_lower = page_name.lower()
    
    # Check if we have a selected variation
    if SELECTED_VARIATION_INDEX is not None:
        selected_ast_dir = TEMPLATE_SELECTION_DIR / str(SELECTED_VARIATION_INDEX) / "src" / "ast"
        ast_file_path = selected_ast_dir / f"{page_name_lower}.json"
        print(f"Applying patch to selected variation {SELECTED_VARIATION_INDEX}: {ast_file_path}")
    else:
        ast_file_path = config.AST_INPUT_DIR / f"{page_name_lower}.json"
        print(f"Applying patch to default location: {ast_file_path}")
    
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

        # Ensure parent directory exists
        ast_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(ast_file_path, 'w') as f:
            json.dump(patched_ast, f, indent=2)

        # Regenerate the project from the updated AST
        # For selected variations, this will regenerate directly in /tmp/selection/{index}
        if SELECTED_VARIATION_INDEX is not None:
            print(f"Regenerating selected variation {SELECTED_VARIATION_INDEX}...")
            # Temporarily copy AST to inputs for generator
            input_ast_path = config.AST_INPUT_DIR / f"{page_name_lower}.json"
            input_ast_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ast_file_path, input_ast_path)
            
            # Generate
            project_gen = ProjectGenerator()
            project_gen.generate_project()
            
            # Copy regenerated files back to selected variation (excluding build artifacts)
            variation_dir = TEMPLATE_SELECTION_DIR / str(SELECTED_VARIATION_INDEX)
            print(f"Copying regenerated files to: {variation_dir}")
            for item in config.OUTPUT_DIR.iterdir():
                if item.name in ['node_modules', 'dist', '.vite', 'package-lock.json']:
                    continue
                dest = variation_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            
            print(f"✓ Variation {SELECTED_VARIATION_INDEX} updated (Vite hot-reload will pick up changes)")
        else:
            # No selection yet - just regenerate for initial template generation
            print(f"Patch applied to /ast/{page_name_lower}. Running generator...")
            project_gen = ProjectGenerator()
            project_gen.generate_project()
            print("File generation complete.")
        
        return {"status": "success", "data": patched_ast}

    except jsonpatch.JsonPatchException as e:
        raise HTTPException(status_code=400, detail=f"Invalid patch: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@app.post("/generate-template-variations", summary="Generate 4 template variations")
async def generate_template_variations(request: TemplateGenerationRequest):
    """
    Generates 4 variations of a template with different palettes.
    Creates complete projects in /tmp/selection/0, /tmp/selection/1, etc.
    The container watches these locations for updates.
    
    Args:
        template_type: One of 'portfolio', 'product', 'gallery', 'ecommerce', 'blog'
        variables: Template-specific variables (e.g., name, tagline, etc.)
    
    Returns:
        Status and paths to the generated variations
    """
    try:
        # Import templates module
        import sys
        templates_path = config.BASE_DIR / "templates"
        if str(templates_path) not in sys.path:
            sys.path.insert(0, str(templates_path))
        
        from templates import generate_from_template, get_available_templates
        
        # Validate template type
        available_templates = get_available_templates()
        if request.template_type not in available_templates:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid template type. Available: {', '.join(available_templates)}"
            )
        
        # Create selection directory if it doesn't exist
        TEMPLATE_SELECTION_DIR.mkdir(parents=True, exist_ok=True)
        
        # Clean up old variations
        for i in range(4):
            variant_dir = TEMPLATE_SELECTION_DIR / str(i)
            if variant_dir.exists():
                shutil.rmtree(variant_dir)
        
        generated_variations = []
        
        # Generate 4 variations with different palettes
        for idx, palette in enumerate(PALETTE_VARIATIONS):
            print(f"\n=== Generating variation {idx}: {palette} palette ===")
            
            # Prepare variables with the current palette
            variation_vars = request.variables.copy()
            variation_vars['palette'] = palette
            
            # Set default font based on palette
            font_map = {
                "professional": "modern",
                "dark": "tech",
                "minimal": "elegant",
                "energetic": "playful"
            }
            if 'font' not in variation_vars:
                variation_vars['font'] = font_map.get(palette, "modern")
            
            # Generate the template
            result = generate_from_template(
                request.template_type, 
                variation_vars, 
                multi_page=True
            )
            
            # Create variation directory structure
            variant_dir = TEMPLATE_SELECTION_DIR / str(idx)
            variant_inputs_dir = variant_dir / "inputs"
            variant_inputs_dir.mkdir(parents=True, exist_ok=True)
            
            # Write project.json (apply patches to default config)
            project_config = config.DEFAULT_PROJECT_CONFIG.copy()
            project_patches = result.get('projectPatches', [])
            patched_project = jsonpatch.apply_patch(project_config, project_patches)
            
            project_file = variant_dir / "project.json"
            with open(project_file, 'w') as f:
                json.dump(patched_project, f, indent=2)
            
            # Write page AST files
            pages = result.get('pages', {})
            page_files = []
            for page_filename, page_ast in pages.items():
                page_path = variant_inputs_dir / page_filename
                with open(page_path, 'w') as f:
                    json.dump(page_ast, f, indent=2)
                page_files.append(page_filename)
            
            # Copy static files (if needed for generation)
            static_src = config.STATIC_DIR
            static_dst = variant_dir / "static"
            if static_src.exists():
                shutil.copytree(static_src, static_dst, dirs_exist_ok=True)
            
            # Copy manifests (if needed for generation)
            manifests_src = config.MANIFESTS_DIR
            manifests_dst = variant_dir / "manifests"
            if manifests_src.exists():
                shutil.copytree(manifests_src, manifests_dst, dirs_exist_ok=True)
            
            # Generate the output files for this variation
            print(f"Generating output for variation {idx}...")
            
            # Create output directory at the root of variant (not nested)
            variant_output_dir = variant_dir
            
            # Generate using ProjectGenerator with overridden paths
            from .project_generator import ProjectGenerator
            
            # Override the paths temporarily BEFORE creating generator
            original_ast_dir = config.AST_INPUT_DIR
            original_project_file = config.PROJECT_CONFIG_FILE
            original_output_dir = config.OUTPUT_DIR
            original_static_dir = config.STATIC_DIR
            original_manifests_dir = config.MANIFESTS_DIR
            
            try:
                config.AST_INPUT_DIR = variant_inputs_dir
                config.PROJECT_CONFIG_FILE = project_file
                config.OUTPUT_DIR = variant_output_dir
                config.STATIC_DIR = static_dst
                config.MANIFESTS_DIR = manifests_dst
                
                # NOW create the generator with overridden paths
                gen = ProjectGenerator()
                gen.generate_project()
                
            finally:
                # Restore original paths
                config.AST_INPUT_DIR = original_ast_dir
                config.PROJECT_CONFIG_FILE = original_project_file
                config.OUTPUT_DIR = original_output_dir
                config.STATIC_DIR = original_static_dir
                config.MANIFESTS_DIR = original_manifests_dir
            
            generated_variations.append({
                "index": idx,
                "palette": palette,
                "font": variation_vars.get('font'),
                "path": str(variant_dir),
                "pages": page_files,
                "project_file": str(project_file),
                "package_json": str(variant_dir / "package.json"),
                "ready_to_run": True  # Indicates this is a complete Vue project
            })
            
            print(f"✓ Variation {idx} complete at {variant_dir}")
            print(f"  Ready to run: cd {variant_dir} && npm install && npm run dev")
        
        return {
            "status": "success",
            "template_type": request.template_type,
            "variations": generated_variations,
            "selection_dir": str(TEMPLATE_SELECTION_DIR),
            "active_project_dir": str(ACTIVE_PROJECT_DIR),
            "message": f"Generated 4 variations of {request.template_type} template"
        }
    
    except Exception as e:
        import traceback
        error_detail = f"Error generating template variations: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/select-template-variation", summary="Select a template variation as active")
async def select_template_variation(request: TemplateSelectionRequest):
    """
    Simplified: Just tracks which variation (0-3) is selected.
    No copying, no restart. Patches will be applied directly to /tmp/selection/{index}.
    
    Args:
        variation_index: 0, 1, 2, or 3 (which variation to select)
    
    Returns:
        Status and selected variation info
    """
    global SELECTED_VARIATION_INDEX
    
    try:
        # Validate index
        if request.variation_index not in [0, 1, 2, 3]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid variation_index. Must be 0, 1, 2, or 3. Got: {request.variation_index}"
            )
        
        # Check if variation exists
        variation_dir = TEMPLATE_SELECTION_DIR / str(request.variation_index)
        if not variation_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Variation {request.variation_index} not found at {variation_dir}. Generate templates first."
            )
        
        print(f"\n=== Selecting variation {request.variation_index} ===")
        
        # Just track the selection - no copying needed
        SELECTED_VARIATION_INDEX = request.variation_index
        
        # Read metadata about the selected variation
        project_file = variation_dir / "project.json"
        with open(project_file, 'r') as f:
            project_config = json.load(f)
        
        # Get palette and font info
        palette = PALETTE_VARIATIONS[request.variation_index]
        font_map = {
            "professional": "modern",
            "dark": "tech",
            "minimal": "elegant",
            "energetic": "playful"
        }
        font = font_map[palette]
        
        # List pages
        pages = [p.get("name") for p in project_config.get("pages", [])]
        
        print(f"✓ Selected variation {request.variation_index}")
        print(f"  Path: {variation_dir}")
        print(f"  Palette: {palette}")
        print(f"  Font: {font}")
        print(f"  Pages: {', '.join(pages)}")
        print(f"  Port: {5173 + request.variation_index}")
        
        # No restart needed - we're editing the live variation directly
        return {
            "status": "success",
            "selected_variation": request.variation_index,
            "palette": palette,
            "font": font,
            "variation_path": str(variation_dir),
            "project_name": project_config.get("projectName", "Project"),
            "pages": pages,
            "message": f"Variation {request.variation_index} ({palette}) selected. Edits will apply directly to port {5173 + request.variation_index}.",
            "port": 5173 + request.variation_index,
            "preview_ports": {
                "variation_0": 5173,
                "variation_1": 5174,
                "variation_2": 5175,
                "variation_3": 5176
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error selecting template variation: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/selected-variation", summary="Get information about the selected variation")
async def get_selected_variation():
    """
    Returns information about the currently selected variation.
    Replaces /active-project endpoint.
    """
    if SELECTED_VARIATION_INDEX is None:
        return {
            "status": "no_selection",
            "message": "No variation selected yet. Select a template variation first.",
            "selected_variation": None,
            "variation_path": None,
            "port": None
        }
    
    try:
        variation_dir = TEMPLATE_SELECTION_DIR / str(SELECTED_VARIATION_INDEX)
        project_file = variation_dir / "project.json"
        with open(project_file, 'r') as f:
            project_config = json.load(f)
        
        palette = PALETTE_VARIATIONS[SELECTED_VARIATION_INDEX]
        port = 5173 + SELECTED_VARIATION_INDEX
        
        return {
            "status": "selected",
            "selected_variation": SELECTED_VARIATION_INDEX,
            "variation_path": str(variation_dir),
            "palette": palette,
            "port": port,
            "project_name": project_config.get("projectName", "Project"),
            "pages": [p.get("name") for p in project_config.get("pages", [])],
            "message": f"Variation {SELECTED_VARIATION_INDEX} is selected (port {port})"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading selected variation: {str(e)}",
            "selected_variation": SELECTED_VARIATION_INDEX,
            "variation_path": str(TEMPLATE_SELECTION_DIR / str(SELECTED_VARIATION_INDEX))
        }