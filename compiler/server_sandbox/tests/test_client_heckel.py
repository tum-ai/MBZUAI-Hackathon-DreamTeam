# test_client_heckel.py
import requests
import json
import time
import config  # <-- Import the config
import os

# --- Read URL from config ---
BASE_URL = f"http://{config.HOST}:{config.PORT}"

# --- Helper Functions (from test_client.py) ---

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

def patch_project(patch_list: list, op_name: str = "Project Operation"):
    """Sends a PATCH request to the /project endpoint."""
    print(f"--- PATCH {BASE_URL}/project ({op_name}) ---")
    try:
        response = requests.patch(f"{BASE_URL}/project", json=patch_list)
        response.raise_for_status() 
        print(f"PATCH /project ({op_name}) successful.")
        time.sleep(1.5) # Give generator time
        return True
    except requests.exceptions.RequestException as e:
        print(f"PATCH /project ({op_name}) FAILED: {e}")
        return False

def patch_page(page_name: str, patch_list: list, op_name: str = "Page Operation"):
    """Sends a PATCH request to the /ast/{page_name} endpoint."""
    print(f"--- PATCH {BASE_URL}/ast/{page_name} ({op_name}) ---")
    try:
        response = requests.patch(f"{BASE_URL}/ast/{page_name}", json=patch_list)
        response.raise_for_status()
        print(f"PATCH /ast/{page_name} ({op_name}): {response.json().get('status')}")
        time.sleep(1.5) # Give generator time
        return True
    except requests.exceptions.RequestException as e:
        print(f"PATCH /ast/{page_name} ({op_name}) FAILED: {e}")
        return False

# --- Main Demo Script ---

