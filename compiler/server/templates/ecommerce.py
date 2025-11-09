"""
E-commerce Template
Simple shopping website with multiple pages.
"""

from typing import Dict, List, Any
from .base import TemplateBase

class EcommerceTemplate(TemplateBase):
    """Generates e-commerce site with: Home, Products, About, Contact"""
    
    def __init__(self, variables: Dict[str, Any]):
        super().__init__(variables)
        self.store_name = variables.get("storeName", "My Store")
        self.tagline = variables.get("tagline", "Quality products for you")
        self.products = variables.get("products", self._default_products())
        self.about = variables.get("about", "We provide quality products.")
    
    def _default_products(self):
        return [
            {"name": "Product 1", "price": "$99", "image": f"https://picsum.photos/400/400?random={i}"}
            for i in range(10, 16)
        ]
    
    def generate_multi_page(self) -> Dict[str, Any]:
        pages_config = [
            {"name": "Home", "path": "/", "file": "home.json"},
            {"name": "Products", "path": "/products", "file": "products.json"},
            {"name": "About", "path": "/about", "file": "about.json"},
            {"name": "Contact", "path": "/contact", "file": "contact.json"}
        ]
        
        navbar = self.create_navbar(
            [{"name": p["name"], "path": p["path"]} for p in pages_config],
            logo_text=self.store_name
        )
        
        project_patches = [self.create_global_styles_patch()]
        for p in pages_config:
            project_patches.append(self.create_page_patch(p["name"], p["path"], p["file"]))
        
        return {
            "projectPatches": project_patches,
            "pages": {
                "home.json": self._create_home(navbar),
                "products.json": self._create_products(navbar),
                "about.json": self._create_about(navbar),
                "contact.json": self._create_contact(navbar)
            }
        }
    
    def _create_home(self, navbar):
        # Use first product image or default
        hero_image = self.products[0]["image"] if self.products else "https://picsum.photos/1920/1080?random=200"
        
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
                    src=hero_image,
                    alt="Hero background",
                    style={
                        "position": "absolute",
                        "top": "0",
                        "left": "0",
                        "width": "100%",
                        "height": "100%",
                        "objectFit": "cover",
                        "zIndex": "1",
                        "filter": "brightness(0.6)"
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
                        "background": f"linear-gradient(to top, {self.get_color('background')} 10%, transparent)",
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
                        "textAlign": "center"
                    },
                    children=[
                        self.create_gradient_text(
                            id="hero-title",
                            content=self.store_name,
                            as_tag="h1",
                            animated=True
                        ),
                        self.create_text(
                            id="hero-tagline",
                            content=self.tagline,
                            as_tag="h2",
                            style={
                                "fontSize": "2rem",
                                "marginTop": "1rem",
                                "color": "#ffffff",
                                "textShadow": "0 2px 8px rgba(0,0,0,0.7)"
                            }
                        ),
                        self.create_button(
                            id="cta",
                            text="Shop Now",
                            style={
                                "marginTop": "2rem",
                                "padding": "1rem 2rem",
                                "fontSize": "1.1rem",
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
            ]
        )
        return self.create_page_with_navbar(navbar, [hero])
    
    def _create_products(self, navbar):
        product_cards = []
        for idx, product in enumerate(self.products):
            product_cards.append(
                self.create_card(
                    id=f"product-{idx}",
                    children=[
                        self.create_image(id=f"product-{idx}-img", src=product["image"], alt=product["name"], style={"width": "100%", "height": "250px", "objectFit": "cover", "borderRadius": "8px 8px 0 0"}),
                        self.create_text(id=f"product-{idx}-name", content=product["name"], as_tag="h3", style={"fontSize": "1.3rem", "marginTop": "1rem"}),
                        self.create_text(id=f"product-{idx}-price", content=product["price"], as_tag="p", style={"fontSize": "1.5rem", "fontWeight": "700", "color": self.get_color("primary"), "marginTop": "0.5rem"})
                    ],
                    variant="elevated",
                    style={"padding": "0", "overflow": "hidden"}
                )
            )
        
        content = self.create_box(
            id="products-section",
            style={"maxWidth": "1200px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(id="products-title", content="Our Products", as_tag="h1", style={"fontSize": "3rem", "textAlign": "center", "marginBottom": "3rem"}),
                self.create_box(id="products-grid", style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "2rem"}, children=product_cards)
            ]
        )
        return self.create_page_with_navbar(navbar, [content])
    
    def _create_about(self, navbar):
        content = self.create_box(
            id="about-section",
            style={"maxWidth": "800px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(id="about-title", content="About Us", as_tag="h1", style={"fontSize": "3rem", "marginBottom": "2rem"}),
                self.create_text(id="about-content", content=self.about, as_tag="p", style={"fontSize": "1.2rem", "lineHeight": "1.8"})
            ]
        )
        return self.create_page_with_navbar(navbar, [content])
    
    def _create_contact(self, navbar):
        content = self.create_box(
            id="contact-section",
            style={"maxWidth": "600px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(id="contact-title", content="Contact Us", as_tag="h1", style={"fontSize": "3rem", "textAlign": "center", "marginBottom": "2rem"}),
                self.create_text(id="contact-desc", content="Get in touch with us", as_tag="p", style={"fontSize": "1.1rem", "textAlign": "center", "color": self.get_color("textLight")})
            ]
        )
        return self.create_page_with_navbar(navbar, [content])
