# test_client_iphone.py
import requests
import json
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adjust path to import config
import config  # <-- Import the config

# --- V15: Read URL from config ---
BASE_URL = f"http://{config.HOST}:{config.PORT}"

# --- V15: Lorem Ipsum Helper ---
def lorem_ipsum(paragraphs=1):
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    return "\n\n".join([text] * paragraphs)

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

# --- V15: Apple Theme ---
def get_apple_theme_styles():
    return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background-color: #000;
  color: #fff;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* V18: Removed hardcoded #nav styles, now part of AST */

.page-container {
  max-width: 100%; /* Full width for hero sections */
  margin: 0 auto;
}

.content-width {
  max-width: 980px;
  margin: 0 auto;
  padding: 2rem;
}

h1, h2, h3, h4 {
  font-weight: 700;
  margin: 0;
  padding: 0;
}

/* --- Global Component Classes --- */
.btn-primary {
  background-color: #007aff;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 99px; /* Pill shape */
  cursor: pointer;
  transition: background-color 0.2s;
  text-decoration: none;
}
.btn-primary:hover {
  background-color: #0056b3;
}
/* V18: Added secondary button for pricing toggle */
.btn-secondary {
  background-color: #333;
  color: #fff;
  border: 1px solid #555;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 99px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-secondary:hover {
  background-color: #444;
}

.text-link {
  color: #007aff;
  text-decoration: none;
}
.text-link:hover {
  text-decoration: underline;
}

.icon-check {
  color: #34c759; /* Apple green */
  width: 1.5em;
  height: 1.5em;
  margin-right: 0.5rem;
}