def main():
    print("--- Starting Reinhard Heckel Website Build (V7 Client) ---")

    # --- Step 0: Clean Slate ---
    print("\n--- Step 0: Ensuring a clean slate ---")
    if config.PROJECT_CONFIG_FILE.exists():
        print(f"Removing existing {config.PROJECT_CONFIG_FILE.name}...")
        os.remove(config.PROJECT_CONFIG_FILE)
    
    for f in config.AST_INPUT_DIR.glob("*.json"):
        print(f"Removing existing AST: {f.name}...")
        os.remove(f)
    print("Clean slate confirmed.")

    # --- Step 1: Create the Project & Pages ---
    # We create the project and ALL its pages in one go.
    create_project_patch = [
        {
            "op": "add",
            "path": "/projectName",
            "value": "Prof. Reinhard Heckel"
        },
        # Page 1: Home
        {
            "op": "add", "path": "/pages/-",
            "value": { "name": "Home", "path": "/", "astFile": "home.json" }
        },
        # Page 2: Projects
        {
            "op": "add", "path": "/pages/-",
            "value": { "name": "Projects", "path": "/projects", "astFile": "projects.json" }
        },
        # Page 3: Project Detail (our "Modal" replacement)
        {
            "op": "add", "path": "/pages/-",
            "value": { "name": "ProjectDeepDecoder", "path": "/projects/deep-decoder", "astFile": "project_deepdecoder.json" }
        }
    ]
    if not patch_project(create_project_patch, "Create Project"):
        print("Fatal error: Could not create project. Aborting.")
        return
    
    # --- Step 2: Build the Home Page ---
    # This is ONE patch request with a MASSIVE batch of operations
    # to build the entire homepage for Prof. Heckel.
    
    home_page_patches = [
        # Set a root container
        {
            "op": "replace", "path": "/tree",
            "value": {
                "id": "root-container", "type": "Box",
                "props": { "style": { "font-family": "Arial, sans-serif", "max-width": "1000px", "margin": "0 auto", "padding": "20px" } },
                "slots": { "default": [] }
            }
        },
        
        # --- Hero Section (Flexbox) ---
        {
            "op": "add", "path": "/tree/slots/default/-",
            "value": {
                "id": "hero-section", "type": "Box",
                "props": { "style": { "display": "flex", "align-items": "center", "border-bottom": "2px solid #eee", "padding-bottom": "20px", "margin-bottom": "20px" } },
                "slots": { "default": [
                    # Image
                    {
                        "id": "hero-img", "type": "Image",
                        "props": { 
                            "src": "https://placehold.co/150x150/EFEFEF/333?text=Prof.+Heckel", 
                            "alt": "Prof. Reinhard Heckel", 
                            "style": { "width": "150px", "height": "150px", "border-radius": "50%", "flex-shrink": "0" } 
                        },
                        "slots": {}
                    },
                    # Text Box
                    {
                        "id": "hero-text-box", "type": "Box",
                        "props": { "style": { "margin-left": "25px" } },
                        "slots": { "default": [
                            { "id": "hero-title", "type": "Text", "props": { "content": "Reinhard Heckel", "as": "h1", "style": { "fontSize": "48px", "margin": "0 0 10px 0" } } },
                            { "id": "hero-subtitle", "type": "Text", "props": { "content": "Associate Professor, Technical University of Munich", "as": "p", "style": { "fontSize": "22px", "color": "#555", "margin": "0" } } },
                            { "id": "hero-subtitle-2", "type": "Text", "props": { "content": "Adjunct Faculty, Rice University", "as": "p", "style": { "fontSize": "22px", "color": "#555", "margin": "0" } } }
                        ]}
                    }
                ]}
            }
        },
        
        # --- Research Interests Section ---
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "research-title", "type": "Text", "props": { "content": "Research Interests", "as": "h2", "style": { "fontSize": "32px", "border-bottom": "1px solid #ccc", "padding-bottom": "5px" } } } },
        {
            "op": "add", "path": "/tree/slots/default/-", "value": {
                "id": "research-text", "type": "Text",
                "props": { 
                    "content": "Machine learning and signal and information processing. Current focus: i) algorithms and theory for deep learning based signal and image reconstruction, ii) mathematical and empirical foundations of machine learning, and iii) DNA as digital information technology.", 
                    "as": "p", 
                    "style": { "fontSize": "16px", "line-height": "1.6" } 
                },
                "slots": {}
            }
        },

        # --- Button to Projects Page ---
        {
            "op": "add", "path": "/tree/slots/default/-", "value": {
                "id": "projects-link-btn", "type": "Link",
                "props": { "href": "#/projects" }, # Vue Router hash link
                "slots": { "default": [
                    { 
                        "id": "projects-btn", "type": "Button", 
                        "props": { "text": "View My Projects", "style": { "fontSize": "18px", "padding": "10px 15px", "margin": "20px 0" } },
                        "events": {}
                    }
                ]}
            }
        },

        # --- Awards Section (List) ---
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "awards-title", "type": "Text", "props": { "content": "Awards and Honors", "as": "h2", "style": { "fontSize": "32px", "border-bottom": "1px solid #ccc", "padding-bottom": "5px" } } } },
        {
            "op": "add", "path": "/tree/slots/default/-", "value": {
                "id": "awards-list", "type": "List",
                "props": {
                    "items": [
                        "105th Röntgen Vorlesung, 2024",
                        "Capital magazine's 40 under 40, 2022",
                        "Young scientist honour from the Werner-von-Siemens-Ring foundation, 2022",
                        "Outstanding Reviewer Award, NeurIPS, 2021",
                        "ETH Zurich medal for outstanding Ph.D. thesis, 2015"
                    ],
                    "style": { "fontSize": "16px", "line-height": "1.7" }
                },
                "slots": {}
            }
        }
    ]
    
    if not patch_page("Home", home_page_patches, "Build Home Page"):
        print("Fatal error: Could not build Home page. Aborting.")
        return

    # --- Step 3: Build the Projects Page ---
    # This demonstrates the "Carousel" (scrolling flexbox)
    
    projects_page_patches = [
        # Set root container
        { "op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": { "style": { "font-family": "Arial, sans-serif", "max-width": "1200px", "margin": "0 auto", "padding": "20px" } },
            "slots": { "default": [] }
        }},
        # Title
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "projects-title", "type": "Text", "props": { "content": "Selected Projects", "as": "h1", "style": { "fontSize": "48px" } } } },
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "projects-subtitle", "type": "Text", "props": { "content": "Scroll horizontally to see projects.", "as": "p", "style": { "fontSize": "16px", "color": "#555" } } } },
        
        # --- The "Carousel" ---
        {
            "op": "add", "path": "/tree/slots/default/-", "value": {
                "id": "project-carousel", "type": "Box",
                "props": { "style": { 
                    "display": "flex", 
                    "overflow-x": "auto",  # <-- This makes it scroll
                    "padding": "20px 0"
                }},
                "slots": { "default": [
                    
                    # --- Card 1: Deep Decoder (links to new page) ---
                    {
                        "id": "card-link-1", "type": "Link",
                        "props": { "href": "#/projects/deep-decoder" }, # Our "modal" link
                        "slots": { "default": [
                            {
                                "id": "card-1", "type": "Box",
                                "props": { "style": {
                                    "border": "1px solid #ddd", "border-radius": "8px", "padding": "15px", "margin-right": "20px",
                                    "width": "300px", "flex-shrink": "0", "text-decoration": "none", "color": "black"
                                }},
                                "slots": { "default": [
                                    { "id": "card-1-img", "type": "Image", "props": { "src": "https://placehold.co/300x150/EEE/333?text=Deep+Decoder", "style": {"width": "100%"}} },
                                    { "id": "card-1-title", "type": "Text", "props": { "content": "Deep Decoder: Concise image representations", "as": "h3", "style": {"margin": "10px 0"} } },
                                    { "id": "card-1-text", "type": "Text", "props": { "content": "Published at ICLR 2019. Image representations from untrained non-convolutional networks.", "as": "p" } }
                                ]}
                            }
                        ]}
                    },
                    
                    # --- Card 2: DNA Data Storage ---
                    {
                        "id": "card-link-2", "type": "Link", "props": { "href": "#" },
                        "slots": { "default": [
                            {
                                "id": "card-2", "type": "Box",
                                "props": { "style": {
                                    "border": "1px solid #ddd", "border-radius": "8px", "padding": "15px", "margin-right": "20px",
                                    "width": "300px", "flex-shrink": "0", "text-decoration": "none", "color": "black"
                                }},
                                "slots": { "default": [
                                    { "id": "card-2-img", "type": "Image", "props": { "src": "https://placehold.co/300x150/EEE/333?text=DNA+Data+Storage", "style": {"width": "100%"}} },
                                    { "id": "card-2-title", "type": "Text", "props": { "content": "Low cost DNA data storage", "as": "h3", "style": {"margin": "10px 0"} } },
                                    { "id": "card-2-text", "type": "Text", "props": { "content": "Published in Nature Communications, 2020. Using photolithographic synthesis.", "as": "p" } }
                                ]}
                            }
                        ]}
                    },
                    
                    # --- Card 3: More... ---
                ]}
            }
        }
    ]
    patch_page("Projects", projects_page_patches, "Build Projects Page")

    # --- Step 4: Build the Project Detail Page ("Modal") ---
    # This proves our dynamic routing works.
    
    deepdecoder_page_patches = [
        # Set root container
        { "op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": { "style": { "font-family": "Arial, sans-serif", "max-width": "1000px", "margin": "0 auto", "padding": "20px" } },
            "slots": { "default": [] }
        }},
        # Back Link
        { "op": "add", "path": "/tree/slots/default/-", "value": {
            "id": "back-link", "type": "Link", "props": { "href": "#/projects" },
            "slots": { "default": [ { "id": "back-link-text", "type": "Text", "props": { "content": "< Back to Projects", "as": "p" } } ] }
        }},
        # Title
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "dd-title", "type": "Text", "props": { "content": "Deep Decoder: Concise image representations from untrained non-convolutional networks", "as": "h1" } } },
        # Publication Info
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "dd-pub", "type": "Text", "props": { "content": "Published at ICLR 2019 (L6)", "as": "p", "style": { "font-style": "italic", "color": "#444" } } } },
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "dd-img", "type": "Image", "props": { "src": "https://placehold.co/800x400/EEE/333?text=Deep+Decoder+Paper+Figure", "style": {"width": "100%", "margin": "20px 0"}} } },
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "dd-abstract-title", "type": "Text", "props": { "content": "Abstract", "as": "h2" } } },
        { "op": "add", "path": "/tree/slots/default/-", "value": { "id": "dd-abstract", "type": "Text", "props": { "content": "Placeholder for the paper abstract... This demonstrates a dynamically generated detail page that acts as a modal.", "as": "p", "style": {"line-height": "1.6"} } } },
    ]
    patch_page("ProjectDeepDecoder", deepdecoder_page_patches, "Build Detail Page")

    
    print("\n--- Reinhard Heckel Website Build COMPLETE! ---")
    print(f"Generated a {len(create_project_patch)} page project with {len(home_page_patches)} home page patches.")
    print(f"Check the output in: {config.OUTPUT_DIR}")
    print(f"Then run:\n  cd {config.OUTPUT_DIR.name}\n  npm install\n  npm run dev")

if __name__ == "__main__":
    main()