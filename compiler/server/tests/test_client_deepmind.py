# test_client_deepmind.py
import requests
import json
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adjust path to import config
import config  # <-- Import the configimport os
import random

# --- V12: Read URL from config ---
BASE_URL = f"http://{config.HOST}:{config.PORT}"

# --- V12: Lorem Ipsum Helper ---
def lorem_ipsum(paragraphs=1):
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    return "\n\n".join([text] * paragraphs)

# --- Helper Functions ---
def patch_project(patch_list: list, op_name: str = "Project Operation"):
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

# --- V12: Global Theme Definition ---
def get_global_theme_styles():
    """
    Defines the entire website's theme, including dark mode,
    fonts, and CSS classes.
    """
    return """
/* V12: Import 'Inter' font (Google Sans-like) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background-color: #111;
  color: #eee;
  margin: 0;
  padding: 0;
}

/* V12: Style the nav bar (previously hardcoded in generator) */
#nav {
  padding: 2rem;
  text-align: center;
  background-color: #1a1a1a;
}
.nav-link { /* Class added by generator */
  font-weight: 700;
  color: #888;
  text-decoration: none;
  padding: 0 1rem;
}
.nav-link.router-link-exact-active {
  color: #42b983;
}

/* --- Global Component Classes --- */
h1, h2, h3, h4 {
  font-weight: 700;
}

.btn-primary {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-primary:hover {
  background-color: #36a473;
}

.btn-secondary {
  background-color: transparent;
  color: #eee;
  border: 1px solid #eee;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary:hover {
  background-color: #eee;
  color: #111;
}

.text-link {
  color: #42b983;
  text-decoration: none;
}
.text-link:hover {
  text-decoration: underline;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 4rem;
}
"""

