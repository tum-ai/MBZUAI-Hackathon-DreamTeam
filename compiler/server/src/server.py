# src/server.py
import json
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import jsonpatch

import config
from .project_generator import ProjectGenerator

app = FastAPI()

# --- Lock and Generation Task REMOVED ---
# This server's only job is to apply patches and write files.

# --- Template Generation Models ---
class TemplateGenerationRequest(BaseModel):
    template_type: str  # 'portfolio', 'product', 'gallery', 'ecommerce', 'blog'
    variables: dict  # Template-specific variables

class TemplateSelectionRequest(BaseModel):
    variation_index: int  # 0, 1, 2, or 3

# --- Template Generation Constants ---
TEMPLATE_SELECTION_DIR = Path("/tmp/selection")
ACTIVE_PROJECT_DIR = Path("/tmp/active")  # The selected/active template
PALETTE_VARIATIONS = ["professional", "dark", "minimal", "energetic"]  # 4 variations

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
    Selects one of the 4 template variations and copies it to the active project directory.
    This makes it the "5th" project that the user will edit.
    The container should rebuild/restart the dev server for this active project.
    
    Args:
        variation_index: 0, 1, 2, or 3 (which variation to select)
    
    Returns:
        Status and path to the active project
    """
    try:
        # Validate index
        if request.variation_index not in [0, 1, 2, 3]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid variation_index. Must be 0, 1, 2, or 3. Got: {request.variation_index}"
            )
        
        # Check if variation exists
        source_dir = TEMPLATE_SELECTION_DIR / str(request.variation_index)
        if not source_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Variation {request.variation_index} not found at {source_dir}. Generate templates first."
            )
        
        print(f"\n=== Selecting variation {request.variation_index} as active ===")
        
        # Clean active directory contents (but not the directory itself - it's a Docker volume mount)
        if ACTIVE_PROJECT_DIR.exists():
            print(f"Cleaning existing active project contents: {ACTIVE_PROJECT_DIR}")
            for item in ACTIVE_PROJECT_DIR.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            # Create directory if it doesn't exist
            ACTIVE_PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Copy selected variation contents to active directory (skip node_modules)
        print(f"Copying {source_dir} contents → {ACTIVE_PROJECT_DIR}")
        for item in source_dir.iterdir():
            # Skip node_modules and other build artifacts
            if item.name in ['node_modules', 'dist', '.vite', 'package-lock.json']:
                continue
            dest = ACTIVE_PROJECT_DIR / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        
        print(f"✓ Files copied (node_modules will be installed by dev server)")
        
        # Read metadata about the selected variation
        project_file = ACTIVE_PROJECT_DIR / "project.json"
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
        
        print(f"✓ Active project set to variation {request.variation_index}")
        print(f"  Path: {ACTIVE_PROJECT_DIR}")
        print(f"  Palette: {palette}")
        print(f"  Font: {font}")
        print(f"  Pages: {', '.join(pages)}")
        
        return {
            "status": "success",
            "selected_variation": request.variation_index,
            "palette": palette,
            "font": font,
            "active_project_path": str(ACTIVE_PROJECT_DIR),
            "project_name": project_config.get("projectName", "Project"),
            "pages": pages,
            "message": f"Variation {request.variation_index} ({palette}) is now active. Container should rebuild on port 5177.",
            "container_port": 5177,
            "preview_ports": {
                "variation_0": 5173,
                "variation_1": 5174,
                "variation_2": 5175,
                "variation_3": 5176,
                "active": 5177
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error selecting template variation: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/active-project", summary="Get information about the active project")
async def get_active_project():
    """
    Returns information about the currently active project.
    The container uses this to know what to serve on port 5177.
    """
    if not ACTIVE_PROJECT_DIR.exists():
        return {
            "status": "no_active_project",
            "message": "No active project. Select a template variation first.",
            "active_project_path": None
        }
    
    try:
        project_file = ACTIVE_PROJECT_DIR / "project.json"
        with open(project_file, 'r') as f:
            project_config = json.load(f)
        
        return {
            "status": "active",
            "active_project_path": str(ACTIVE_PROJECT_DIR),
            "project_name": project_config.get("projectName", "Project"),
            "pages": [p.get("name") for p in project_config.get("pages", [])],
            "container_port": 5177,
            "message": "Active project ready"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading active project: {str(e)}",
            "active_project_path": str(ACTIVE_PROJECT_DIR)
        }