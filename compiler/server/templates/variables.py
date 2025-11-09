"""
Template Variables and Presets
Defines color palettes, font combinations, and other variables for templates.
"""

# Color Palettes
COLOR_PALETTES = {
    "professional": {
        "primary": "#2c3e50",
        "secondary": "#3498db",
        "accent": "#e74c3c",
        "background": "#ffffff",
        "text": "#333333",
        "textLight": "#7f8c8d",
        "cardBg": "#f8f9fa",
        "border": "#dee2e6"
    },
    "personal": {
        "primary": "#6c5ce7",
        "secondary": "#a29bfe",
        "accent": "#fd79a8",
        "background": "#ffeaa7",
        "text": "#2d3436",
        "textLight": "#636e72",
        "cardBg": "#ffffff",
        "border": "#dfe6e9"
    },
    "quirky": {
        "primary": "#ff6b6b",
        "secondary": "#4ecdc4",
        "accent": "#ffe66d",
        "background": "#f7f1e3",
        "text": "#2d3436",
        "textLight": "#636e72",
        "cardBg": "#ffffff",
        "border": "#ff6b6b"
    },
    "fun": {
        "primary": "#ff6348",
        "secondary": "#ffa502",
        "accent": "#ff4757",
        "background": "#ffffff",
        "text": "#2f3542",
        "textLight": "#57606f",
        "cardBg": "#fff5f5",
        "border": "#ffa502"
    },
    "energetic": {
        "primary": "#ee5a6f",
        "secondary": "#f29e4c",
        "accent": "#efea5a",
        "background": "#f1c0e8",
        "text": "#1a1a2e",
        "textLight": "#16213e",
        "cardBg": "#ffffff",
        "border": "#ee5a6f"
    },
    "dark": {
        "primary": "#00d2ff",
        "secondary": "#3a7bd5",
        "accent": "#00d2ff",
        "background": "#0a0a0a",
        "text": "#ffffff",
        "textLight": "#a0a0a0",
        "cardBg": "#1a1a1a",
        "border": "#333333"
    },
    "minimal": {
        "primary": "#000000",
        "secondary": "#4a4a4a",
        "accent": "#000000",
        "background": "#ffffff",
        "text": "#000000",
        "textLight": "#6a6a6a",
        "cardBg": "#f5f5f5",
        "border": "#e0e0e0"
    }
}

# Font Combinations
FONT_COMBOS = {
    "modern": {
        "heading": "Inter",
        "body": "Inter",
        "googleFontsImport": "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');",
        "headingWeight": "700",
        "bodyWeight": "400"
    },
    "elegant": {
        "heading": "Playfair Display",
        "body": "Source Sans Pro",
        "googleFontsImport": "@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+Pro:wght@400;600&display=swap');",
        "headingWeight": "700",
        "bodyWeight": "400"
    },
    "tech": {
        "heading": "Space Grotesk",
        "body": "Space Grotesk",
        "googleFontsImport": "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');",
        "headingWeight": "700",
        "bodyWeight": "400"
    },
    "playful": {
        "heading": "Fredoka",
        "body": "Nunito",
        "googleFontsImport": "@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Nunito:wght@400;600&display=swap');",
        "headingWeight": "600",
        "bodyWeight": "400"
    },
    "classic": {
        "heading": "Montserrat",
        "body": "Lato",
        "googleFontsImport": "@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Lato:wght@400;700&display=swap');",
        "headingWeight": "700",
        "bodyWeight": "400"
    },
    "serif": {
        "heading": "Merriweather",
        "body": "Merriweather",
        "googleFontsImport": "@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&display=swap');",
        "headingWeight": "700",
        "bodyWeight": "400"
    }
}

# Spacing scales
SPACING = {
    "compact": {"section": "3rem", "card": "1.5rem", "element": "1rem"},
    "normal": {"section": "4rem", "card": "2rem", "element": "1.5rem"},
    "spacious": {"section": "6rem", "card": "3rem", "element": "2rem"}
}

# Border radius presets
BORDER_RADIUS = {
    "sharp": "0px",
    "subtle": "4px",
    "rounded": "8px",
    "soft": "12px",
    "pill": "50px"
}

# Shadow presets
SHADOWS = {
    "none": "none",
    "subtle": "0 2px 4px rgba(0, 0, 0, 0.05)",
    "soft": "0 4px 12px rgba(0, 0, 0, 0.08)",
    "medium": "0 8px 20px rgba(0, 0, 0, 0.12)",
    "strong": "0 12px 32px rgba(0, 0, 0, 0.18)"
}

# Animation speeds
ANIMATION = {
    "instant": "0.1s",
    "fast": "0.2s",
    "normal": "0.3s",
    "slow": "0.5s"
}

def get_palette(palette_name: str) -> dict:
    """Get color palette by name, defaults to professional if not found."""
    return COLOR_PALETTES.get(palette_name, COLOR_PALETTES["professional"])

def get_fonts(font_combo: str) -> dict:
    """Get font combination by name, defaults to modern if not found."""
    return FONT_COMBOS.get(font_combo, FONT_COMBOS["modern"])

def generate_global_styles(palette_name: str = "professional", font_combo: str = "modern") -> str:
    """Generate global CSS styles string for a given palette and font combo."""
    palette = get_palette(palette_name)
    fonts = get_fonts(font_combo)
    
    return f"""{fonts['googleFontsImport']}
body {{
    font-family: '{fonts['body']}', sans-serif;
    background-color: {palette['background']};
    color: {palette['text']};
    margin: 0;
    padding: 0;
    line-height: 1.6;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: '{fonts['heading']}', sans-serif;
    font-weight: {fonts['headingWeight']};
    margin: 0;
}}

* {{
    box-sizing: border-box;
}}"""