# --- Main Demo Script ---
def main():
    print("--- Starting Ultimate Demo Build (V13 Client) ---")

    # --- Step 0: Clean Slate ---
    print("\n--- Step 0: Ensuring a clean slate ---")
    if config.PROJECT_CONFIG_FILE.exists():
        os.remove(config.PROJECT_CONFIG_FILE)
    for f in config.AST_INPUT_DIR.glob("*.json"):
        os.remove(f)
    print("Clean slate confirmed.")

    # --- Step 1: Create Project & Global Theme ---
    create_project_patch = [
        {"op": "add", "path": "/projectName", "value": "GenAI Web Design"},
        {"op": "add", "path": "/globalStyles", "value": get_global_theme_styles()},
        {"op": "add", "path": "/pages/-", "value": { "name": "Home", "path": "/", "astFile": "home.json" }},
        {"op": "add", "path": "/pages/-", "value": { "name": "Contact", "path": "/contact", "astFile": "contact.json" }}
    ]
    if not patch_project(create_project_patch, "Create Project & Dark Theme"):
        return

    # --- Step 2: Build the Home Page ---
    home_page_patches = [
        # Add state for Modal and Carousel
        {"op": "add", "path": "/state/isModalOpen", "value": {"type": "boolean", "defaultValue": False}},
        {"op": "add", "path": "/state/currentSlide", "value": {"type": "number", "defaultValue": 0}},
        
        # Set root container
        {"op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": {"class": "page-container"},
            "slots": { "default": [] }
        }},
        
        # --- Header ---
        {"op": "add", "path": "/tree/slots/default/-", "value": {
            "id": "header", "type": "Box",
            "props": {"style": {"display": "flex", "justify-content": "space-between", "align-items": "center"}},
            "slots": { "default": [
                {"id": "logo", "type": "Text", "props": {"content": "GenAI", "as": "h3", "style": {"font-size": "24px"}}},
                {"id": "modal-open-btn", "type": "Button", "props": {"text": "Open Menu", "class": "btn-secondary"},
                 "events": {"click": [{"type": "action:setState", "stateKey": "isModalOpen", "newValue": True}]}}
            ]}
        }},

        # --- Hero Section ---
        {"op": "add", "path": "/tree/slots/default/-", "value": {
            "id": "hero", "type": "Box",
            "props": {"style": {"display": "grid", "grid-template-columns": "1fr 1fr", "gap": "2rem", "align-items": "center", "margin": "5rem 0"}},
            "slots": { "default": [
                {"id": "hero-text", "type": "Box", "slots": { "default": [
                    {"id": "hero-title", "type": "Text", "props": {"content": "Generate the Future of Web Design.", "as": "h1", "style": {"font-size": "60px", "line-height": "1.1"}}},
                    {"id": "hero-subtitle", "type": "Text", "props": {"content": "This entire website was generated by an AI from a natural language prompt.", "as": "p", "style": {"font-size": "20px", "color": "#aaa", "margin": "1rem 0 2rem 0"}}},
                    {"id": "hero-btn", "type": "Button", "props": {"text": "Get In Touch", "class": "btn-primary"}}
                ]}},
                {"id": "hero-img", "type": "Image", "props": {
                    # Swapped to picsum.photos as requested
                    "src": "https://picsum.photos/800/600", 
                    "alt": "AI Generated", "style": {"width": "100%", "border-radius": "12px"}
                }}
            ]}
        }},

        # --- Carousel Section ---
        {"op": "add", "path": "/tree/slots/default/-", "value": {"id": "carousel-title", "type": "Text", "props": {"content": "Features", "as": "h2", "style": {"font-size": "40px", "text-align": "center", "margin-top": "4rem"}}}},
        {"op": "add", "path": "/tree/slots/default/-", "value": {
            "id": "carousel-container", "type": "Box",
            "props": {"style": {"position": "relative", "width": "100%", "height": "400px", "background": "#222", "border-radius": "12px", "overflow": "hidden", "margin": "2rem 0"}},
            "slots": { "default": [
                # Slide 1
                {"id": "slide-1", "type": "Image", "v-if": {"expression": "currentSlide === 0"}, "props": {"src": "https://picsum.photos/800/400?random=1", "style": {"width": "100%", "height": "100%", "object-fit": "cover"}}},
                # Slide 2
                {"id": "slide-2", "type": "Image", "v-if": {"expression": "currentSlide === 1"}, "props": {"src": "https://picsum.photos/800/400?random=2", "style": {"width": "100%", "height": "100%", "object-fit": "cover"}}},
                # Slide 3
                {"id": "slide-3", "type": "Image", "v-if": {"expression": "currentSlide === 2"}, "props": {"src": "https://picsum.photos/800/400?random=3", "style": {"width": "100%", "height": "100%", "object-fit": "cover"}}},
                
                # --- V13: Previous Button Added ---
                {"id": "carousel-prev", "type": "Button", 
                 "props": {"text": "<", "class": "btn-primary", "style": {"position": "absolute", "top": "50%", "left": "1rem", "transform": "translateY(-50%)", "padding": "1rem"}},
                 "events": {"click": [{"type": "action:setState", "stateKey": "currentSlide", 
                                       # Correct modulo logic for negative numbers
                                       "newValue": {"type": "expression", "value": "(${state.currentSlide} - 1 + 3) % 3"}} ]}},
                
                # --- V13: Next Button Fixed ---
                {"id": "carousel-next", "type": "Button", 
                 "props": {"text": ">", "class": "btn-primary", "style": {"position": "absolute", "top": "50%", "right": "1rem", "transform": "translateY(-50%)", "padding": "1rem"}},
                 "events": {"click": [{"type": "action:setState", "stateKey": "currentSlide",
                                       # Fixed missing parenthesis
                                       "newValue": {"type": "expression", "value": "(${state.currentSlide} + 1) % 3"}} ]}}
            ]}
        }},

        # --- About Section (Long Text) ---
        {"op": "add", "path": "/tree/slots/default/-", "value": {"id": "about-title", "type": "Text", "props": {"content": "About This Project", "as": "h2", "style": {"font-size": "40px", "margin-top": "4rem"}}}},
        {"op": "add", "path": "/tree/slots/default/-", "value": {
            "id": "about-text", "type": "Text", "props": {"content": lorem_ipsum(3), "as": "p", "style": {"line-height": "1.7", "color": "#aaa"}}
        }},

        # --- Modal Popup (v-if) ---
        {"op": "add", "path": "/tree/slots/default/-", "value": {
            "id": "modal-overlay", "type": "Box",
            "v-if": {"stateKey": "isModalOpen"},
            "props": {"style": {
                "position": "fixed", "top": "0", "left": "0", "width": "100vw", "height": "100vh",
                "background": "rgba(0, 0, 0, 0.7)", "display": "flex", "align-items": "center", "justify-content": "center", "z-index": "100"
            }},
            "slots": { "default": [
                {"id": "modal-content", "type": "Box", "props": {"style": {
                    "background": "#222", "padding": "3rem", "border-radius": "12px", "min-width": "300px", "position": "relative"
                }}, "slots": { "default": [
                    {"id": "modal-title", "type": "Text", "props": {"content": "Menu", "as": "h2", "style": {"font-size": "32px", "margin-top": "0"}}},
                    {"id": "modal-link-1", "type": "Link", "props": {"href": "#/", "class": "text-link", "style": {"display": "block", "font-size": "20px", "margin": "1rem 0"}}, "slots": {"default": [{"id": "ml1-t", "type": "Text", "props": {"content": "Home"}}]}},
                    {"id": "modal-link-2", "type": "Link", "props": {"href": "#/contact", "class": "text-link", "style": {"display": "block", "font-size": "20px", "margin": "1rem 0"}}, "slots": {"default": [{"id": "ml2-t", "type": "Text", "props": {"content": "Contact"}}]}},
                    {"id": "modal-close-btn", "type": "Button",
                     "props": {"text": "X", "class": "btn-secondary", "style": {"position": "absolute", "top": "1rem", "right": "1rem", "padding": "0.5rem 1rem"}},
                     "events": {"click": [{"type": "action:setState", "stateKey": "isModalOpen", "newValue": False}]}}
                ]}}
            ]}
        }}
    ]
    if not patch_page("Home", home_page_patches, "Build Home Page"): return

    # --- Step 3: Build the Contact Page ---
    contact_page_patches = [
        {"op": "add", "path": "/state/contactName", "value": {"type": "string", "defaultValue": ""}},
        {"op": "add", "path": "/state/contactEmail", "value": {"type": "string", "defaultValue": ""}},
        {"op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": {"class": "page-container", "style": {"max-width": "800px"}},
            "slots": { "default": [
                {"id": "contact-title", "type": "Text", "props": {"content": "Contact Us", "as": "h1", "style": {"font-size": "60px"}}},
                {"id": "contact-subtitle", "type": "Text", "props": {"content": "This form demonstrates state binding (v-model) and event handling.", "as": "p", "style": {"font-size": "20px", "color": "#aaa", "margin-bottom": "2rem"}}},
                
                {"id": "name-input", "type": "Textbox", "props": {
                    "modelValue": {"type": "stateBinding", "stateKey": "contactName"}, "placeholder": "Your Name",
                    "style": {"width": "100%", "padding": "1rem", "font-size": "16px", "border-radius": "8px", "border": "none", "margin-bottom": "1rem"}
                }, "events": {"input": [{"type": "action:setState", "stateKey": "contactName", "newValue": {"type": "expression", "value": "event.target.value"}}]}},
                
                {"id": "email-input", "type": "Textbox", "props": {
                    "modelValue": {"type": "stateBinding", "stateKey": "contactEmail"}, "placeholder": "Your Email",
                    "style": {"width": "100%", "padding": "1rem", "font-size": "16px", "border-radius": "8px", "border": "none", "margin-bottom": "2rem"}
                }, "events": {"input": [{"type": "action:setState", "stateKey": "contactEmail", "newValue": {"type": "expression", "value": "event.target.value"}}]}},

                {"id": "submit-btn", "type": "Button", "props": {"text": "Submit", "class": "btn-primary"},
                 "events": {"click": [{"type": "action:showAlert", "message": {"type": "expression", "value": "Thanks, ${state.contactName}! We'll email you at ${state.contactEmail}."}}]}}
            ]}
        }}
    ]
    patch_page("Contact", contact_page_patches, "Build Contact Page")
    
    print("\n--- Ultimate Demo Build COMPLETE! ---")
    print(f"Check the output in: {config.OUTPUT_DIR}")
    print(f"Then run:\n  cd {config.OUTPUT_DIR.name}\n  npm install\n  npm run dev")

if __name__ == "__main__":
    main()