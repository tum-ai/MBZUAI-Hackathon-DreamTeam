import requests
import json
import time
import os
import sys

# --- V1: Setup - Assuming config.py exists in the parent directory ---
# (This would be in your project's 'config.py')
# import pathlib
# BASE_DIR = pathlib.Path(__file__).parent.parent
# HOST = "localhost"
# PORT = 8008 # Example port
# PROJECT_CONFIG_FILE = BASE_DIR / "compiler" / "server" / "inputs" / "project.json"
# AST_INPUT_DIR = BASE_DIR / "compiler" / "server" / "inputs"
# OUTPUT_DIR = BASE_DIR / "generated-output"
# --- End of config.py example ---

# Adjust path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create it in the parent directory.")
    print("Using default values for demonstration.")
    
    # Mock config object if import fails, to allow script to be read
    class MockConfig:
        HOST = "localhost"
        PORT = 8008
        @property
        def PROJECT_CONFIG_FILE(self): return self.MockPath("project.json")
        @property
        def AST_INPUT_DIR(self): return self.MockPath("inputs")
        @property
        def OUTPUT_DIR(self): return self.MockPath("output")
        
        class MockPath:
            def __init__(self, path): self.path = path
            def exists(self): return False
            def glob(self, _): return []
            def __str__(self): return self.path
            def __truediv__(self, other): return self.MockPath(f"{self.path}/{other}")
    config = MockConfig()

# --- V2: Read URL from config ---
BASE_URL = f"http://{config.HOST}:{config.PORT}"

# --- Helper Functions (from test_client.py) ---
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

# --- V4: K2Ink Theme (Liquid Glass) ---
def get_k2ink_theme_styles():
    # Styles inspired by your 'Liquid Glass Design System' (README.md)
    return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background-color: #0B0F14;
  color: #fff;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.page-container {
  max-width: 100%;
  margin: 0 auto;
}

.content-width {
  max-width: 1100px;
  margin: 0 auto;
  padding: 4rem 2rem;
}

h1, h2, h3, h4 {
  font-weight: 700;
  margin: 0;
  padding: 0;
}

/* --- Global Component Classes --- */
.btn-primary {
  background-color: #6AA8FF;
  color: #0B0F14;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease-out;
  text-decoration: none;
}
.btn-primary:hover {
  filter: brightness(1.2);
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: transparent;
  color: #fff;
  border: 1px solid #333;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  text-decoration: none;
}
.btn-secondary:hover {
  background-color: #ffffff1a;
}

.glass-card {
  background: rgba(14, 18, 20, 0.5); /* From your tokens */
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem 2rem;
  height: 100%;
  box-sizing: border-box;
}

