#!/usr/bin/env python3
"""
Test script for template selection workflow.
Tests generating 4 variations, then selecting one as active.
"""

import requests
import json
import time
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"

def check_server():
    """Check if server is running."""
    try:
        response = requests.get(f"{API_BASE}/project", timeout=2)
        return response.status_code in [200, 404]
    except:
        return False

def generate_templates():
    """Generate 4 template variations."""
    print("\n" + "="*60)
    print("Step 1: Generating 4 Template Variations")
    print("="*60)
    
    payload = {
        "template_type": "product",
        "variables": {
            "productName": "iPhone 16 Pro",
            "tagline": "Titanium. So Pro.",
            "heroImage": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=1920",
            "features": [
                {"title": "A18 Pro Chip", "description": "Blazing fast performance"},
                {"title": "Pro Camera", "description": "48MP with 10x zoom"},
                {"title": "All-Day Battery", "description": "Up to 29 hours"}
            ],
            "specs": [
                {"label": "Display", "value": "6.3\" Super Retina XDR"},
                {"label": "Chip", "value": "A18 Pro"},
                {"label": "Storage", "value": "Up to 1TB"}
            ],
            "galleryImages": [
                "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800",
                "https://images.unsplash.com/photo-1695048133364-1d2b3a8b4a0f?w=800"
            ]
        }
    }
    
    response = requests.post(f"{API_BASE}/generate-template-variations", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Success!")
        print(f"  Generated {len(result['variations'])} variations")
        print(f"  Selection dir: {result['selection_dir']}")
        print(f"  Active project dir: {result.get('active_project_dir', 'N/A')}")
        
        print("\n  Variations created:")
        for var in result['variations']:
            print(f"    [{var['index']}] {var['palette']:12} + {var['font']:8} → {var['path']}")
        
        return True
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(f"  Error: {response.text[:300]}")
        return False

def select_variation(index):
    """Select a variation as active."""
    print("\n" + "="*60)
    print(f"Step 2: Selecting Variation {index} as Active")
    print("="*60)
    
    payload = {"variation_index": index}
    response = requests.post(f"{API_BASE}/select-template-variation", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Success!")
        print(f"  Selected: Variation {result['selected_variation']}")
        print(f"  Palette: {result['palette']}")
        print(f"  Font: {result['font']}")
        print(f"  Active path: {result['active_project_path']}")
        print(f"  Project name: {result['project_name']}")
        print(f"  Pages: {', '.join(result['pages'])}")
        
        print("\n  🌐 Port Configuration:")
        ports = result['preview_ports']
        print(f"    Variation 0 (Professional): http://localhost:{ports['variation_0']}")
        print(f"    Variation 1 (Dark):         http://localhost:{ports['variation_1']}")
        print(f"    Variation 2 (Minimal):      http://localhost:{ports['variation_2']}")
        print(f"    Variation 3 (Energetic):    http://localhost:{ports['variation_3']}")
        print(f"    ⭐ Active (Selected):        http://localhost:{ports['active']} ⭐")
        
        return True
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(f"  Error: {response.text[:300]}")
        return False

def get_active_project():
    """Get info about active project."""
    print("\n" + "="*60)
    print("Step 3: Checking Active Project Status")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/active-project")
    
    if response.status_code == 200:
        result = response.json()
        
        if result['status'] == 'active':
            print("\n✅ Active project is set!")
            print(f"  Status: {result['status']}")
            print(f"  Path: {result['active_project_path']}")
            print(f"  Project: {result['project_name']}")
            print(f"  Pages: {', '.join(result['pages'])}")
            print(f"  Container port: {result['container_port']}")
            print(f"  Message: {result['message']}")
        else:
            print(f"\nℹ️  Status: {result['status']}")
            print(f"  Message: {result['message']}")
        
        return True
    else:
        print(f"\n❌ Failed: {response.status_code}")
        return False

def verify_file_structure():
    """Verify the file structure is correct."""
    print("\n" + "="*60)
    print("Step 4: Verifying File Structure")
    print("="*60)
    
    selection_dir = Path("/tmp/selection")
    active_dir = Path("/tmp/active")
    
    # Check variations
    print("\n  Checking variations:")
    for i in range(4):
        var_dir = selection_dir / str(i)
        has_package = (var_dir / "package.json").exists()
        has_src = (var_dir / "src").exists()
        status = "✅" if has_package and has_src else "❌"
        print(f"    {status} Variation {i}: {var_dir}")
    
    # Check active
    print("\n  Checking active project:")
    has_package = (active_dir / "package.json").exists()
    has_src = (active_dir / "src").exists()
    has_project = (active_dir / "project.json").exists()
    status = "✅" if has_package and has_src and has_project else "❌"
    print(f"    {status} Active: {active_dir}")
    
    if has_package and has_src and has_project:
        # Show which pages exist
        views_dir = active_dir / "src" / "views"
        if views_dir.exists():
            vue_files = list(views_dir.glob("*.vue"))
            print(f"    Pages: {', '.join([f.stem for f in vue_files])}")

def main():
    print("="*60)
    print("Template Selection Workflow Test")
    print("="*60)
    
    # Check server
    if not check_server():
        print("\n❌ Error: Server is not running!")
        print("  Start the server first:")
        print("  cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server")
        print("  python run_server.py")
        return
    
    print("\n✅ Server is running")
    
    # Step 1: Generate templates
    if not generate_templates():
        return
    
    time.sleep(1)
    
    # Step 2: Select variation 1 (Dark theme)
    if not select_variation(1):
        return
    
    time.sleep(1)
    
    # Step 3: Check active project
    get_active_project()
    
    # Step 4: Verify file structure
    verify_file_structure()
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("\n✅ Template selection workflow complete!")
    print("\n📁 Directory Structure:")
    print("  /tmp/selection/0  → Professional palette (preview)")
    print("  /tmp/selection/1  → Dark palette (preview)")
    print("  /tmp/selection/2  → Minimal palette (preview)")
    print("  /tmp/selection/3  → Energetic palette (preview)")
    print("  /tmp/active       → Selected variation (editable)")
    
    print("\n🌐 To run all servers:")
    print("  cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server")
    print("  ./run_variations.sh")
    
    print("\n📝 Container should now:")
    print("  1. Watch /tmp/selection/{0,1,2,3} for previews")
    print("  2. Watch /tmp/active for the editable version")
    print("  3. Run dev servers on ports 5173-5177")
    print("  4. When user edits, only /tmp/active changes")

if __name__ == "__main__":
    main()
