"""
Base Template Class
Provides foundation for all template generators.
"""

from typing import Dict, List, Any, Optional
from .variables import get_palette, get_fonts, generate_global_styles, SPACING, BORDER_RADIUS, SHADOWS

class TemplateBase:
    """
    Base class for all templates.
    Provides common utilities for generating JSON Patch operations.
    """
    
    def __init__(self, variables: Dict[str, Any]):
        """
        Initialize template with variables.
        
        Args:
            variables: Dictionary of template variables (colors, fonts, content, etc.)
        """
        self.variables = variables
        self.palette = get_palette(variables.get("palette", "professional"))
        self.fonts = get_fonts(variables.get("fonts", "modern"))
        self.spacing = SPACING[variables.get("spacing", "normal")]
        self.border_radius = variables.get("borderRadius", "rounded")
        self.shadow = variables.get("shadow", "soft")
        
    def generate_patches(self) -> List[Dict[str, Any]]:
        """
        Generate JSON Patch operations for this template.
        Must be implemented by subclasses.
        
        Returns:
            List of JSON Patch operations (for single-page templates)
        """
        raise NotImplementedError("Subclasses must implement generate_patches()")
    
    def generate_multi_page(self) -> Dict[str, Any]:
        """
        Generate multi-page template structure.
        Must be implemented by subclasses that support multi-page.
        
        Returns:
            Dictionary with structure:
            {
                "projectPatches": [...],  # Patches for project.json (global styles, pages list)
                "pages": {
                    "home.json": {...},    # Complete AST for each page
                    "about.json": {...},
                    ...
                }
            }
        """
        raise NotImplementedError("Subclasses must implement generate_multi_page()")
    
    def create_global_styles_patch(self) -> Dict[str, Any]:
        """
        Create a patch operation for global styles.
        
        Returns:
            JSON Patch operation for /globalStyles
        """
        return {
            "op": "replace",
            "path": "/globalStyles",
            "value": generate_global_styles(
                self.variables.get("palette", "professional"),
                self.variables.get("fonts", "modern")
            )
        }
    
    def create_component(
        self,
        id: str,
        comp_type: str,
        props: Dict[str, Any],
        slots: Optional[Dict[str, List[Any]]] = None,
        events: Optional[Dict[str, List[Any]]] = None,
        v_if: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a component definition for the AST.
        
        Args:
            id: Semantic ID for the component
            comp_type: Component type (Box, Text, Button, etc.)
            props: Component props
            slots: Component slots (default: empty default slot)
            events: Component events
            v_if: Conditional rendering
            
        Returns:
            Component definition dict
        """
        component = {
            "id": id,
            "type": comp_type,
            "props": props,
            "slots": slots or {"default": []}
        }
        
        if events:
            component["events"] = events
        
        if v_if:
            component["v-if"] = v_if
            
        return component
    
    def create_box(
        self,
        id: str,
        style: Dict[str, Any],
        children: Optional[List[Any]] = None,
        as_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Box component (common layout container).
        
        Args:
            id: Semantic ID
            style: Inline styles
            children: Child components
            as_tag: HTML tag override (e.g., 'section', 'footer')
            
        Returns:
            Box component definition
        """
        props = {"style": style}
        if as_tag:
            props["as"] = as_tag
            
        return self.create_component(
            id=id,
            comp_type="Box",
            props=props,
            slots={"default": children or []}
        )
    
    def create_text(
        self,
        id: str,
        content: str,
        as_tag: str = "p",
        style: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Text component.
        
        Args:
            id: Semantic ID
            content: Text content
            as_tag: HTML tag (h1, h2, p, span, etc.)
            style: Inline styles
            
        Returns:
            Text component definition
        """
        props = {
            "content": content,
            "as": as_tag
        }
        if style:
            props["style"] = style
            
        return self.create_component(
            id=id,
            comp_type="Text",
            props=props
        )
    
    def create_gradient_text(
        self,
        id: str,
        content: str,
        variant: str = "sunset",
        as_tag: str = "h1",
        animated: bool = True
    ) -> Dict[str, Any]:
        """
        Create a GradientText component (V20 enhanced).
        
        Args:
            id: Semantic ID
            content: Text content
            variant: Gradient variant (sunset, ocean, neon, purple-haze)
            as_tag: HTML tag
            animated: Whether to animate the gradient
            
        Returns:
            GradientText component definition
        """
        return self.create_component(
            id=id,
            comp_type="GradientText",
            props={
                "content": content,
                "as": as_tag,
                "variant": variant,
                "animated": animated
            }
        )
    
    def create_card(
        self,
        id: str,
        children: List[Any],
        variant: str = "elevated",
        style: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Card component (V20 enhanced).
        
        Args:
            id: Semantic ID
            children: Child components
            variant: Card variant (default, elevated, outlined, flat)
            style: Additional inline styles
            
        Returns:
            Card component definition
        """
        props = {"variant": variant}
        if style:
            props["style"] = style
            
        return self.create_component(
            id=id,
            comp_type="Card",
            props=props,
            slots={"default": children}
        )
    
    def create_button(
        self,
        id: str,
        text: str,
        style: Optional[Dict[str, Any]] = None,
        events: Optional[Dict[str, List[Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a Button component.
        
        Args:
            id: Semantic ID
            text: Button text
            style: Inline styles
            events: Event handlers
            
        Returns:
            Button component definition
        """
        props = {"text": text}
        if style:
            props["style"] = style
            
        return self.create_component(
            id=id,
            comp_type="Button",
            props=props,
            events=events
        )
    
    def create_image(
        self,
        id: str,
        src: str,
        alt: str,
        style: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an Image component.
        
        Args:
            id: Semantic ID
            src: Image source URL
            alt: Alt text
            style: Inline styles
            
        Returns:
            Image component definition
        """
        props = {
            "src": src,
            "alt": alt
        }
        if style:
            props["style"] = style
            
        return self.create_component(
            id=id,
            comp_type="Image",
            props=props
        )
    
    def create_link(
        self,
        id: str,
        href: str,
        text: str,
        style: Optional[Dict[str, Any]] = None,
        target: str = "_self"
    ) -> Dict[str, Any]:
        """
        Create a Link component.
        
        Args:
            id: Semantic ID
            href: Link destination
            text: Link text
            style: Inline styles
            target: Link target (_self, _blank, etc.)
            
        Returns:
            Link component definition
        """
        props = {
            "href": href,
            "target": target
        }
        if style:
            props["style"] = style
            
        return self.create_component(
            id=id,
            comp_type="Link",
            props=props,
            slots={"default": [self.create_text(f"{id}-text", text, "span")]}
        )
    
    def get_color(self, color_key: str) -> str:
        """Get color from current palette."""
        return self.palette.get(color_key, "#000000")
    
    def get_spacing(self, spacing_key: str) -> str:
        """Get spacing value from current spacing scale."""
        return self.spacing.get(spacing_key, "1rem")
    
    # ===== MULTI-PAGE UTILITIES =====
    
    def create_page_patch(self, page_name: str, page_path: str, ast_filename: str) -> Dict[str, Any]:
        """
        Create a patch to add a new page to PROJECT_CONFIG.
        
        Args:
            page_name: Display name of the page (e.g., "About")
            page_path: URL path (e.g., "/about")
            ast_filename: Filename for the page's AST (e.g., "about.json")
            
        Returns:
            JSON Patch operation to add page to /pages array
        """
        return {
            "op": "add",
            "path": "/pages/-",
            "value": {
                "name": page_name,
                "path": page_path,
                "astFile": ast_filename
            }
        }
    
    def create_empty_page_ast(self) -> Dict[str, Any]:
        """
        Create an empty page AST structure.
        
        Returns:
            Empty AST with root Box
        """
        return {
            "state": {},
            "tree": {
                "id": "root",
                "type": "Box",
                "props": {"style": {}},
                "slots": {"default": []}
            }
        }
    
    def create_navbar(
        self,
        pages: List[Dict[str, str]],
        logo_text: Optional[str] = None,
        style_variant: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a navigation bar component.
        
        Args:
            pages: List of page dicts with 'name' and 'path' keys
            logo_text: Optional logo/brand text
            style_variant: Style variant (default, transparent, sticky)
            
        Returns:
            Navbar Box component
        """
        # Nav items (links)
        nav_items = []
        for page in pages:
            nav_items.append(
                self.create_link(
                    id=f"nav-{page['name'].lower()}",
                    href=f"#/{page['path'].lstrip('/')}",
                    text=page['name'],
                    style={
                        "padding": "0.5rem 1rem",
                        "color": self.get_color("text"),
                        "textDecoration": "none",
                        "fontSize": "1rem",
                        "fontWeight": "600",
                        "transition": "color 0.2s ease"
                    }
                )
            )
        
        # Nav links container
        nav_links = self.create_box(
            id="nav-links",
            style={
                "display": "flex",
                "gap": "0.5rem",
                "alignItems": "center"
            },
            children=nav_items
        )
        
        # Logo
        logo = None
        if logo_text:
            logo = self.create_text(
                id="nav-logo",
                content=logo_text,
                as_tag="span",
                style={
                    "fontSize": "1.5rem",
                    "fontWeight": "700",
                    "color": self.get_color("primary")
                }
            )
        
        # Navbar container
        navbar_style = {
            "width": "100%",
            "display": "flex",
            "justifyContent": "space-between" if logo else "flex-end",
            "alignItems": "center",
            "padding": "1rem 2rem",
            "backgroundColor": self.get_color("background"),
            "borderBottom": f"1px solid {self.get_color('border')}",
            "position": "sticky" if style_variant == "sticky" else "relative",
            "top": "0",
            "zIndex": "1000"
        }
        
        if style_variant == "transparent":
            navbar_style["backgroundColor"] = "transparent"
            navbar_style["borderBottom"] = "none"
        
        navbar_children = [nav_links]
        if logo:
            navbar_children.insert(0, logo)
        
        return self.create_box(
            id="navbar",
            style=navbar_style,
            children=navbar_children,
            as_tag="nav"
        )
    
    def create_page_with_navbar(
        self,
        navbar: Dict[str, Any],
        content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a complete page structure with navbar and content.
        
        Args:
            navbar: Navbar component
            content: List of content components
            
        Returns:
            Complete page AST structure
        """
        return {
            "state": {},
            "tree": {
                "id": "root",
                "type": "Box",
                "props": {"style": {}},
                "slots": {
                    "default": [navbar] + content
                }
            }
        }