.icon-chevron {
  width: 0.8em;
  height: 0.8em;
  margin-left: 0.25rem;
}
"""

# --- V15: Anchor Header ---
# This is a reusable chunk of JSON for the sticky header
def get_sticky_header(active_page="Home"):
    pages = ["Home", "Features", "Compare", "Pricing"]
    links = []
    for page in pages:
        # V18: Use router-link friendly hrefs
        href = f"#/{page.lower()}"
        if page == "Home": href = "#/"
        
        links.append({
            "id": f"nav-link-{page.lower()}",
            "type": "Link",
            "props": {
                "href": href,
                "text": page,
                "style": {
                    "color": "#fff" if page == active_page else "#888",
                    "text-decoration": "none",
                    "font-weight": "500",
                    "padding": "0 1rem",
                    "font-size": "14px"
                }
            },
            "slots": {"default": [{"id": f"nav-text-{page.lower()}", "type": "Text", "props": {"content": page}}]}
        })
    
    return {
        "id": "sticky-header", "type": "Box",
        "props": {
            "style": {
                "position": "sticky", "top": "0", "left": "0", "width": "100%",
                "display": "flex", "justify-content": "space-between", "align-items": "center",
                "padding": "1rem 2rem", "background": "rgba(0, 0, 0, 0.7)",
                "backdrop-filter": "blur(10px)", "-webkit-backdrop-filter": "blur(10px)",
                "z-index": "1000", "border-bottom": "1px solid #333",
                "box-sizing": "border-box" # V18: Add box-sizing
            }
        },
        "slots": { "default": [
            { "id": "header-logo", "type": "Text", "props": {"content": "iPhone 17 Pro", "as": "h3", "style": {"font-weight": "700"}}},
            { "id": "header-links", "type": "Box", "props": {"style": {"display": "flex"}}, "slots": {"default": links}},
            { "id": "header-buy-btn", "type": "Button", "props": {"text": "Buy", "class": "btn-primary", "style": {"padding": "5px 15px", "font-size": "14px"}}}
        ]}
    }


# --- Main Demo Script ---
def main():
    print("--- Starting iPhone 17 Pro Demo Build (V18 Client) ---")

    # --- Step 0: Clean Slate ---
    print("\n--- Step 0: Ensuring a clean slate ---")
    if config.PROJECT_CONFIG_FILE.exists(): os.remove(config.PROJECT_CONFIG_FILE)
    for f in config.AST_INPUT_DIR.glob("*.json"): os.remove(f)
    print("Clean slate confirmed.")

    # --- Step 1: Create Project & Global Theme ---
    create_project_patch = [
        {"op": "add", "path": "/projectName", "value": "iPhone 17 Pro"},
        {"op": "add", "path": "/globalStyles", "value": get_apple_theme_styles()},
        {"op": "add", "path": "/pages/-", "value": { "name": "Home", "path": "/", "astFile": "home.json" }},
        {"op": "add", "path": "/pages/-", "value": { "name": "Features", "path": "/features", "astFile": "features.json" }},
        {"op": "add", "path": "/pages/-", "value": { "name": "Compare", "path": "/compare", "astFile": "compare.json" }},
        {"op": "add", "path": "/pages/-", "value": { "name": "Pricing", "path": "/pricing", "astFile": "pricing.json" }}
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
                
                # --- V18: Hero Section (Overlay Fix) ---
                {
                    "id": "hero-section", "type": "Box",
                    "props": {
                        "id": "hero-section", # Anchor ID
                        "style": {
                            "height": "100vh", "width": "100%", "position": "relative",
                            "display": "flex", "flex-direction": "column", "justify-content": "center", "align-items": "center",
                            "text-align": "center", "overflow": "hidden"
                        }
                    },
                    "slots": { "default": [
                        # Background Image (Absolute)
                        { "id": "hero-img", "type": "Image", "props": {
                            "src": "https://picsum.photos/1920/1080?random=1", "alt": "iPhone Hero",
                            "style": {"position": "absolute", "top": "0", "left": "0", "width": "100%", "height": "100%", "object-fit": "cover", "z-index": "1"}
                        }},
                        # Gradient Overlay (Absolute)
                        { "id": "hero-gradient", "type": "Box", "props": {
                            "style": {"position": "absolute", "bottom": "0", "left": "0", "width": "100%", "height": "50%", "z-index": "2",
                                      "background": "linear-gradient(to top, #000 20%, transparent)"}
                        }},
                        # Text Content (Relative, z-index 3)
                        { "id": "hero-text-box", "type": "Box", "props": {"style": {"position": "relative", "z-index": "3"}},
                          "slots": {"default": [
                            { "id": "hero-title", "type": "Text", "props": {"content": "iPhone 17 Pro", "as": "h1", "style": {"font-size": "80px"}}},
                            { "id": "hero-subtitle", "type": "Text", "props": {"content": "The Future. Now.", "as": "p", "style": {"font-size": "32px", "color": "#ccc"}}}
                        ]}}
                    ]}
                },

                # --- V18: A20 Bionic Chip Section (Overlay Fix) ---
                {
                    "id": "chip-section", "type": "Box",
                    "props": {
                        "id": "chip-section", # Anchor ID
                        "style": { "height": "100vh", "width": "100%", "position": "relative", "display": "flex", "justify-content": "center", "align-items": "center", "overflow": "hidden"}
                    },
                    "slots": {"default": [
                        { "id": "chip-img", "type": "Image", "props": {
                            "src": "https://picsum.photos/1920/1080?random=2", "alt": "A20 Bionic",
                            "style": {"position": "absolute", "top": "0", "left": "0", "width": "100%", "height": "100%", "object-fit": "cover", "z-index": "1"}
                        }},
                        { "id": "chip-gradient", "type": "Box", "props": {
                            "style": {"position": "absolute", "bottom": "0", "left": "0", "width": "100%", "height": "50%", "z-index": "2",
                                      "background": "linear-gradient(to top, #000 20%, transparent)"}
                        }},
                        { "id": "chip-text", "type": "Box", "props": {"style": {"position": "relative", "z-index": "3", "text-align": "center"}},
                          "slots": {"default": [
                            { "id": "chip-title", "type": "Text", "props": {"content": "A20 Bionic", "as": "h2", "style": {"font-size": "60px"}}},
                            { "id": "chip-subtitle", "type": "Text", "props": {"content": "The most powerful chip ever in an iPhone.", "as": "p", "style": {"font-size": "24px", "color": "#ccc"}}}
                        ]}}
                    ]}
                },
                
                # --- V18: Pro Camera System Section (Overlay Fix) ---
                {
                    "id": "camera-section", "type": "Box",
                    "props": {
                        "id": "camera-section", # Anchor ID
                        "style": { "height": "100vh", "width": "100%", "position": "relative", "display": "flex", "justify-content": "center", "align-items": "center", "overflow": "hidden"}
                    },
                    "slots": {"default": [
                        { "id": "camera-img", "type": "Image", "props": {
                            "src": "https://picsum.photos/1920/1080?random=3", "alt": "Pro Camera",
                            "style": {"position": "absolute", "top": "0", "left": "0", "width": "100%", "height": "100%", "object-fit": "cover", "z-index": "1"}
                        }},
                        { "id": "camera-gradient", "type": "Box", "props": {
                            "style": {"position": "absolute", "bottom": "0", "left": "0", "width": "100%", "height": "50%", "z-index": "2",
                                      "background": "linear-gradient(to top, #000 20%, transparent)"}
                        }},
                        { "id": "camera-text", "type": "Box", "props": {"style": {"position": "relative", "z-index": "3", "text-align": "center"}},
                          "slots": {"default": [
                            { "id": "camera-title", "type": "Text", "props": {"content": "Pro Camera System", "as": "h2", "style": {"font-size": "60px"}}},
                            { "id": "camera-subtitle", "type": "Text", "props": {"content": "Capture your world like never before.", "as": "p", "style": {"font-size": "24px", "color": "#ccc"}}}
                        ]}}
                    ]}
                },

                # --- Footer ---
                {
                    "id": "footer", "type": "Box",
                    "props": {"style": {"text-align": "center", "padding": "3rem", "margin-top": "3rem", "border-top": "1px solid #333"}},
                    "slots": {"default": [
                        { "id": "footer-text", "type": "Text", "props": {"content": "Copyright © 2025 GenAI Inc. All rights reserved.", "as": "p", "style": {"font-size": "14px", "color": "#888"}}}
                    ]}
                }
            ]}
        }}
    ]
    if not patch_page("Home", home_page_patches, "Build Home Page"): return

    # --- Step 3: Build the Features Page (List, Icons) ---
    features_page_patches = [
        {"op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": {"class": "page-container"},
            "slots": { "default": [
                get_sticky_header(active_page="Features"), # Add sticky header
                { "id": "features-content", "type": "Box", "props": {"class": "content-width"}, "slots": {"default": [
                    { "id": "feat-title", "type": "Text", "props": {"content": "Pro Features", "as": "h1", "style": {"font-size": "60px", "text-align": "center", "margin": "3rem 0"}}},
                    
                    # V18: Use a List component, but populate its default slot
                    { "id": "feat-list-container", "type": "List", "props": {"class": "features-list", "style": {"list-style": "none", "padding": "0"}},
                      "slots": {"default": [
                        
                        # Feature Item 1
                        { "id": "feat-item-1", "type": "Box", "props": {"as": "li", "style": {"display": "flex", "align-items": "center", "font-size": "20px", "margin-bottom": "1rem"}},
                          "slots": {"default": [
                            { "id": "feat-icon-1", "type": "Icon", "props": {"svgPath": "M20 6L9 17l-5-5", "class": "icon-check", "viewBox": "0 0 24 24"} },
                            { "id": "feat-text-1", "type": "Text", "props": {"content": "Dynamic Island"} }
                          ]}},
                        
                        # Feature Item 2
                        { "id": "feat-item-2", "type": "Box", "props": {"as": "li", "style": {"display": "flex", "align-items": "center", "font-size": "20px", "margin-bottom": "1rem"}},
                          "slots": {"default": [
                            { "id": "feat-icon-2", "type": "Icon", "props": {"svgPath": "M20 6L9 17l-5-5", "class": "icon-check", "viewBox": "0 0 24 24"} },
                            { "id": "feat-text-2", "type": "Text", "props": {"content": "ProMotion Display (1-120Hz)"} }
                          ]}},

                        # Feature Item 3
                        { "id": "feat-item-3", "type": "Box", "props": {"as": "li", "style": {"display": "flex", "align-items": "center", "font-size": "20px", "margin-bottom": "1rem"}},
                          "slots": {"default": [
                            { "id": "feat-icon-3", "type": "Icon", "props": {"svgPath": "M20 6L9 17l-5-5", "class": "icon-check", "viewBox": "0 0 24 24"} },
                            { "id": "feat-text-3", "type": "Text", "props": {"content": "48MP Main Camera with 10x Optical Zoom"} }
                          ]}}
                      ]}}
                ]}}
            ]}
        }}
    ]
    patch_page("Features", features_page_patches, "Build Features Page")

    # --- Step 4: Build the Compare Page (Table) ---
    compare_page_patches = [
        {"op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": {"class": "page-container"},
            "slots": { "default": [
                get_sticky_header(active_page="Compare"), # Add sticky header
                { "id": "compare-content", "type": "Box", "props": {"class": "content-width"}, "slots": {"default": [
                    { "id": "compare-title", "type": "Text", "props": {"content": "Compare Models", "as": "h1", "style": {"font-size": "60px", "text-align": "center", "margin": "3rem 0"}}},
                    { "id": "compare-table", "type": "Table", "props": {
                        "headers": ["Feature", "iPhone 17 Pro", "iPhone 16 Pro"],
                        "rows": [
                            ["Chip", "A20 Bionic", "A19 Pro"],
                            ["Display", "ProMotion 1-120Hz", "ProMotion 10-120Hz"],
                            ["Camera", "48MP Main, 10x Optical Zoom", "48MP Main, 5x Optical Zoom"],
                            ["Material", "Titanium Grade 6", "Titanium Grade 5"]
                        ],
                        "style": {"width": "100%", "font-size": "18px", "border-collapse": "collapse", "text-align": "left"},
                        "class": "compare-table" # We can style this in globalStyles
                    }}
                ]}}
            ]}
        }}
    ]
    patch_page("Compare", compare_page_patches, "Build Compare Page")

    # --- Step 5: Build the Pricing Page (Stateful Toggle) ---
    pricing_page_patches = [
        {"op": "add", "path": "/state/pricingMode", "value": {"type": "string", "defaultValue": "full"}},
        {"op": "replace", "path": "/tree", "value": {
            "id": "root-container", "type": "Box",
            "props": {"class": "page-container"},
            "slots": { "default": [
                get_sticky_header(active_page="Pricing"), # Add sticky header
                { "id": "pricing-content", "type": "Box", "props": {"class": "content-width"}, "slots": {"default": [
                    { "id": "pricing-title", "type": "Text", "props": {"content": "Choose Your iPhone", "as": "h1", "style": {"font-size": "60px", "text-align": "center", "margin": "3rem 0"}}},
                    
                    # --- Toggle Button ---
                    { "id": "toggle-box", "type": "Box", "props": {"style": {"text-align": "center", "margin-bottom": "2rem"}},
                      "slots": {"default": [
                        { "id": "toggle-btn-full", "type": "Button", 
                          # V18: Use expression for class binding
                          "props": {"text": "Pay Full", "class": {"type": "expression", "value": "pricingMode === 'full' ? 'btn-primary' : 'btn-secondary'"}},
                          "events": {"click": [{"type": "action:setState", "stateKey": "pricingMode", "newValue": "full"}]}},
                        { "id": "toggle-btn-monthly", "type": "Button", 
                          "props": {"text": "Pay Monthly", "class": {"type": "expression", "value": "pricingMode === 'monthly' ? 'btn-primary' : 'btn-secondary'"}, "style": {"margin-left": "1rem"}},
                          "events": {"click": [{"type": "action:setState", "stateKey": "pricingMode", "newValue": "monthly"}]}},
                      ]}},

                    # --- Pricing Cards ---
                    { "id": "pricing-cards", "type": "Box", "props": {"style": {"display": "grid", "grid-template-columns": "1fr 1fr", "gap": "2rem"}},
                      "slots": {"default": [
                        
                        # Card 1: 17 Pro
                        { "id": "card-pro", "type": "Box", "props": {"style": {"border": "1px solid #333", "border-radius": "12px", "padding": "2rem"}},
                          "slots": {"default": [
                            { "id": "card-pro-title", "type": "Text", "props": {"content": "iPhone 17 Pro", "as": "h3", "style": {"font-size": "24px"}}},
                            # Conditional Price 1
                            { "id": "card-pro-price-full", "type": "Text", "props": {"content": "From $1199", "as": "p", "style": {"font-size": "32px", "margin": "1rem 0"}}, "v-if": {"expression": "pricingMode === 'full'"}},
                            { "id": "card-pro-price-monthly", "type": "Text", "props": {"content": "From $49.95/mo", "as": "p", "style": {"font-size": "32px", "margin": "1rem 0"}}, "v-if": {"expression": "pricingMode === 'monthly'"}},
                            { "id": "card-pro-btn", "type": "Button", "props": {"text": "Buy", "class": "btn-primary"}}
                          ]}},
                        
                        # Card 2: 17 Pro Max
                        { "id": "card-max", "type": "Box", "props": {"style": {"border": "1px solid #333", "border-radius": "12px", "padding": "2rem"}},
                          "slots": {"default": [
                            { "id": "card-max-title", "type": "Text", "props": {"content": "iPhone 17 Pro Max", "as": "h3", "style": {"font-size": "24px"}}},
                            # Conditional Price 2
                            { "id": "card-max-price-full", "type": "Text", "props": {"content": "From $1299", "as": "p", "style": {"font-size": "32px", "margin": "1rem 0"}}, "v-if": {"expression": "pricingMode === 'full'"}},
                            { "id": "card-max-price-monthly", "type": "Text", "props": {"content": "From $54.12/mo", "as": "p", "style": {"font-size": "32px", "margin": "1rem 0"}}, "v-if": {"expression": "pricingMode === 'monthly'"}},
                            { "id": "card-max-btn", "type": "Button", "props": {"text": "Buy", "class": "btn-primary"}}
                          ]}}
                      ]}}
                ]}}
            ]}
        }}
    ]
    patch_page("Pricing", pricing_page_patches, "Build Pricing Page")

    print("\n--- iPhone 17 Pro Demo Build COMPLETE! ---")
    print(f"Check the output in: {config.OUTPUT_DIR}")
    print(f"Then run:\n  cd {config.OUTPUT_DIR.name}\n  npm install --ignore-scripts\n  npm run dev")

if __name__ == "__main__":
    main()