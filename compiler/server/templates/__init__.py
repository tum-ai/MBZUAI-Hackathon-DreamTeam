"""
Template Generator Module
Main API for generating JSON Patch operations from templates.
"""

import json
from typing import Dict, List, Any, Optional
from .portfolio import PortfolioTemplate
from .product_showcase import ProductShowcaseTemplate
from .gallery import GalleryTemplate
from .ecommerce import EcommerceTemplate
from .blog import BlogTemplate

# Template registry
TEMPLATES = {
    "portfolio": PortfolioTemplate,
    "product": ProductShowcaseTemplate,
    "gallery": GalleryTemplate,
    "ecommerce": EcommerceTemplate,
    "blog": BlogTemplate
}

def generate_from_template(
    template_name: str,
    variables: Dict[str, Any],
    multi_page: bool = True
) -> Dict[str, Any]:
    """
    Generate template structure from variables.
    
    Args:
        template_name: Name of the template (e.g., "portfolio")
        variables: Dictionary of template variables
        multi_page: If True, returns multi-page structure; if False, returns single-page patches
        
    Returns:
        If multi_page=True:
            {
                "projectPatches": [...],  # Patches for project.json
                "pages": {
                    "home.json": {...},    # Complete AST for each page
                    "about.json": {...}
                }
            }
        If multi_page=False:
            List of JSON Patch operations (legacy format)
        
    Raises:
        ValueError: If template name is not found
        
    Example:
        >>> result = generate_from_template("portfolio", {
        ...     "name": "John Doe",
        ...     "tagline": "Full Stack Developer",
        ...     "palette": "professional"
        ... })
        >>> print(result.keys())  # ['projectPatches', 'pages']
    """
    if template_name not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Template '{template_name}' not found. Available templates: {available}")
    
    template_class = TEMPLATES[template_name]
    template = template_class(variables)
    
    if multi_page:
        # Check if template supports multi-page
        if hasattr(template, 'generate_multi_page'):
            return template.generate_multi_page()
        else:
            # Fallback: wrap single-page in multi-page structure
            patches = template.generate_patches()
            return {
                "projectPatches": [p for p in patches if '/globalStyles' in p.get('path', '')],
                "pages": {
                    "home.json": {
                        "state": {},
                        "tree": patches[-1]["value"] if patches else {"id": "root", "type": "Box", "props": {}, "slots": {"default": []}}
                    }
                }
            }
    else:
        # Legacy single-page format
        return template.generate_patches()

def get_available_templates() -> List[str]:
    """
    Get list of available template names.
    
    Returns:
        List of template names
    """
    return list(TEMPLATES.keys())

def get_template_info(template_name: str) -> Dict[str, Any]:
    """
    Get information about a template including required/optional variables.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Dictionary with template information
        
    Raises:
        ValueError: If template name is not found
    """
    if template_name not in TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found")
    
    template_class = TEMPLATES[template_name]
    
    # Extract docstring information
    docstring = template_class.__doc__ or "No description available"
    
    # For portfolio template, provide structured info
    if template_name == "portfolio":
        return {
            "name": template_name,
            "description": "Personal portfolio website with customizable sections",
            "required_variables": {
                "name": "Person's name (string)",
                "tagline": "Professional tagline/role (string)"
            },
            "optional_variables": {
                "palette": "Color scheme: professional, personal, quirky, fun, energetic, dark, minimal (default: professional)",
                "fonts": "Font combination: modern, elegant, tech, playful, classic, serif (default: modern)",
                "spacing": "Spacing scale: compact, normal, spacious (default: normal)",
                "image": "URL to profile/hero image (default: placeholder)",
                "about": "About me text (default: placeholder)",
                "sections": "List of sections to include: about, projects, education, experience, skills, gallery, blog, contact (default: [about, projects, contact])",
                "projects": "List of project objects with title, description, image",
                "education": "List of education objects with degree, school, year, description",
                "experience": "List of experience objects with title, company, period, description",
                "skills": "List of skill names",
                "socialLinks": "Dictionary of social media links (github, linkedin, twitter, email, etc.)",
                "heroLayout": "Hero section layout: centered, split, minimal (default: split)"
            },
            "example": {
                "name": "Jane Doe",
                "tagline": "UX Designer & Developer",
                "palette": "professional",
                "fonts": "elegant",
                "sections": ["about", "projects", "skills", "contact"],
                "about": "I create beautiful, user-centered digital experiences.",
                "projects": [
                    {
                        "title": "E-commerce Redesign",
                        "description": "Complete overhaul of shopping experience",
                        "image": "https://picsum.photos/400/300"
                    }
                ],
                "skills": ["UI/UX Design", "Figma", "React", "CSS"],
                "socialLinks": {
                    "github": "https://github.com/janedoe",
                    "linkedin": "https://linkedin.com/in/janedoe"
                }
            }
        }
    
    return {
        "name": template_name,
        "description": docstring.strip(),
        "required_variables": {},
        "optional_variables": {},
        "example": {}
    }

def save_patches_to_file(patches: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save JSON Patch operations to a file.
    
    Args:
        patches: List of JSON Patch operations
        filepath: Path to save the file
    """
    with open(filepath, 'w') as f:
        json.dump(patches, f, indent=2)

def save_multi_page_output(result: Dict[str, Any], output_dir: str) -> None:
    """
    Save multi-page template output to directory.
    
    Args:
        result: Multi-page result dict with 'projectPatches' and 'pages'
        output_dir: Directory to save files
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Save project patches
    with open(os.path.join(output_dir, 'project_patches.json'), 'w') as f:
        json.dump(result['projectPatches'], f, indent=2)
    
    # Save each page AST
    for page_name, page_ast in result['pages'].items():
        with open(os.path.join(output_dir, page_name), 'w') as f:
            json.dump(page_ast, f, indent=2)

def generate_and_save(
    template_name: str,
    variables: Dict[str, Any],
    output_path: str
) -> List[Dict[str, Any]]:
    """
    Generate patches from template and save to file.
    
    Args:
        template_name: Name of the template
        variables: Template variables
        output_path: Path to save the JSON patch file
        
    Returns:
        Generated patches
    """
    patches = generate_from_template(template_name, variables)
    save_patches_to_file(patches, output_path)
    return patches

# CLI usage example
if __name__ == "__main__":
    import sys
    
    print("Available templates:")
    for template in get_available_templates():
        print(f"  - {template}")
    
    if len(sys.argv) > 1:
        template_name = sys.argv[1]
        print(f"\nTemplate info for '{template_name}':")
        info = get_template_info(template_name)
        print(json.dumps(info, indent=2))
