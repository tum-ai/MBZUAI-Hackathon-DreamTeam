# test_ast_directly.py
"""
Helper script to test an AST file directly without going through the server.
This bypasses the patch system and directly generates output from an AST.

Usage: python test_ast_directly.py <ast_file.json> <page_name>
Example: python test_ast_directly.py tests/test-enhanced.json Home
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.project_generator import ProjectGenerator

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_ast_directly.py <ast_file.json> <page_name>")
        print("Example: python test_ast_directly.py tests/test-enhanced.json Home")
        sys.exit(1)

    ast_file = sys.argv[1]
    page_name = sys.argv[2]
    
    if not os.path.exists(ast_file):
        print(f"Error: AST file not found: {ast_file}")
        sys.exit(1)
    
    # Load the AST
    try:
        with open(ast_file, 'r') as f:
            ast_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {ast_file}: {e}")
        sys.exit(1)
    
    print(f"Loaded AST from {ast_file}")
    print(f"Creating page: {page_name}")
    
    # Clean up old files
    print("\n--- Cleaning up old files ---")
    if config.PROJECT_CONFIG_FILE.exists():
        os.remove(config.PROJECT_CONFIG_FILE)
        print(f"Removed {config.PROJECT_CONFIG_FILE}")
    
    for f in config.AST_INPUT_DIR.glob("*.json"):
        os.remove(f)
        print(f"Removed {f}")
    
    # Create project config
    project_config = {
        "projectName": "test-enhanced-site",
        "globalStyles": "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');\nbody { font-family: 'Inter', sans-serif; background-color: #0a0a0a; color: #fff; margin: 0; padding: 0; }",
        "pages": [
            {
                "name": page_name,
                "path": "/" if page_name.lower() == "home" else f"/{page_name.lower()}",
                "astFile": f"{page_name.lower()}.json"
            }
        ]
    }
    
    # Write project config
    with open(config.PROJECT_CONFIG_FILE, 'w') as f:
        json.dump(project_config, f, indent=2)
    print(f"\nCreated {config.PROJECT_CONFIG_FILE}")
    
    # Write AST file
    ast_output_path = config.AST_INPUT_DIR / f"{page_name.lower()}.json"
    with open(ast_output_path, 'w') as f:
        json.dump(ast_data, f, indent=2)
    print(f"Created {ast_output_path}")
    
    # Generate the project
    print("\n--- Generating project ---")
    try:
        generator = ProjectGenerator()
        generator.generate_project()
        print(f"\n✅ Success! Project generated at: {config.OUTPUT_DIR}")
        print(f"\nTo view the result:")
        print(f"  cd {config.OUTPUT_DIR}")
        print(f"  npm install")
        print(f"  npm run dev")
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
