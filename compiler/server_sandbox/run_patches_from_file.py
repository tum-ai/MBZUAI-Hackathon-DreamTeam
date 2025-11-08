# run_patches_from_file.py
import requests
import json
import time
import sys
import config
import os

# --- V18: Read URL from config ---
BASE_URL = f"http://{config.HOST}:{config.PORT}"

# --- Helper Functions (copied from test clients) ---
# --- V3: Added trigger_build parameter ---
def patch_project(patch_list: list, op_name: str = "Project Operation", trigger_build: bool = False):
    """Sends a PATCH request to the /project endpoint."""
    print(f"--- PATCH {BASE_URL}/project ({op_name}) ---")
    if not patch_list:
        print("No project patches to apply. Skipping.")
        return True
    
    # V3: Add trigger_build to the query params
    params = {"trigger_build": str(trigger_build).lower()}
        
    try:
        response = requests.patch(f"{BASE_URL}/project", json=patch_list, params=params)
        response.raise_for_status() 
        print(f"PATCH /project ({op_name}) successful (Build Triggered: {trigger_build}).")
        if trigger_build:
            print("Waiting 3s for build to complete...")
            time.sleep(3) # Give generator time
        else:
            time.sleep(0.5) # Short sleep
        return True
    except requests.exceptions.RequestException as e:
        print(f"PATCH /project ({op_name}) FAILED: {e}")
        return False

# --- V3: Added trigger_build parameter ---
def patch_page(page_name: str, patch_list: list, op_name: str = "Page Operation", trigger_build: bool = False):
    """Sends a PATCH request to the /ast/{page_name} endpoint."""
    print(f"--- PATCH {BASE_URL}/ast/{page_name} ({op_name}) ---")
    if not patch_list:
        print(f"No page patches to apply for {page_name}. Skipping.")
        return True
    
    # V3: Add trigger_build to the query params
    params = {"trigger_build": str(trigger_build).lower()}
        
    try:
        response = requests.patch(f"{BASE_URL}/ast/{page_name}", json=patch_list, params=params)
        response.raise_for_status()
        print(f"PATCH /ast/{page_name} ({op_name}): {response.json().get('status')} (Build Triggered: {trigger_build})")
        if trigger_build:
            print("Waiting 3s for build to complete...")
            time.sleep(3) # Give generator time
        else:
            time.sleep(0.5) # Short sleep
        return True
    except requests.exceptions.RequestException as e:
        print(f"PATCH /ast/{page_name} ({op_name}) FAILED: {e}")
        return False

def sort_and_run_patches(all_patches: list, target_page: str):
    """
    Sorts a master list of patches into project-level and page-level
    and sends them to the correct endpoints.
    """
    project_patches = []
    page_patches = []

    # Define paths that belong to project.json
    project_paths = ("/globalStyles", "/projectName", "/pages")

    for patch in all_patches:
        path = patch.get("path", "")
        if path.startswith(project_paths):
            project_patches.append(patch)
        else:
            # Assume everything else belongs to the page AST
            page_patches.append(patch)

    print(f"Found {len(project_patches)} project patches and {len(page_patches)} page patches.")

    # --- V2 FIX: Ensure the target page exists in the project ---
    # Check if a patch for this page already exists
    page_exists_in_patch = False
    for patch in project_patches:
        if patch.get("path", "").startswith("/pages"):
            page_name_in_patch = patch.get("value", {}).get("name", "")
            if page_name_in_patch.lower() == target_page.lower():
                page_exists_in_patch = True
                break
    
    if not page_exists_in_patch:
        print(f"Injecting 'add page' patch for target page: {target_page}")
        # Determine path (e.g., "/" for Home, "/contact" for Contact)
        page_path = "/" if target_page.lower() == "home" else f"/{target_page.lower()}"
        
        project_patches.append({
            "op": "add",
            "path": "/pages/-", # Add to end of pages array
            "value": {
                "name": target_page,
                "path": page_path,
                "astFile": f"{target_page.lower()}.json"
            }
        })
        print(f"Injected patch: {project_patches[-1]}")
    # --- End V2 FIX ---
    # --- V3 FIX: Trigger build ONLY on the *last* call ---
    
    # Run project patches first, but DO NOT trigger a build
    if not patch_project(project_patches, "Apply Project Patches", trigger_build=False):
        print("Stopping due to project patch failure.")
        return

    # Run page patches second and DO trigger a build
    if not patch_page(target_page, page_patches, f"Apply Page Patches to {target_page}", trigger_build=True):
        print("Stopping due to page patch failure.")
        return

    print("\n--- All patches applied successfully! ---")


def main():
    """
    Main entry point.
    Usage: python run_patches_from_file.py <json_file> <page_name>
    Example: python run_patches_from_file.py llm_patches.json Home
    """
    if len(sys.argv) != 3:
        print("Usage: python run_patches_from_file.py <json_file> <page_name>")
        print("Example: python run_patches_from_file.py llm_patches.json Home")
        sys.exit(1)

    json_file_path = sys.argv[1]
    target_page = sys.argv[2] # The page context the LLM was given

    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        sys.exit(1)

    try:
        with open(json_file_path, 'r') as f:
            all_patches = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    # --- V4: Clean Slate for testing ---
    print("\n--- Step 0: Ensuring a clean slate ---")
    if config.PROJECT_CONFIG_FILE.exists():
        print(f"Removing existing {config.PROJECT_CONFIG_FILE.name}...")
        os.remove(config.PROJECT_CONFIG_FILE)
    
    for f in config.AST_INPUT_DIR.glob("*.json"):
        print(f"Removing existing AST: {f.name}...")
        os.remove(f)
    print("Clean slate confirmed.")
    # --- End Clean Slate ---

    print(f"\n--- Running patches from '{json_file_path}' on page '{target_page}' ---")
    sort_and_run_patches(all_patches, target_page)

if __name__ == "__main__":
    main()