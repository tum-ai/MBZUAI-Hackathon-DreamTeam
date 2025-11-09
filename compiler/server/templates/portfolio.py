"""
Portfolio Template Generator
Creates a complete personal portfolio website with customizable sections.
"""

from typing import Dict, List, Any
from .base import TemplateBase

class PortfolioTemplate(TemplateBase):
    """
    Generates a personal portfolio website with:
    - Hero section with name and tagline
    - About section
    - Optional sections: Projects, Education, Experience, Skills, Gallery, Blog, Contact
    - Footer
    """
    
    def __init__(self, variables: Dict[str, Any]):
        """
        Initialize portfolio template.
        
        Required variables:
            - name: str (person's name)
            - tagline: str (professional tagline/role)
            
        Optional variables:
            - palette: str (professional, personal, quirky, fun, energetic, dark, minimal)
            - fonts: str (modern, elegant, tech, playful, classic, serif)
            - spacing: str (compact, normal, spacious)
            - image: str (URL to profile/hero image)
            - about: str (about me text)
            - sections: list[str] (which sections to include: projects, education, experience, skills, gallery, blog, contact)
            - projects: list[dict] (project data)
            - education: list[dict] (education data)
            - experience: list[dict] (experience data)
            - skills: list[str] (skill names)
            - socialLinks: dict (github, linkedin, twitter, email, etc.)
            - heroLayout: str (centered, split, minimal)
        """
        super().__init__(variables)
        
        # Required
        self.name = variables.get("name", "Your Name")
        self.tagline = variables.get("tagline", "Web Developer & Designer")
        
        # Optional
        self.image = variables.get("image", "https://picsum.photos/600/600?random=1")
        self.about = variables.get("about", "I'm a passionate developer creating beautiful digital experiences.")
        self.sections = variables.get("sections", ["about", "projects", "contact"])
        self.hero_layout = variables.get("heroLayout", "split")
        
        # Data
        self.projects = variables.get("projects", [])
        self.education = variables.get("education", [])
        self.experience = variables.get("experience", [])
        self.skills = variables.get("skills", [])
        self.social_links = variables.get("socialLinks", {})
    
    def generate_patches(self) -> List[Dict[str, Any]]:
        """Generate all JSON Patch operations for portfolio."""
        patches = []
        
        # 1. Global styles
        patches.append(self.create_global_styles_patch())
        
        # 2. Hero section
        patches.append(self._create_hero_section_patch())
        
        # 3. Dynamic sections based on what's requested
        if "about" in self.sections:
            patches.append(self._create_about_section_patch())
        
        if "projects" in self.sections:
            patches.append(self._create_projects_section_patch())
        
        if "experience" in self.sections:
            patches.append(self._create_experience_section_patch())
        
        if "education" in self.sections:
            patches.append(self._create_education_section_patch())
        
        if "skills" in self.sections:
            patches.append(self._create_skills_section_patch())
        
        if "gallery" in self.sections:
            patches.append(self._create_gallery_section_patch())
        
        if "blog" in self.sections:
            patches.append(self._create_blog_section_patch())
        
        if "contact" in self.sections:
            patches.append(self._create_contact_section_patch())
        
        # 4. Footer
        patches.append(self._create_footer_section_patch())
        
        return patches
    
    def _create_hero_section_patch(self) -> Dict[str, Any]:
        """Create hero section based on layout preference."""
        if self.hero_layout == "split":
            return self._create_split_hero()
        elif self.hero_layout == "minimal":
            return self._create_minimal_hero()
        else:
            return self._create_centered_hero()
    
    def _create_centered_hero(self) -> Dict[str, Any]:
        """Create centered hero with name and tagline."""
        hero_children = [
            self.create_gradient_text(
                id="hero-name",
                content=self.name,
                variant="sunset" if self.variables.get("palette") != "dark" else "ocean",
                as_tag="h1",
                animated=True
            ),
            self.create_text(
                id="hero-tagline",
                content=self.tagline,
                as_tag="h2",
                style={
                    "fontSize": "1.8rem",
                    "color": self.get_color("textLight"),
                    "textAlign": "center",
                    "marginTop": "1rem",
                    "fontWeight": "400"
                }
            )
        ]
        
        hero = self.create_box(
            id="hero-section",
            style={
                "height": "100vh",
                "width": "100%",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "center",
                "padding": "0 2rem",
                "background": f"linear-gradient(135deg, {self.get_color('background')} 0%, {self.get_color('cardBg')} 100%)"
            },
            children=hero_children,
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": hero
        }
    
    def _create_split_hero(self) -> Dict[str, Any]:
        """Create split hero with text on left, image on right."""
        text_content = self.create_box(
            id="hero-text-content",
            style={
                "flex": "1",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "padding": "2rem"
            },
            children=[
                self.create_gradient_text(
                    id="hero-name",
                    content=self.name,
                    variant="sunset" if self.variables.get("palette") != "dark" else "ocean",
                    as_tag="h1",
                    animated=True
                ),
                self.create_text(
                    id="hero-tagline",
                    content=self.tagline,
                    as_tag="h2",
                    style={
                        "fontSize": "1.8rem",
                        "color": self.get_color("textLight"),
                        "marginTop": "1rem",
                        "fontWeight": "400"
                    }
                )
            ]
        )
        
        image_container = self.create_box(
            id="hero-image-container",
            style={
                "flex": "1",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "2rem"
            },
            children=[
                self.create_image(
                    id="hero-image",
                    src=self.image,
                    alt=f"Photo of {self.name}",
                    style={
                        "width": "100%",
                        "maxWidth": "500px",
                        "height": "auto",
                        "borderRadius": "12px",
                        "boxShadow": f"0 20px 60px rgba(0, 0, 0, 0.3)"
                    }
                )
            ]
        )
        
        hero = self.create_box(
            id="hero-section",
            style={
                "minHeight": "100vh",
                "width": "100%",
                "display": "flex",
                "alignItems": "center",
                "padding": "2rem",
                "gap": "4rem"
            },
            children=[text_content, image_container],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": hero
        }
    
    def _create_minimal_hero(self) -> Dict[str, Any]:
        """Create minimal hero with just name."""
        hero = self.create_box(
            id="hero-section",
            style={
                "height": "100vh",
                "width": "100%",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "padding": "0 2rem"
            },
            children=[
                self.create_text(
                    id="hero-name",
                    content=self.name,
                    as_tag="h1",
                    style={
                        "fontSize": "6rem",
                        "fontWeight": "900",
                        "color": self.get_color("primary"),
                        "margin": "0"
                    }
                )
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": hero
        }
    
    def _create_about_section_patch(self) -> Dict[str, Any]:
        """Create about me section."""
        section = self.create_box(
            id="about-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card")
            },
            children=[
                self.create_text(
                    id="about-title",
                    content="About Me",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "borderBottom": f"3px solid {self.get_color('secondary')}",
                        "paddingBottom": "1rem",
                        "marginBottom": self.get_spacing("element")
                    }
                ),
                self.create_text(
                    id="about-content",
                    content=self.about,
                    as_tag="p",
                    style={
                        "fontSize": "1.2rem",
                        "color": self.get_color("text"),
                        "lineHeight": "1.8",
                        "textAlign": "justify"
                    }
                )
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_projects_section_patch(self) -> Dict[str, Any]:
        """Create projects showcase section."""
        project_cards = []
        
        if not self.projects:
            # Default placeholder projects
            self.projects = [
                {"title": "Project 1", "description": "A cool project", "image": "https://picsum.photos/400/300?random=10"},
                {"title": "Project 2", "description": "Another amazing project", "image": "https://picsum.photos/400/300?random=11"},
                {"title": "Project 3", "description": "My best work yet", "image": "https://picsum.photos/400/300?random=12"}
            ]
        
        for idx, project in enumerate(self.projects):
            card_children = []
            
            if project.get("image"):
                card_children.append(
                    self.create_image(
                        id=f"project-{idx}-image",
                        src=project["image"],
                        alt=project["title"],
                        style={
                            "width": "100%",
                            "height": "200px",
                            "objectFit": "cover",
                            "borderRadius": "8px 8px 0 0"
                        }
                    )
                )
            
            card_children.extend([
                self.create_text(
                    id=f"project-{idx}-title",
                    content=project["title"],
                    as_tag="h3",
                    style={
                        "fontSize": "1.5rem",
                        "color": self.get_color("primary"),
                        "marginBottom": "0.5rem"
                    }
                ),
                self.create_text(
                    id=f"project-{idx}-description",
                    content=project["description"],
                    as_tag="p",
                    style={
                        "fontSize": "1rem",
                        "color": self.get_color("textLight")
                    }
                )
            ])
            
            project_cards.append(
                self.create_card(
                    id=f"project-{idx}",
                    children=card_children,
                    variant="elevated",
                    style={
                        "padding": "0",
                        "overflow": "hidden"
                    }
                )
            )
        
        grid = self.create_box(
            id="projects-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                "gap": self.get_spacing("element"),
                "marginTop": self.get_spacing("element")
            },
            children=project_cards
        )
        
        section = self.create_box(
            id="projects-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card")
            },
            children=[
                self.create_text(
                    id="projects-title",
                    content="Projects",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "borderBottom": f"3px solid {self.get_color('secondary')}",
                        "paddingBottom": "1rem"
                    }
                ),
                grid
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_experience_section_patch(self) -> Dict[str, Any]:
        """Create experience/work history section."""
        experience_items = []
        
        if not self.experience:
            self.experience = [
                {"title": "Software Developer", "company": "Tech Co", "period": "2020-Present", "description": "Building awesome things"}
            ]
        
        for idx, exp in enumerate(self.experience):
            experience_items.append(
                self.create_card(
                    id=f"experience-{idx}",
                    children=[
                        self.create_text(
                            id=f"experience-{idx}-title",
                            content=exp["title"],
                            as_tag="h3",
                            style={"fontSize": "1.5rem", "color": self.get_color("primary")}
                        ),
                        self.create_text(
                            id=f"experience-{idx}-company",
                            content=f"{exp['company']} | {exp['period']}",
                            as_tag="p",
                            style={"fontSize": "1rem", "color": self.get_color("textLight"), "marginBottom": "0.5rem"}
                        ),
                        self.create_text(
                            id=f"experience-{idx}-description",
                            content=exp["description"],
                            as_tag="p",
                            style={"fontSize": "1rem", "color": self.get_color("text")}
                        )
                    ],
                    variant="outlined"
                )
            )
        
        section = self.create_box(
            id="experience-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card")
            },
            children=[
                self.create_text(
                    id="experience-title",
                    content="Experience",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "borderBottom": f"3px solid {self.get_color('secondary')}",
                        "paddingBottom": "1rem",
                        "marginBottom": self.get_spacing("element")
                    }
                ),
                self.create_box(
                    id="experience-list",
                    style={"display": "flex", "flexDirection": "column", "gap": self.get_spacing("element")},
                    children=experience_items
                )
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_education_section_patch(self) -> Dict[str, Any]:
        """Create education section."""
        education_items = []
        
        if not self.education:
            self.education = [
                {"degree": "Bachelor of Science", "school": "University", "year": "2020", "description": "Computer Science"}
            ]
        
        for idx, edu in enumerate(self.education):
            education_items.append(
                self.create_card(
                    id=f"education-{idx}",
                    children=[
                        self.create_text(
                            id=f"education-{idx}-degree",
                            content=edu["degree"],
                            as_tag="h3",
                            style={"fontSize": "1.5rem", "color": self.get_color("primary")}
                        ),
                        self.create_text(
                            id=f"education-{idx}-school",
                            content=f"{edu['school']} | {edu['year']}",
                            as_tag="p",
                            style={"fontSize": "1rem", "color": self.get_color("textLight"), "marginBottom": "0.5rem"}
                        ),
                        self.create_text(
                            id=f"education-{idx}-description",
                            content=edu["description"],
                            as_tag="p",
                            style={"fontSize": "1rem", "color": self.get_color("text")}
                        )
                    ],
                    variant="outlined"
                )
            )
        
        section = self.create_box(
            id="education-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card")
            },
            children=[
                self.create_text(
                    id="education-title",
                    content="Education",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "borderBottom": f"3px solid {self.get_color('secondary')}",
                        "paddingBottom": "1rem",
                        "marginBottom": self.get_spacing("element")
                    }
                ),
                self.create_box(
                    id="education-list",
                    style={"display": "flex", "flexDirection": "column", "gap": self.get_spacing("element")},
                    children=education_items
                )
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_skills_section_patch(self) -> Dict[str, Any]:
        """Create skills section."""
        skill_items = []
        
        if not self.skills:
            self.skills = ["JavaScript", "Python", "React", "Vue", "Design"]
        
        for idx, skill in enumerate(self.skills):
            skill_items.append(
                self.create_box(
                    id=f"skill-{idx}",
                    style={
                        "padding": "1rem 1.5rem",
                        "backgroundColor": self.get_color("cardBg"),
                        "borderRadius": "8px",
                        "textAlign": "center",
                        "border": f"2px solid {self.get_color('border')}"
                    },
                    children=[
                        self.create_text(
                            id=f"skill-{idx}-name",
                            content=skill,
                            as_tag="span",
                            style={"fontSize": "1.1rem", "color": self.get_color("primary"), "fontWeight": "600"}
                        )
                    ]
                )
            )
        
        grid = self.create_box(
            id="skills-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
                "gap": self.get_spacing("element"),
                "marginTop": self.get_spacing("element")
            },
            children=skill_items
        )
        
        section = self.create_box(
            id="skills-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card")
            },
            children=[
                self.create_text(
                    id="skills-title",
                    content="Skills",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "borderBottom": f"3px solid {self.get_color('secondary')}",
                        "paddingBottom": "1rem"
                    }
                ),
                grid
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_gallery_section_patch(self) -> Dict[str, Any]:
        """Create image gallery section."""
        gallery_images = []
        
        for i in range(6):
            gallery_images.append(
                self.create_image(
                    id=f"gallery-image-{i}",
                    src=f"https://picsum.photos/400/300?random={20+i}",
                    alt=f"Gallery image {i+1}",
                    style={
                        "width": "100%",
                        "height": "250px",
                        "objectFit": "cover",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "transition": "transform 0.3s ease"
                    }
                )
            )
        
        grid = self.create_box(
            id="gallery-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                "gap": self.get_spacing("element"),
                "marginTop": self.get_spacing("element")
            },
            children=gallery_images
        )
        
        section = self.create_box(
            id="gallery-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card")
            },
            children=[
                self.create_text(
                    id="gallery-title",
                    content="Gallery",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "borderBottom": f"3px solid {self.get_color('secondary')}",
                        "paddingBottom": "1rem"
                    }
                ),
                grid
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_blog_section_patch(self) -> Dict[str, Any]:
        """Create blog/articles section."""
        blog_posts = [
            {"title": "My First Blog Post", "date": "Jan 2024", "excerpt": "An introduction to my journey..."},
            {"title": "Learning New Technologies", "date": "Feb 2024", "excerpt": "Exploring the latest tools..."},
            {"title": "Design Principles", "date": "Mar 2024", "excerpt": "What makes good design..."}
        ]
        
        post_cards = []
        for idx, post in enumerate(blog_posts):
            post_cards.append(
                self.create_card(
                    id=f"blog-post-{idx}",
                    children=[
                        self.create_text(
                            id=f"blog-post-{idx}-title",
                            content=post["title"],
                            as_tag="h3",
                            style={"fontSize": "1.5rem", "color": self.get_color("primary"), "marginBottom": "0.5rem"}
                        ),
                        self.create_text(
                            id=f"blog-post-{idx}-date",
                            content=post["date"],
                            as_tag="p",
                            style={"fontSize": "0.9rem", "color": self.get_color("textLight"), "marginBottom": "0.5rem"}
                        ),
                        self.create_text(
                            id=f"blog-post-{idx}-excerpt",
                            content=post["excerpt"],
                            as_tag="p",
                            style={"fontSize": "1rem", "color": self.get_color("text")}
                        )
                    ],
                    variant="elevated"
                )
            )
        
        section = self.create_box(
            id="blog-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card")
            },
            children=[
                self.create_text(
                    id="blog-title",
                    content="Blog",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "borderBottom": f"3px solid {self.get_color('secondary')}",
                        "paddingBottom": "1rem",
                        "marginBottom": self.get_spacing("element")
                    }
                ),
                self.create_box(
                    id="blog-posts",
                    style={"display": "flex", "flexDirection": "column", "gap": self.get_spacing("element")},
                    children=post_cards
                )
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_contact_section_patch(self) -> Dict[str, Any]:
        """Create contact/links section."""
        links = []
        
        if self.social_links:
            for name, url in self.social_links.items():
                links.append(
                    self.create_link(
                        id=f"social-{name}",
                        href=url,
                        text=name.capitalize(),
                        target="_blank",
                        style={
                            "padding": "0.8rem 1.5rem",
                            "backgroundColor": self.get_color("primary"),
                            "color": self.get_color("background"),
                            "borderRadius": "8px",
                            "textDecoration": "none",
                            "fontSize": "1.1rem",
                            "fontWeight": "600",
                            "transition": "all 0.3s ease"
                        }
                    )
                )
        
        section = self.create_box(
            id="contact-section",
            style={
                "width": "100%",
                "maxWidth": "1200px",
                "margin": f"{self.get_spacing('section')} auto",
                "padding": self.get_spacing("card"),
                "textAlign": "center"
            },
            children=[
                self.create_text(
                    id="contact-title",
                    content="Get In Touch",
                    as_tag="h2",
                    style={
                        "fontSize": "3rem",
                        "fontWeight": "700",
                        "color": self.get_color("primary"),
                        "marginBottom": self.get_spacing("element")
                    }
                ),
                self.create_text(
                    id="contact-description",
                    content="Feel free to reach out for collaborations or just a friendly hello",
                    as_tag="p",
                    style={
                        "fontSize": "1.2rem",
                        "color": self.get_color("textLight"),
                        "marginBottom": self.get_spacing("element")
                    }
                ),
                self.create_box(
                    id="contact-links",
                    style={
                        "display": "flex",
                        "gap": "1rem",
                        "justifyContent": "center",
                        "flexWrap": "wrap"
                    },
                    children=links if links else [
                        self.create_text(
                            id="contact-placeholder",
                            content="Add your social links here",
                            as_tag="p",
                            style={"color": self.get_color("textLight")}
                        )
                    ]
                )
            ],
            as_tag="section"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": section
        }
    
    def _create_footer_section_patch(self) -> Dict[str, Any]:
        """Create footer."""
        footer = self.create_box(
            id="footer-section",
            style={
                "width": "100%",
                "margin": f"{self.get_spacing('section')} 0 0 0",
                "padding": "2rem",
                "textAlign": "center",
                "backgroundColor": self.get_color("cardBg"),
                "borderTop": f"1px solid {self.get_color('border')}"
            },
            children=[
                self.create_text(
                    id="footer-copyright",
                    content=f"© 2024 {self.name}. All rights reserved.",
                    as_tag="p",
                    style={
                        "fontSize": "1rem",
                        "color": self.get_color("textLight")
                    }
                )
            ],
            as_tag="footer"
        )
        
        return {
            "op": "add",
            "path": "/tree/slots/default/-",
            "value": footer
        }
