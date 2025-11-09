"""
Blog Template
Blog/article website with multiple pages.
"""

from typing import Dict, List, Any
from .base import TemplateBase

class BlogTemplate(TemplateBase):
    """Generates blog site with: Home, Blog, About, Contact"""
    
    def __init__(self, variables: Dict[str, Any]):
        super().__init__(variables)
        self.blog_name = variables.get("blogName", "My Blog")
        self.tagline = variables.get("tagline", "Thoughts and stories")
        self.posts = variables.get("posts", self._default_posts())
        self.about = variables.get("about", "Welcome to my blog where I share my thoughts.")
    
    def _default_posts(self):
        return [
            {"title": "First Post", "date": "Jan 2024", "excerpt": "Welcome to my blog...", "image": f"https://picsum.photos/800/400?random={i}"}
            for i in range(20, 26)
        ]
    
    def generate_multi_page(self) -> Dict[str, Any]:
        pages_config = [
            {"name": "Home", "path": "/", "file": "home.json"},
            {"name": "Blog", "path": "/blog", "file": "blog.json"},
            {"name": "About", "path": "/about", "file": "about.json"},
            {"name": "Contact", "path": "/contact", "file": "contact.json"}
        ]
        
        navbar = self.create_navbar(
            [{"name": p["name"], "path": p["path"]} for p in pages_config],
            logo_text=self.blog_name
        )
        
        project_patches = [self.create_global_styles_patch()]
        for p in pages_config:
            project_patches.append(self.create_page_patch(p["name"], p["path"], p["file"]))
        
        return {
            "projectPatches": project_patches,
            "pages": {
                "home.json": self._create_home(navbar),
                "blog.json": self._create_blog(navbar),
                "about.json": self._create_about(navbar),
                "contact.json": self._create_contact(navbar)
            }
        }
    
    def _create_home(self, navbar):
        # Hero image from first post or default
        hero_image = self.posts[0]["image"] if self.posts else "https://picsum.photos/1920/1080?random=100"
        
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
                        "height": "60%",
                        "background": f"linear-gradient(to top, {self.get_color('background')} 0%, transparent 100%)",
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
                        "color": "#ffffff",
                        "textShadow": "0 2px 8px rgba(0,0,0,0.7)"
                    },
                    children=[
                        self.create_text(
                            id="hero-title",
                            content=self.blog_name,
                            as_tag="h1",
                            style={"fontSize": "5rem", "fontWeight": "700"}
                        ),
                        self.create_text(
                            id="hero-tagline",
                            content=self.tagline,
                            as_tag="h2",
                            style={"fontSize": "2rem", "marginTop": "1rem", "fontWeight": "400"}
                        )
                    ]
                )
            ]
        )
        return self.create_page_with_navbar(navbar, [hero])
    
    def _create_blog(self, navbar):
        post_cards = []
        for idx, post in enumerate(self.posts):
            post_cards.append(
                self.create_card(
                    id=f"post-{idx}",
                    children=[
                        self.create_image(id=f"post-{idx}-img", src=post["image"], alt=post["title"], style={"width": "100%", "height": "200px", "objectFit": "cover", "borderRadius": "8px 8px 0 0"}),
                        self.create_text(id=f"post-{idx}-title", content=post["title"], as_tag="h3", style={"fontSize": "1.5rem", "marginTop": "1rem", "color": self.get_color("primary")}),
                        self.create_text(id=f"post-{idx}-date", content=post["date"], as_tag="p", style={"fontSize": "0.9rem", "color": self.get_color("textLight"), "marginTop": "0.5rem"}),
                        self.create_text(id=f"post-{idx}-excerpt", content=post["excerpt"], as_tag="p", style={"fontSize": "1rem", "marginTop": "0.5rem", "color": self.get_color("text")})
                    ],
                    variant="elevated",
                    style={"padding": "0", "overflow": "hidden"}
                )
            )
        
        content = self.create_box(
            id="blog-section",
            style={"maxWidth": "1200px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(id="blog-title", content="Latest Posts", as_tag="h1", style={"fontSize": "3rem", "textAlign": "center", "marginBottom": "3rem"}),
                self.create_box(id="blog-grid", style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))", "gap": "2rem"}, children=post_cards)
            ]
        )
        return self.create_page_with_navbar(navbar, [content])
    
    def _create_about(self, navbar):
        content = self.create_box(
            id="about-section",
            style={"maxWidth": "800px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(id="about-title", content="About", as_tag="h1", style={"fontSize": "3rem", "marginBottom": "2rem"}),
                self.create_text(id="about-content", content=self.about, as_tag="p", style={"fontSize": "1.2rem", "lineHeight": "1.8"})
            ]
        )
        return self.create_page_with_navbar(navbar, [content])
    
    def _create_contact(self, navbar):
        content = self.create_box(
            id="contact-section",
            style={"maxWidth": "600px", "margin": "4rem auto", "padding": "2rem"},
            children=[
                self.create_text(id="contact-title", content="Contact", as_tag="h1", style={"fontSize": "3rem", "textAlign": "center", "marginBottom": "2rem"}),
                self.create_text(id="contact-desc", content="Reach out to me", as_tag="p", style={"fontSize": "1.1rem", "textAlign": "center", "color": self.get_color("textLight")})
            ]
        )
        return self.create_page_with_navbar(navbar, [content])
