# test_client.py
import requests
import json
import time
import config  # <-- Import the new config
import os

# --- V4: Read URL from config ---
BASE_URL = f"http://{config.HOST}:{config.PORT}"

def get_project():
    """Fetches the current project.json state."""
    print(f"--- GET {BASE_URL}/project ---")
    try:
        response = requests.get(f"{BASE_URL}/project")
        response.raise_for_status()
        print(f"GET /project response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"GET /project FAILED: {e}")
        return None

def patch_project(patch_list: list):
    """Sends a PATCH request to the /project endpoint."""
    print(f"--- PATCH {BASE_URL}/project ---")
    try:
        response = requests.patch(f"{BASE_URL}/project", json=patch_list)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        print(f"PATCH /project successful.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"PATCH /project FAILED: {e}")
        return False

def patch_page(page_name: str, patch_list: list, op_name: str = "Operation"):
    """Sends a PATCH request to the /ast/{page_name} endpoint."""
    print(f"--- PATCH {BASE_URL}/ast/{page_name} ({op_name}) ---")
    try:
        response = requests.patch(f"{BASE_URL}/ast/{page_name}", json=patch_list)
        response.raise_for_status()
        print(f"PATCH /ast/{page_name} ({op_name}): {response.json().get('status')}")
        # Give the background task a moment to run.
        time.sleep(1) 
        return True
    except requests.exceptions.RequestException as e:
        print(f"PATCH /ast/{page_name} ({op_name}) FAILED: {e}")
        return False

def main():
    print("--- Starting V-Zero Test (V4 Client) ---")

    # --- Step 0: Clean Slate (V4 Test) ---
    print("\n--- Step 0: Ensuring a clean slate ---")
    # We delete project.json to simulate a true "from-nothing" start
    if config.PROJECT_CONFIG_FILE.exists():
        print(f"Removing existing {config.PROJECT_CONFIG_FILE.name}...")
        os.remove(config.PROJECT_CONFIG_FILE)
    
    # We can also clear the inputs directory
    for f in config.AST_INPUT_DIR.glob("*.json"):
        print(f"Removing existing AST: {f.name}...")
        os.remove(f)

    print("Clean slate confirmed.")

    # --- Step 1: Create Project from Nothing ---
    print("\n--- Step 1: Creating project from nothing ---")
    
    # The first GET should return the default config
    project_config = get_project()
    if not project_config:
        print("Fatal error: Could not get /project. Is server running?")
        print(f"Attempted to connect to {BASE_URL}")
        return
    
    if project_config != config.DEFAULT_PROJECT_CONFIG:
        print(f"Warning: GET /project did not return default config. Test may be skewed.")
        print(f"Got: {project_config}")
        
    # Now, let's create the project with a name and our first page
    create_project_patch = [
        {
            "op": "add",
            "path": "/projectName",
            "value": "My V-Zero Hackathon Site"
        },
        {
            "op": "add",
            "path": "/pages/-", # Add to the end of the 'pages' array
            "value": {
                "name": "Portfolio", 
                "path": "/portfolio", 
                "astFile": "portfolio.json" # Server will lowercase this
            }
        }
    ]
    
    if not patch_project(create_project_patch):
        print("Fatal error: Could not create project. Aborting.")
        return
    
    print(f"{config.PROJECT_CONFIG_FILE.name} should now exist.")
    print("\nWaiting 2s for server to create blank AST file and run build...")
    time.sleep(2) 

    # --- Step 2: Add content to the new 'Portfolio' page ---
    print("--- Step 2: Setting up root container ---")
    root_tree = {
        "id": "root-container", "type": "Box",
        "props": { "style": { "font-family": "Arial, sans-serif", "max-width": "1000px", "margin": "0 auto", "padding": "20px" } },
        "slots": { "default": [] }
    }
    # This patch will apply to the *default blank page* created by the server
    patch_page("Portfolio", [{"op": "replace", "path": "/tree", "value": root_tree}], "Init Root")

    # --- Step 3: Add Header (Image + Text) ---
    print("--- Step 3: Adding Header ---")
    header_patch = [
        {
            "op": "add", "path": "/tree/slots/default/-",
            "value": {
                "id": "header-box", "type": "Box",
                "props": { "style": { "display": "flex", "align-items": "center", "border-bottom": "2px solid #eee", "padding-bottom": "20px" } },
                "slots": { "default": [
                    {
                        "id": "header-img", "type": "Image",
                        "props": { "src": "https://placehold.co/150x150/EFEFEF/333?text=Profile", "alt": "Profile Photo", "style": { "width": "150px", "height": "150px", "border-radius": "50%" } },
                        "slots": {}
                    },
                    {
                        "id": "header-text-box", "type": "Box",
                        "props": { "style": { "margin-left": "20px" } },
                        "slots": { "default": [
                            { "id": "header-title", "type": "Text", "props": { "content": "Your Name", "as": "h1", "style": { "fontSize": "48px", "margin": "0" } }, "slots": {} },
                            { "id": "header-subtitle", "type": "Text", "props": { "content": "Your Title", "as": "p", "style": { "fontSize": "24px", "color": "#555", "margin": "0" } }, "slots": {} }
                        ]}
                    }
                ]}
            }
        }
    ]
    patch_page("Portfolio", header_patch, "Add Header")

    # --- Step 4: Add "Contact" Section (Textbox, Button) & State ---
    print("--- Step 4: Adding 'Contact' Form (State, Textbox, Button) ---")
    
    # First, add the state variables
    state_patch = [
        { "op": "add", "path": "/state/contactMessage", "value": {"type": "string", "defaultValue": "Default Message"} },
    ]
    patch_page("Portfolio", state_patch, "Add State")

    # Now, add the form components that bind to that state
    form_patch = [
        {
            "op": "add", "path": "/tree/slots/default/-",
            "value": {
                "id": "form-section", "type": "Box",
                "props": { "style": { "margin-top": "30px", "background": "#f9f9f9", "padding": "20px", "border-radius": "8px" } },
                "slots": { "default": [
                    { "id": "form-title", "type": "Text", "props": { "content": "Contact Me", "as": "h2", "style": { "fontSize": "32px" } }, "slots": {} },
                    { 
                        "id": "msg-input", "type": "Textbox", 
                        "props": { 
                            "modelValue": {"type": "stateBinding", "stateKey": "contactMessage"}, 
                            "placeholder": "Your Message" 
                        }, 
                        "events": { 
                            "input": [ {"type": "action:setState", "stateKey": "contactMessage", "newValue": {"type": "expression", "value": "event.target.value"}} ] 
                        } 
                    },
                    { 
                        "id": "submit-btn", "type": "Button", 
                        "props": { "text": "Submit" }, 
                        "events": { 
                            "click": [ {"type": "action:showAlert", "message": {"type": "expression", "value": "Form submitted with message: ${state.contactMessage}"}} ] 
                        } 
                    }
                ]}
            }
        }
    ]
    patch_page("Portfolio", form_patch, "Add Form")


    print("\n--- Test complete! ---")
    print(f"A 'Portfolio' page should now exist and be fully populated at {config.AST_INPUT_DIR / 'portfolio.json'}")
    print(f"The generated project is in: {config.OUTPUT_DIR}")
    print(f"\nNext Steps:")
    print(f"1. Run the server: python run_server.py")
    print(f"2. Run this test client: python test_client.py")
    print(f"3. Run the Vite server in '{config.OUTPUT_DIR.name}':")
    print(f"   cd {config.OUTPUT_DIR.name}")
    print(f"   npm install")
    print(f"   npm run dev")
    print(f"\n4. Open your browser to the Vite URL (e.g., http://localhost:5173/#/portfolio)")

if __name__ == "__main__":
    main()