#!/usr/bin/env python3
"""
Template System Demo
Demonstrates all features of the template system.
"""

import json
from templates import (
    generate_from_template,
    get_available_templates,
    get_template_info
)

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def demo_list_templates():
    """Demo: List available templates."""
    print_section("1. Available Templates")
    templates = get_available_templates()
    for template in templates:
        print(f"  ✓ {template}")

def demo_template_info():
    """Demo: Get template information."""
    print_section("2. Template Information")
    info = get_template_info("portfolio")
    print(f"Name: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"\nRequired Variables:")
    for key, desc in info['required_variables'].items():
        print(f"  • {key}: {desc}")
    print(f"\nOptional Variables (showing first 5):")
    for i, (key, desc) in enumerate(list(info['optional_variables'].items())[:5]):
        print(f"  • {key}: {desc}")
    print("  ... and more")

def demo_simple_generation():
    """Demo: Simple portfolio generation."""
    print_section("3. Simple Portfolio Generation")
    
    variables = {
        "name": "Demo User",
        "tagline": "Web Developer",
        "palette": "professional"
    }
    
    print("Variables:")
    print(json.dumps(variables, indent=2))
    
    print("\nGenerating...")
    patches = generate_from_template("portfolio", variables)
    
    print(f"\n✓ Generated {len(patches)} JSON Patch operations")
    print(f"✓ Total size: {len(json.dumps(patches))} bytes")
    
    # Show first patch (global styles)
    print("\nFirst patch (global styles preview):")
    first_patch = patches[0]
    print(f"  Operation: {first_patch['op']}")
    print(f"  Path: {first_patch['path']}")
    print(f"  Value (first 100 chars): {first_patch['value'][:100]}...")

def demo_custom_sections():
    """Demo: Portfolio with custom sections."""
    print_section("4. Portfolio with Custom Sections")
    
    variables = {
        "name": "Alice Johnson",
        "tagline": "UX Designer & Researcher",
        "palette": "personal",
        "fonts": "elegant",
        "sections": ["about", "experience", "education", "contact"],
        "experience": [
            {
                "title": "Senior UX Designer",
                "company": "Tech Corp",
                "period": "2020-Present",
                "description": "Leading design initiatives"
            }
        ],
        "education": [
            {
                "degree": "Master of Design",
                "school": "Design University",
                "year": "2019",
                "description": "Focus on human-computer interaction"
            }
        ]
    }
    
    print("Generating portfolio with:")
    print(f"  • Palette: {variables['palette']}")
    print(f"  • Fonts: {variables['fonts']}")
    print(f"  • Sections: {', '.join(variables['sections'])}")
    print(f"  • {len(variables['experience'])} experience entry")
    print(f"  • {len(variables['education'])} education entry")
    
    patches = generate_from_template("portfolio", variables)
    
    print(f"\n✓ Generated {len(patches)} patches")

def demo_all_palettes():
    """Demo: Generate with different palettes."""
    print_section("5. Palette Variations")
    
    palettes = ["professional", "personal", "quirky", "dark", "minimal"]
    
    for palette in palettes:
        variables = {
            "name": "Test User",
            "tagline": "Developer",
            "palette": palette,
            "sections": ["about"]
        }
        
        patches = generate_from_template("portfolio", variables)
        
        # Extract color from global styles
        global_styles = patches[0]["value"]
        bg_color = global_styles.split("background-color:")[1].split(";")[0].strip()
        text_color = global_styles.split("color:")[1].split(";")[0].strip()
        
        print(f"  {palette:15} → bg: {bg_color:9} text: {text_color}")

def demo_performance():
    """Demo: Performance test."""
    print_section("6. Performance Test")
    
    import time
    
    variables = {
        "name": "Performance Test",
        "tagline": "Speed Matters",
        "sections": ["about", "projects", "skills", "contact"],
        "skills": ["Skill " + str(i) for i in range(20)],
        "projects": [
            {"title": f"Project {i}", "description": "Test project"}
            for i in range(10)
        ]
    }
    
    print(f"Generating portfolio with:")
    print(f"  • 4 sections")
    print(f"  • 20 skills")
    print(f"  • 10 projects")
    
    start = time.time()
    patches = generate_from_template("portfolio", variables)
    end = time.time()
    
    duration_ms = (end - start) * 1000
    total_size = len(json.dumps(patches))
    
    print(f"\n✓ Generated {len(patches)} patches")
    print(f"✓ Total size: {total_size:,} bytes")
    print(f"✓ Generation time: {duration_ms:.2f}ms")
    print(f"✓ Speed: {total_size / duration_ms:.0f} bytes/ms")

def demo_json_structure():
    """Demo: Show JSON Patch structure."""
    print_section("7. JSON Patch Structure")
    
    variables = {
        "name": "Structure Demo",
        "tagline": "Developer",
        "sections": ["about"]
    }
    
    patches = generate_from_template("portfolio", variables)
    
    print("Patch operations:")
    for i, patch in enumerate(patches):
        print(f"\n  Patch {i+1}:")
        print(f"    Operation: {patch['op']}")
        print(f"    Path: {patch['path']}")
        if patch['op'] == 'add':
            component = patch['value']
            if isinstance(component, dict) and 'type' in component:
                print(f"    Component: {component['type']} (id: {component['id']})")
                print(f"    Has {len(component.get('slots', {}).get('default', []))} children")

def main():
    """Run all demos."""
    print("\n" + "█"*60)
    print("  TEMPLATE SYSTEM DEMONSTRATION")
    print("█"*60)
    
    try:
        demo_list_templates()
        demo_template_info()
        demo_simple_generation()
        demo_custom_sections()
        demo_all_palettes()
        demo_performance()
        demo_json_structure()
        
        print("\n" + "="*60)
        print("  ✓ All demos completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