/* --- V4: Added Comparison Table Styles --- */
.comparison-table {
  width: 100%;
  font-size: 16px;
  border-collapse: collapse;
  text-align: left;
  margin-top: 2rem;
}
.comparison-table th, .comparison-table td {
  border: 1px solid #333;
  padding: 0.75rem 1rem;
}
.comparison-table th {
  background-color: #ffffff1a;
  font-weight: 700;
}
.comparison-table td:first-child {
  font-weight: 500;
  color: #eee;
}
"""

# --- V4: Sticky Header ---
def get_sticky_header(active_page="Home"):
    nav_links = [
        {"id": "nav-link-how", "type": "Link", "props": {"href": "#how-it-works", "text": "How It Works", "style": {"padding": "0 1rem", "font-size": "14px", "font-weight": "500", "color": "#ccc", "text-decoration": "none"}}},
        {"id": "nav-link-features", "type": "Link", "props": {"href": "#features", "text": "Features", "style": {"padding": "0 1rem", "font-size": "14px", "font-weight": "500", "color": "#ccc", "text-decoration": "none"}}},
        {"id": "nav-link-compare", "type": "Link", "props": {"href": "#compare", "text": "Compare", "style": {"padding": "0 1rem", "font-size": "14px", "font-weight": "500", "color": "#ccc", "text-decoration": "none"}}},
    ]
    
    return {
        "id": "sticky-header", "type": "Box",
        "props": {
            "style": {
                "position": "sticky", "top": "0", "left": "0", "width": "100%",
                "display": "flex", "justify-content": "space-between", "align-items": "center",
                "padding": "1rem 2rem", "background": "rgba(11, 15, 20, 0.7)",
                "backdrop-filter": "blur(10px)", "-webkit-backdrop-filter": "blur(10px)",
                "z-index": "1000", "border-bottom": "1px solid #333",
                "box-sizing": "border-box"
            }
        },
        "slots": { "default": [
            # V4: Renamed Product
            { "id": "header-logo", "type": "Text", "props": {"content": "K2Ink", "as": "h3", "style": {"font-weight": "700"}}},
            { "id": "header-links", "type": "Box", "props": {"style": {"display": "flex"}}, "slots": {"default": nav_links}},
            { "id": "header-signup-btn", "type": "Button", "props": {"text": "Join Waitlist", "class": "btn-primary", "style": {"padding": "8px 16px", "font-size": "14px"}}}
        ]}
    }


# --- Main Demo Script ---
def main():
    # V4: Renamed Product
    print("--- Starting K2Ink Demo Build (V2 Client) ---")

    # --- Step 0: Clean Slate ---
    print("\n--- Step 0: Ensuring a clean slate ---")
    if config.PROJECT_CONFIG_FILE.exists(): os.remove(config.PROJECT_CONFIG_FILE)
    for f in config.AST_INPUT_DIR.glob("*.json"): os.remove(f)
    print("Clean slate confirmed.")

    # --- Step 1: Create Project & Global Theme ---
    create_project_patch = [
        # V4: Renamed Product
        {"op": "add", "path": "/projectName", "value": "K2Ink"},
        {"op": "add", "path": "/globalStyles", "value": get_k2ink_theme_styles()},
        {"op": "add", "path": "/pages/-", "value": { "name": "Home", "path": "/", "astFile": "home.json" }},
    ]
    if not patch_project(create_project_patch, "Create Project & Theme"): return

    # --- Step 2: Build the Home (Landing) Page ---
    home_page_patches = [
        # Set root container
        {"op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": {"class": "page-container"},
            "slots": { "default": [
                get_sticky_header(active_page="Home"), # Add sticky header
                
                # --- Hero Section ---
                {
                    "id": "hero-section", "type": "Box",
                    "props": {
                        "id": "hero", # Anchor ID
                        "style": {
                            "height": "80vh", "width": "100%", "position": "relative",
                            "display": "flex", "flex-direction": "column", "justify-content": "center", "align-items": "center",
                            "text-align": "center", "padding": "0 2rem", "box-sizing": "border-box"
                        }
                    },
                    "slots": { "default": [
                        { "id": "hero-title", "type": "GradientText", "props": {
                            "content": "Build at the Speed of Thought.", 
                            "as": "h1", 
                            "style": {"font-size": "72px", "margin-bottom": "1rem"},
                            "gradient": "linear-gradient(to right, #6AA8FF, #D67CFF)"
                        }},
                        { "id": "hero-subtitle", "type": "Text", "props": {
                            "content": "A voice-first generative platform that compiles natural language into a deterministic UI Abstract Syntax Tree.", 
                            "as": "p", 
                            "style": {"font-size": "20px", "color": "#ccc", "max-width": "700px", "margin-bottom": "2rem"}
                        }},
                        { "id": "hero-cta-btn", "type": "Button", "props": {"text": "Join the Private Beta", "class": "btn-primary"}}
                    ]}
                },

                # --- How It Works Section ---
                {
                    "id": "how-it-works-section", "type": "Box",
                    "props": {"id": "how-it-works", "class": "content-width"},
                    "slots": {"default": [
                        { "id": "how-title", "type": "Text", "props": {"content": "From Voice to Code. Deterministically.", "as": "h2", "style": {"font-size": "48px", "text-align": "center", "margin-bottom": "3rem"}}},
                        { "id": "how-grid", "type": "Box", "props": {"style": {"display": "grid", "grid-template-columns": "repeat(4, 1fr)", "gap": "1.5rem"}},
                          "slots": {"default": [
                            # Step 1: Intent
                            { "id": "how-card-1", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "how-card-1-title", "type": "Text", "props": {"content": "1. Intent", "as": "h3", "style": {"color": "#6AA8FF", "margin-bottom": "1rem"}}},
                                { "id": "how-card-1-text", "type": "Text", "props": {"content": "Speak your request. Our agentic system (Planner & Clarifier) understands your natural language intent.", "style": {"color": "#eee"}}}
                            ]}},
                            # Step 2: Compile
                            { "id": "how-card-2", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "how-card-2-title", "type": "Text", "props": {"content": "2. Compile", "as": "h3", "style": {"color": "#6AA8FF", "margin-bottom": "1rem"}}},
                                { "id": "how-card-2-text", "type": "Text", "props": {"content": "The 'LLM AST Compiler' generates a structured JSON Patch, not raw code. This is a safe, abstract command.", "style": {"color": "#eee"}}}
                            ]}},
                            # Step 3: Update
                            { "id": "how-card-3", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "how-card-3-title", "type": "Text", "props": {"content": "3. Update AST", "as": "h3", "style": {"color": "#6AA8FF", "margin-bottom": "1rem"}}},
                                { "id": "how-card-3-text", "type": "Text", "props": {"content": "Your 'ui-tree.json' (the AST) is updated. This file is now the single source of truth for your entire application.", "style": {"color": "#eee"}}}
                            ]}},
                            # Step 4: Generate
                            { "id": "how-card-4", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "how-card-4-title", "type": "Text", "props": {"content": "4. Generate", "as": "h3", "style": {"color": "#6AA8FF", "margin-bottom": "1rem"}}},
                                { "id": "how-card-4-text", "type": "Text", "props": {"content": "A 100% deterministic Python generator compiles the new AST into perfect, framework-native code (React, Vue, etc).", "style": {"color": "#eee"}}}
                            ]}},
                          ]}}
                    ]}
                },
                
                # --- Features Section ---
                {
                    "id": "features-section", "type": "Box",
                    "props": {"id": "features", "class": "content-width"},
                    "slots": {"default": [
                        { "id": "feat-title", "type": "Text", "props": {"content": "An Unprecedented Workflow.", "as": "h2", "style": {"font-size": "48px", "text-align": "center", "margin-bottom": "3rem"}}},
                        { "id": "feat-grid", "type": "Box", "props": {"style": {"display": "grid", "grid-template-columns": "1fr 1fr", "gap": "1.5rem"}},
                          "slots": {"default": [
                            # Feature 1
                            { "id": "feat-card-1", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "feat-card-1-title", "type": "Text", "props": {"content": "Voice-First Agentic System", "as": "h3", "style": {"margin-bottom": "1rem"}}},
                                { "id": "feat-card-1-text", "type": "Text", "props": {"content": "Use natural language to build. Our 'Bixby-like' assistant uses Planner, Editor, and Clarifier agents to handle ambiguity and execute complex tasks.", "style": {"color": "#ccc", "line-height": "1.6"}}}
                            ]}},
                            # Feature 2
                            { "id": "feat-card-2", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "feat-card-2-title", "type": "Text", "props": {"content": "AST as Source of Truth", "as": "h3", "style": {"margin-bottom": "1rem"}}},
                                { "id": "feat-card-2-text", "type": "Text", "props": {"content": "Eliminate state drift and brittle code. Your UI is 100% defined by the 'ui-tree.json' AST. To change the UI, you must change the AST.", "style": {"color": "#ccc", "line-height": "1.6"}}}
                            ]}},
                            # Feature 3
                            { "id": "feat-card-3", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "feat-card-3-title", "type": "Text", "props": {"content": "Deterministic Generation", "as": "h3", "style": {"margin-bottom": "1rem"}}},
                                { "id": "feat-card-3-text", "type": "Text", "props": {"content": "Our generator is a 'pure function'. The same AST input will always produce the exact same code output, making your UI predictable and testable.", "style": {"color": "#ccc", "line-height": "1.6"}}}
                            ]}},
                            # Feature 4
                            { "id": "feat-card-4", "type": "Box", "props": {"class": "glass-card"}, "slots": {"default": [
                                { "id": "feat-card-4-title", "type": "Text", "props": {"content": "Framework-Agnostic", "as": "h3", "style": {"margin-bottom": "1rem"}}},
                                { "id": "feat-card-4-text", "type": "Text", "props": {"content": "Use Component Manifests (schema-driven JSON) to teach the generator. Target React, Vue, Angular, and more, all from the same abstract AST.", "style": {"color": "#ccc", "line-height": "1.6"}}}
                            ]}},
                          ]}}
                    ]}
                },

                # --- V4: NEW Comparison Section ---
                {
                    "id": "comparison-section", "type": "Box",
                    "props": {"id": "compare", "class": "content-width"},
                    "slots": {"default": [
                        { "id": "compare-title", "type": "Text", "props": {"content": "Compare Our Approach", "as": "h2", "style": {"font-size": "48px", "text-align": "center", "margin-bottom": "1rem"}}},
                        { "id": "compare-subtitle", "type": "Text", "props": {"content": "K2Ink isn't just another 'AI website builder'. It's a deterministic compiler.", "as": "p", "style": {"font-size": "18px", "color": "#ccc", "text-align": "center", "margin-bottom": "2rem"}}},
                        { "id": "compare-table", "type": "Table", "props": {
                            "class": "comparison-table",
                            "headers": ["Feature", "K2Ink (AST Compiler)", "Gen-AI Tools (e.g., Lovable)", "Manual Coding"],
                            "rows": [
                                ["Source of Truth", "Deterministic AST (ui-tree.json)", "Proprietary UI (Black Box)", "Raw Code Files (.tsx, .vue)"],
                                ["Output", "Deterministic, framework-native code", "LLM-generated, brittle code", "Human-written (slow, error-prone)"],
                                ["Modification", "Safe JSON Patch on AST", "Ambiguous 'prompt-to-edit' (Risky)", "Manual Refactoring"],
                                ["State Management", "Abstracted in AST (e.g., 'action:setState')", "Handled by Platform", "Manual (e.g., useState, Pinia)"],
                                ["Extensibility", "Via Component Manifests (JSON)", "Limited by Platform Features", "Unlimited (but complex)"],
                                ["Workflow", "Voice -> AST -> Code", "Voice -> Code", "Keyboard -> Code"]
                            ]
                        }}
                    ]}
                },
                
                # --- Footer ---
                {
                    "id": "footer", "type": "Box",
                    "props": {"style": {"text-align": "center", "padding": "3rem", "margin-top": "3rem", "border-top": "1px solid #333"}},
                    "slots": {"default": [
                        # V4: Renamed
                        { "id": "footer-text", "type": "Text", "props": {"content": "Copyright © 2025 TUM.ai DreamTeam. All rights reserved.", "as": "p", "style": {"font-size": "14px", "color": "#888"}}}
                    ]}
                }
            ]}
        }}
    ]
    if not patch_page("Home", home_page_patches, "Build Home Page"): return


    print(f"\n--- K2Ink Demo Build COMPLETE! ---")
    print(f"Check the output in: {config.OUTPUT_DIR}")
    print(f"Then run:\n  cd {config.OUTPUT_DIR.name}\n  npm install --ignore-scripts\n  npm run dev")

if __name__ == "__main__":
    main()