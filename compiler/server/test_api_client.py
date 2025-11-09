#!/usr/bin/env python3
"""
API Client for the Vue Bits Generator Server

This script demonstrates how to programmatically create a multi-page
website by sending JSON patches to the FastAPI server.

Usage:
    python test_api_client.py

The server must be running on http://localhost:8000
Start it with: python run_server.py
"""

import requests
import json
import sys
from typing import Dict, List, Any


class VueBitsAPIClient:
    """
    Client for interacting with the Vue Bits Generator Server API.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def get_project_config(self) -> Dict:
        """Get the current project configuration."""
        response = requests.get(f"{self.base_url}/project")
        response.raise_for_status()
        return response.json()
    
    def patch_project_config(self, patches: List[Dict]) -> Dict:
        """
        Apply JSON patches to the project configuration.
        
        Args:
            patches: List of JSON Patch operations (RFC 6902)
            
        Returns:
            The patched project configuration
        """
        response = requests.patch(
            f"{self.base_url}/project",
            json=patches,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def get_page_ast(self, page_name: str) -> Dict:
        """Get the AST for a specific page."""
        response = requests.get(f"{self.base_url}/ast/{page_name}")
        response.raise_for_status()
        return response.json()
    
    def patch_page_ast(self, page_name: str, patches: List[Dict]) -> Dict:
        """
        Apply JSON patches to a page's AST.
        
        Args:
            page_name: Name of the page (e.g., 'home', 'about')
            patches: List of JSON Patch operations (RFC 6902)
            
        Returns:
            The patched page AST
        """
        response = requests.patch(
            f"{self.base_url}/ast/{page_name}",
            json=patches,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def clean(self, mode: str = "all") -> Dict:
        """
        Clean generated files, cache, and/or orphaned inputs.
        
        Args:
            mode: Cleaning mode - 'all', 'cache-only', 'files-only', or 'inputs'
            
        Returns:
            Status and list of removed items
        """
        response = requests.post(
            f"{self.base_url}/clean",
            params={"mode": mode}
        )
        response.raise_for_status()
        return response.json()


def create_sample_website(client: VueBitsAPIClient):
    """
    Creates a complete sample website from scratch using the API.
    This demonstrates the full workflow.
    """
    
    print("=" * 70)
    print("Creating a Sample Website via API")
    print("=" * 70)
    print()
    
    # Step 1: Set up project configuration
    print("Step 1: Setting up project configuration...")
    project_patches = [
        {
            "op": "replace",
            "path": "/projectName",
            "value": "api-generated-site"
        },
        {
            "op": "replace",
            "path": "/globalStyles",
            "value": "@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');\n\nbody { font-family: 'Poppins', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; }"
        },
        {
            "op": "add",
            "path": "/pages/-",
            "value": {
                "name": "Landing",
                "path": "/",
                "astFile": "landing.json"
            }
        }
    ]
    
    try:
        result = client.patch_project_config(project_patches)
        print(f"✓ Project configured: {result['data']['projectName']}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error configuring project: {e}")
        return
    
    print()
    
    # Step 2: Create landing page content
    print("Step 2: Creating landing page with hero section...")
    
    landing_patches = [
        {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": {
                "id": "hero-box",
                "type": "Box",
                "props": {
                    "style": {
                        "minHeight": "100vh",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "padding": "2rem",
                        "textAlign": "center"
                    }
                },
                "slots": {
                    "default": [
                        {
                            "id": "hero-title",
                            "type": "GradientText",
                            "props": {
                                "content": "Welcome to Vue Bits",
                                "as": "h1",
                                "style": {
                                    "fontSize": "4rem",
                                    "fontWeight": "700",
                                    "marginBottom": "1rem"
                                }
                            },
                            "slots": {}
                        },
                        {
                            "id": "hero-subtitle",
                            "type": "Text",
                            "props": {
                                "content": "Build beautiful websites with our component library",
                                "as": "p",
                                "style": {
                                    "fontSize": "1.5rem",
                                    "opacity": "0.9",
                                    "marginBottom": "2rem"
                                }
                            },
                            "slots": {}
                        },
                        {
                            "id": "hero-cta",
                            "type": "Button",
                            "props": {
                                "style": {
                                    "padding": "1rem 3rem",
                                    "fontSize": "1.2rem",
                                    "background": "#fff",
                                    "color": "#667eea",
                                    "border": "none",
                                    "borderRadius": "50px",
                                    "cursor": "pointer",
                                    "fontWeight": "600",
                                    "boxShadow": "0 4px 15px rgba(0,0,0,0.2)"
                                }
                            },
                            "slots": {
                                "default": [
                                    {
                                        "id": "cta-text",
                                        "type": "Text",
                                        "props": {
                                            "content": "Get Started"
                                        },
                                        "slots": {}
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    ]
    
    try:
        result = client.patch_page_ast("landing", landing_patches)
        print("✓ Landing page created with hero section")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating landing page: {e}")
        return
    
    print()
    
    # Step 3: Add a features section
    print("Step 3: Adding features section to landing page...")
    
    features_patches = [
        {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": {
                "id": "features-section",
                "type": "Box",
                "props": {
                    "style": {
                        "padding": "4rem 2rem",
                        "background": "rgba(255,255,255,0.1)",
                        "backdropFilter": "blur(10px)"
                    }
                },
                "slots": {
                    "default": [
                        {
                            "id": "features-title",
                            "type": "Text",
                            "props": {
                                "content": "Amazing Features",
                                "as": "h2",
                                "style": {
                                    "fontSize": "2.5rem",
                                    "textAlign": "center",
                                    "marginBottom": "3rem"
                                }
                            },
                            "slots": {}
                        },
                        {
                            "id": "features-grid",
                            "type": "Box",
                            "props": {
                                "style": {
                                    "display": "grid",
                                    "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                                    "gap": "2rem",
                                    "maxWidth": "1200px",
                                    "margin": "0 auto"
                                }
                            },
                            "slots": {
                                "default": [
                                    {
                                        "id": "feature-1",
                                        "type": "Card",
                                        "props": {
                                            "style": {
                                                "padding": "2rem",
                                                "background": "rgba(255,255,255,0.05)",
                                                "borderRadius": "15px",
                                                "border": "1px solid rgba(255,255,255,0.2)"
                                            }
                                        },
                                        "slots": {
                                            "default": [
                                                {
                                                    "id": "feature-1-title",
                                                    "type": "Text",
                                                    "props": {
                                                        "content": "⚡ Fast",
                                                        "as": "h3",
                                                        "style": {"fontSize": "1.5rem", "marginBottom": "1rem"}
                                                    },
                                                    "slots": {}
                                                },
                                                {
                                                    "id": "feature-1-desc",
                                                    "type": "Text",
                                                    "props": {
                                                        "content": "Lightning fast build times with Vite",
                                                        "as": "p"
                                                    },
                                                    "slots": {}
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "id": "feature-2",
                                        "type": "Card",
                                        "props": {
                                            "style": {
                                                "padding": "2rem",
                                                "background": "rgba(255,255,255,0.05)",
                                                "borderRadius": "15px",
                                                "border": "1px solid rgba(255,255,255,0.2)"
                                            }
                                        },
                                        "slots": {
                                            "default": [
                                                {
                                                    "id": "feature-2-title",
                                                    "type": "Text",
                                                    "props": {
                                                        "content": "🎨 Beautiful",
                                                        "as": "h3",
                                                        "style": {"fontSize": "1.5rem", "marginBottom": "1rem"}
                                                    },
                                                    "slots": {}
                                                },
                                                {
                                                    "id": "feature-2-desc",
                                                    "type": "Text",
                                                    "props": {
                                                        "content": "Stunning pre-built components",
                                                        "as": "p"
                                                    },
                                                    "slots": {}
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "id": "feature-3",
                                        "type": "Card",
                                        "props": {
                                            "style": {
                                                "padding": "2rem",
                                                "background": "rgba(255,255,255,0.05)",
                                                "borderRadius": "15px",
                                                "border": "1px solid rgba(255,255,255,0.2)"
                                            }
                                        },
                                        "slots": {
                                            "default": [
                                                {
                                                    "id": "feature-3-title",
                                                    "type": "Text",
                                                    "props": {
                                                        "content": "🚀 Easy",
                                                        "as": "h3",
                                                        "style": {"fontSize": "1.5rem", "marginBottom": "1rem"}
                                                    },
                                                    "slots": {}
                                                },
                                                {
                                                    "id": "feature-3-desc",
                                                    "type": "Text",
                                                    "props": {
                                                        "content": "Simple API-driven development",
                                                        "as": "p"
                                                    },
                                                    "slots": {}
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    ]
    
    try:
        result = client.patch_page_ast("landing", features_patches)
        print("✓ Features section added with 3 feature cards")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error adding features: {e}")
        return
    
    print()
    print("=" * 70)
    print("✓ Website created successfully!")
    print("=" * 70)
    print()
    print("The generator should have automatically built the Vue.js project.")
    print("Check: compiler/output/my-new-site/")
    print()


def demonstrate_incremental_update(client: VueBitsAPIClient):
    """
    Demonstrates incremental updates - changing just one component.
    """
    
    print("=" * 70)
    print("Demonstrating Incremental Update")
    print("=" * 70)
    print()
    
    print("Updating the hero title text only...")
    
    patches = [
        {
            "op": "replace",
            "path": "/tree/slots/default/0/slots/default/0/props/content",
            "value": "Vue Bits - Updated!"
        }
    ]
    
    try:
        result = client.patch_page_ast("landing", patches)
        print("✓ Hero title updated")
        print("  Only the Landing page should have been regenerated (incremental)")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error updating page: {e}")
    
    print()


def main():
    """Main entry point."""
    
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                  Vue Bits Generator - API Client                     ║")
    print("║                     Programmatic Website Builder                     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Initialize client
    client = VueBitsAPIClient()
    
    # Test connection
    print("Testing connection to server...")
    try:
        config = client.get_project_config()
        print(f"✓ Connected to server")
        print(f"  Current project: {config.get('projectName', 'N/A')}")
        print()
    except requests.exceptions.RequestException as e:
        print(f"✗ Could not connect to server at http://localhost:8000")
        print(f"  Error: {e}")
        print()
        print("Make sure the server is running:")
        print("  cd compiler/server")
        print("  python run_server.py")
        print()
        sys.exit(1)
    
    # Menu
    print("What would you like to do?")
    print("  1. Create a sample website from scratch")
    print("  2. Demonstrate incremental update (requires sample site)")
    print("  3. View current project config")
    print("  4. Clean generated files (various modes)")
    print("  5. Exit")
    print()
    
    choice = input("Enter your choice (1-5): ").strip()
    print()
    
    if choice == "1":
        create_sample_website(client)
    elif choice == "2":
        demonstrate_incremental_update(client)
    elif choice == "3":
        config = client.get_project_config()
        print("Current Project Configuration:")
        print("=" * 70)
        print(json.dumps(config, indent=2))
        print()
    elif choice == "4":
        print("Clean Options:")
        print("  1. Clean all (files + cache)")
        print("  2. Clean cache only")
        print("  3. Clean generated files only")
        print("  4. Clean orphaned input files")
        print()
        clean_choice = input("Enter clean mode (1-4): ").strip()
        print()
        
        mode_map = {
            "1": "all",
            "2": "cache-only",
            "3": "files-only",
            "4": "inputs"
        }
        
        mode = mode_map.get(clean_choice)
        if mode:
            try:
                result = client.clean(mode)
                print(f"✓ Clean completed (mode: {result['mode']})")
                print(f"  Removed {result['count']} items:")
                for item in result['removed_items']:
                    print(f"    - {item}")
                print()
            except requests.exceptions.RequestException as e:
                print(f"✗ Error cleaning: {e}")
        else:
            print("Invalid clean mode.")
    elif choice == "5":
        print("Goodbye!")
    else:
        print("Invalid choice. Exiting.")
    
    print()


if __name__ == "__main__":
    main()
