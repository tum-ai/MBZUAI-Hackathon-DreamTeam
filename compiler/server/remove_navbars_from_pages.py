#!/usr/bin/env python3
"""
Utility script to remove navbar blocks from individual page ASTs
since they're now handled as shared components in project.json.
"""

import json
from pathlib import Path

def remove_navbar_from_ast(ast_file_path: Path):
    """Remove the navbar block from a page AST."""
    with open(ast_file_path, 'r') as f:
        data = json.load(f)
    
    # Navigate to the default slot of the root tree
    tree = data.get('tree', {})
    default_slot = tree.get('slots', {}).get('default', [])
    
    # Filter out any component with id="navbar"
    original_count = len(default_slot)
    filtered_slot = [comp for comp in default_slot if comp.get('id') != 'navbar']
    
    if len(filtered_slot) < original_count:
        tree['slots']['default'] = filtered_slot
        print(f"  Removed navbar from {ast_file_path.name}")
        
        # Also remove paddingTop adjustments from first section
        if filtered_slot:
            first_section = filtered_slot[0]
            style = first_section.get('props', {}).get('style', {})
            if 'paddingTop' in style:
                # Reset to normal padding
                del style['paddingTop']
                print(f"  Removed paddingTop adjustment from first section")
        
        # Save the modified AST
        with open(ast_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    else:
        print(f"  No navbar found in {ast_file_path.name}")
        return False

def main():
    """Process all page AST files."""
    inputs_dir = Path(__file__).parent / 'inputs'
    
    page_files = [
        'home-page.json',
        'about-page.json',
        'services-page.json',
        'contact-page.json'
    ]
    
    print("Removing navbars from individual page ASTs...")
    print("(They are now shared components in project.json)")
    print()
    
    for page_file in page_files:
        file_path = inputs_dir / page_file
        if file_path.exists():
            print(f"Processing {page_file}:")
            remove_navbar_from_ast(file_path)
        else:
            print(f"Warning: {page_file} not found")
    
    print()
    print("Done! Navbars removed from all pages.")
    print("The shared navbar in project.json will now be used.")

if __name__ == '__main__':
    main()
