"""
Gallery Template
Photography/art showcase website with multiple pages.
"""

from typing import Dict, List, Any
from .base import TemplateBase

class GalleryTemplate(TemplateBase):
    """
    Generates a gallery website with:
    - Home: Hero with featured image
    - Gallery: Photo grid
    - About: Artist bio
    """
    
    def __init__(self, variables: Dict[str, Any]):
        """
        Initialize gallery template.
        
        Required variables:
            - name: str (artist/photographer name)
            - tagline: str (artist description)
            
        Optional variables:
            - palette, fonts, heroImage
            - galleryImages: list[str] (image URLs)
            - about: str (bio text)
            - categories: list[str] (image categories)
        """
        super().__init__(variables)
        
        self.name = variables.get("name", "Artist Name")
        self.tagline = variables.get("tagline", "Visual Storyteller")
        self.hero_image = variables.get("heroImage", "https://picsum.photos/1920/1080?random=1")
        self.gallery_images = variables.get("galleryImages", [f"https://picsum.photos/800/600?random={i}" for i in range(2, 13)])
        self.about = variables.get("about", "Capturing moments and telling stories through the lens.")
    
    def generate_multi_page(self) -> Dict[str, Any]:
        """Generate complete multi-page gallery."""
        pages_config = [
            {"name": "Home", "path": "/", "file": "home.json"},
            {"name": "Gallery", "path": "/gallery", "file": "gallery.json"},
            {"name": "About", "path": "/about", "file": "about.json"}
        ]
        
        navbar = self.create_navbar(
            pages=[{"name": p["name"], "path": p["path"]} for p in pages_config],
            logo_text=self.name,
            style_variant="transparent"
        )
        
        project_patches = [self.create_global_styles_patch()]
        for page_config in pages_config:
            project_patches.append(self.create_page_patch(page_config["name"], page_config["path"], page_config["file"]))
        
        return {
            "projectPatches": project_patches,
            "pages": {
                "home.json": self._create_home_page(navbar),
                "gallery.json": self._create_gallery_page(navbar),
                "about.json": self._create_about_page(navbar)
            }
        }
    
    def _create_home_page(self, navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Create home page with hero image."""
        hero = self.create_box(
            id="hero",
            style={
                "height": "100vh",
                "width": "100%",
                "position": "relative",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center"
            },
            children=[
                self.create_image(
                    id="hero-bg",
                    src=self.hero_image,
                    alt="Hero image",
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
                self.create_box(
                    id="hero-overlay",
                    style={
                        "position": "absolute",
                        "top": "0",
                        "left": "0",
                        "width": "100%",
                        "height": "100%",
                        "background": "linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 50%)",
                        "zIndex": "2"
                    },
                    children=[]
                ),
                self.create_box(
                    id="hero-content",
                    style={
                        "position": "relative",
                        "zIndex": "3",
                        "textAlign": "center",
                        "color": "#ffffff"
                    },
                    children=[
                        self.create_text(
                            id="hero-name",
                            content=self.name,
                            as_tag="h1",
                            style={"fontSize": "4rem", "fontWeight": "700", "textShadow": "0 2px 4px rgba(0,0,0,0.3)"}
                        ),
                        self.create_text(
                            id="hero-tagline",
                            content=self.tagline,
                            as_tag="h2",
                            style={"fontSize": "1.5rem", "marginTop": "1rem", "textShadow": "0 2px 4px rgba(0,0,0,0.3)"}
                        )
                    ]
                )
            ],
            as_tag="section"
        )
        
        return self.create_page_with_navbar(navbar, [hero])
    
    def _create_gallery_page(self, navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Create gallery grid page."""
        gallery_items = []
        for idx, img_url in enumerate(self.gallery_images):
            gallery_items.append(
                self.create_image(
                    id=f"gallery-img-{idx}",
                    src=img_url,
                    alt=f"Gallery image {idx+1}",
                    style={
                        "width": "100%",
                        "height": "350px",
                        "objectFit": "cover",
                        "borderRadius": "4px",
                        "cursor": "pointer",
                        "transition": "transform 0.3s ease"
                    }
                )
            )
        
        content = self.create_box(
            id="gallery-section",
            style={"maxWidth": "1400px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(
                    id="gallery-title",
                    content="Gallery",
                    as_tag="h1",
                    style={"fontSize": "3rem", "textAlign": "center", "marginBottom": "3rem", "color": self.get_color("primary")}
                ),
                self.create_box(
                    id="gallery-grid",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fill, minmax(350px, 1fr))",
                        "gap": "1.5rem"
                    },
                    children=gallery_items
                )
            ],
            as_tag="section"
        )
        
        return self.create_page_with_navbar(navbar, [content])
    
    def _create_about_page(self, navbar: Dict[str, Any]) -> Dict[str, Any]:
        """Create about page."""
        content = self.create_box(
            id="about-section",
            style={"maxWidth": "800px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(
                    id="about-title",
                    content="About",
                    as_tag="h1",
                    style={"fontSize": "3rem", "marginBottom": "2rem", "color": self.get_color("primary")}
                ),
                self.create_text(
                    id="about-content",
                    content=self.about,
                    as_tag="p",
                    style={"fontSize": "1.2rem", "lineHeight": "1.8", "color": self.get_color("text")}
                )
            ],
            as_tag="section"
        )
        
        return self.create_page_with_navbar(navbar, [content])
