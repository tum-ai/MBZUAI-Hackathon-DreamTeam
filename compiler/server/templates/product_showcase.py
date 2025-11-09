"""
Product Showcase Template
iPhone-style product website with multiple pages.
"""

from typing import Dict, List, Any
from .base import TemplateBase

class ProductShowcaseTemplate(TemplateBase):
    """
    Generates a product showcase website with:
    - Home: Hero with product image and CTA
    - Features: Key features showcase
    - Specs: Technical specifications
    - Gallery: Product photos
    """
    
    def __init__(self, variables: Dict[str, Any]):
        """
        Initialize product showcase template.
        
        Required variables:
            - productName: str (product name)
            - tagline: str (product tagline)
            
        Optional variables:
            - palette: str (color palette)
            - fonts: str (font combination)
            - heroImage: str (main product image URL)
            - features: list[dict] (feature data with title, description, icon)
            - specs: list[dict] (spec data with label, value)
            - galleryImages: list[str] (gallery image URLs)
            - ctaText: str (call-to-action button text)
            - ctaLink: str (call-to-action link)
        """
        super().__init__(variables)
        
        # Required
        self.product_name = variables.get("productName", "Product")
        self.tagline = variables.get("tagline", "The future is here")
        
        # Optional
        self.hero_image = variables.get("heroImage", "https://picsum.photos/1200/800?random=1")
        self.features = variables.get("features", self._default_features())
        self.specs = variables.get("specs", self._default_specs())
        self.gallery_images = variables.get("galleryImages", [f"https://picsum.photos/800/600?random={i}" for i in range(2, 7)])
        self.cta_text = variables.get("ctaText", "Buy Now")
        self.cta_link = variables.get("ctaLink", "#")
    
    def _default_features(self):
        return [
            {"title": "Powerful Performance", "description": "Industry-leading specs"},
            {"title": "Stunning Design", "description": "Crafted to perfection"},
            {"title": "All-Day Battery", "description": "Power that lasts"}
        ]
    
    def _default_specs(self):
        return [
            {"label": "Display", "value": "6.1-inch OLED"},
            {"label": "Processor", "value": "Next-gen chip"},
            {"label": "Camera", "value": "48MP Pro system"},
            {"label": "Battery", "value": "Up to 20 hours"}
        ]
    
    def generate_multi_page(self) -> Dict[str, Any]:
        """Generate complete multi-page product showcase."""
        # Define pages
        pages_config = [
            {"name": "Home", "path": "/", "file": "home.json"},
            {"name": "Features", "path": "/features", "file": "features.json"},
            {"name": "Specs", "path": "/specs", "file": "specs.json"},
            {"name": "Gallery", "path": "/gallery", "file": "gallery.json"}
        ]
        
        # Create navbar (will be added to all pages)
        navbar = self.create_navbar(
            pages=[{"name": p["name"], "path": p["path"]} for p in pages_config],
            logo_text=self.product_name,
            style_variant="sticky"
        )
        
        # Project patches (global styles + page definitions)
        project_patches = [
            self.create_global_styles_patch()
        ]
        
        # Add page definitions
        for page_config in pages_config:
            project_patches.append(
                self.create_page_patch(
                    page_name=page_config["name"],
                    page_path=page_config["path"],
                    ast_filename=page_config["file"]
                )
            )
        
        # Generate page ASTs
        pages = {
            "home.json": self._create_home_page(navbar),
            "features.json": self._create_features_page(navbar),
            "specs.json": self._create_specs_page(navbar),
            "gallery.json": self._create_gallery_page(navbar)
        }
        
        return {
            "projectPatches": project_patches,
            "pages": pages
        }
    
    def _create_home_page(self, navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Create home page with hero."""
        hero = self.create_box(
            id="hero",
            style={
                "height": "100vh",
                "width": "100%",
                "position": "relative",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "overflow": "hidden"
            },
            children=[
                # Background image
                self.create_image(
                    id="hero-bg",
                    src=self.hero_image,
                    alt=self.product_name,
                    style={
                        "position": "absolute",
                        "top": "0",
                        "left": "0",
                        "width": "100%",
                        "height": "100%",
                        "objectFit": "cover",
                        "zIndex": "1"
                    }
                ),
                # Gradient overlay
                self.create_box(
                    id="hero-gradient",
                    style={
                        "position": "absolute",
                        "bottom": "0",
                        "left": "0",
                        "width": "100%",
                        "height": "50%",
                        "background": f"linear-gradient(to top, {self.get_color('background')} 20%, transparent)",
                        "zIndex": "2"
                    },
                    children=[]
                ),
                # Content
                self.create_box(
                    id="hero-content",
                    style={
                        "position": "relative",
                        "zIndex": "3",
                        "textAlign": "center",
                        "color": "#ffffff"
                    },
                    children=[
                        self.create_gradient_text(
                            id="hero-product-name",
                            content=self.product_name,
                            variant="sunset" if self.variables.get("palette") != "dark" else "ocean",
                            as_tag="h1",
                            animated=True
                        ),
                        self.create_text(
                            id="hero-tagline",
                            content=self.tagline,
                            as_tag="h2",
                            style={
                                "fontSize": "2rem",
                                "color": "#ffffff",
                                "marginTop": "1rem",
                                "marginBottom": "2rem",
                                "textShadow": "0 2px 8px rgba(0,0,0,0.7)"
                            }
                        ),
                        self.create_button(
                            id="cta-button",
                            text=self.cta_text,
                            style={
                                "padding": "1rem 3rem",
                                "fontSize": "1.2rem",
                                "backgroundColor": self.get_color("primary"),
                                "color": self.get_color("background"),
                                "border": "none",
                                "borderRadius": "50px",
                                "cursor": "pointer",
                                "fontWeight": "600",
                                "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.3)"
                            }
                        )
                    ]
                )
            ],
            as_tag="section"
        )
        
        return self.create_page_with_navbar(navbar, [hero])
    
    def _create_features_page(self, navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Create features page."""
        feature_cards = []
        
        for idx, feature in enumerate(self.features):
            feature_cards.append(
                self.create_card(
                    id=f"feature-{idx}",
                    children=[
                        self.create_text(
                            id=f"feature-{idx}-title",
                            content=feature["title"],
                            as_tag="h3",
                            style={
                                "fontSize": "1.8rem",
                                "color": self.get_color("primary"),
                                "marginBottom": "1rem"
                            }
                        ),
                        self.create_text(
                            id=f"feature-{idx}-description",
                            content=feature["description"],
                            as_tag="p",
                            style={
                                "fontSize": "1.1rem",
                                "color": self.get_color("text"),
                                "lineHeight": "1.6"
                            }
                        )
                    ],
                    variant="elevated"
                )
            )
        
        content = self.create_box(
            id="features-section",
            style={
                "maxWidth": "1200px",
                "margin": "4rem auto",
                "padding": "2rem"
            },
            children=[
                self.create_text(
                    id="features-title",
                    content="Features",
                    as_tag="h1",
                    style={
                        "fontSize": "3rem",
                        "textAlign": "center",
                        "marginBottom": "3rem",
                        "color": self.get_color("primary")
                    }
                ),
                self.create_box(
                    id="features-grid",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                        "gap": "2rem"
                    },
                    children=feature_cards
                )
            ],
            as_tag="section"
        )
        
        return self.create_page_with_navbar(navbar, [content])
    
    def _create_specs_page(self, navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Create specs page."""
        spec_rows = []
        
        for idx, spec in enumerate(self.specs):
            spec_rows.append(
                self.create_box(
                    id=f"spec-row-{idx}",
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "padding": "1.5rem",
                        "borderBottom": f"1px solid {self.get_color('border')}"
                    },
                    children=[
                        self.create_text(
                            id=f"spec-{idx}-label",
                            content=spec["label"],
                            as_tag="dt",
                            style={
                                "fontSize": "1.1rem",
                                "fontWeight": "600",
                                "color": self.get_color("text")
                            }
                        ),
                        self.create_text(
                            id=f"spec-{idx}-value",
                            content=spec["value"],
                            as_tag="dd",
                            style={
                                "fontSize": "1.1rem",
                                "color": self.get_color("textLight")
                            }
                        )
                    ]
                )
            )
        
        content = self.create_box(
            id="specs-section",
            style={
                "maxWidth": "800px",
                "margin": "4rem auto",
                "padding": "2rem"
            },
            children=[
                self.create_text(
                    id="specs-title",
                    content="Technical Specifications",
                    as_tag="h1",
                    style={
                        "fontSize": "3rem",
                        "textAlign": "center",
                        "marginBottom": "3rem",
                        "color": self.get_color("primary")
                    }
                ),
                self.create_card(
                    id="specs-table",
                    children=spec_rows,
                    variant="outlined"
                )
            ],
            as_tag="section"
        )
        
        return self.create_page_with_navbar(navbar, [content])
    
    def _create_gallery_page(self, navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Create gallery page."""
        gallery_items = []
        
        for idx, img_url in enumerate(self.gallery_images):
            gallery_items.append(
                self.create_image(
                    id=f"gallery-img-{idx}",
                    src=img_url,
                    alt=f"{self.product_name} photo {idx+1}",
                    style={
                        "width": "100%",
                        "height": "300px",
                        "objectFit": "cover",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "transition": "transform 0.3s ease"
                    }
                )
            )
        
        content = self.create_box(
            id="gallery-section",
            style={
                "maxWidth": "1200px",
                "margin": "4rem auto",
                "padding": "2rem"
            },
            children=[
                self.create_text(
                    id="gallery-title",
                    content="Gallery",
                    as_tag="h1",
                    style={
                        "fontSize": "3rem",
                        "textAlign": "center",
                        "marginBottom": "3rem",
                        "color": self.get_color("primary")
                    }
                ),
                self.create_box(
                    id="gallery-grid",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))",
                        "gap": "2rem"
                    },
                    children=gallery_items
                )
            ],
            as_tag="section"
        )
        
        return self.create_page_with_navbar(navbar, [content])
