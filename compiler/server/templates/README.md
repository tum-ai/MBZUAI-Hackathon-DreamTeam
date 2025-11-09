# Template System Documentation

## Overview

The template system provides a modular, parameterized way to generate complete website starters. Instead of building sites from scratch every time, you can use templates with customizable variables to generate professional, ready-to-use JSON Patch operations.

## Architecture

```
templates/
├── __init__.py           # Main API and template registry
├── base.py              # Base template class with utilities
├── variables.py         # Color palettes, fonts, spacing presets
├── portfolio.py         # Portfolio template implementation
└── examples/            # Example variable files and outputs
    ├── portfolio_kesava.json
    ├── portfolio_kesava_output.json
    ├── portfolio_quirky.json
    └── portfolio_academic.json
```

## Quick Start

### Command Line Usage

```bash
# List available templates
python template_generator.py --list

# Get template information
python template_generator.py --info portfolio

# Generate from variables file
python template_generator.py portfolio \
  --input templates/examples/portfolio_kesava.json \
  --output output.json

# Generate with inline JSON
python template_generator.py portfolio \
  --vars '{"name":"John","tagline":"Developer","palette":"professional"}'
```

### Python API Usage

```python
from templates import generate_from_template

# Define variables
variables = {
    "name": "Jane Doe",
    "tagline": "Full Stack Developer",
    "palette": "professional",
    "fonts": "modern",
    "sections": ["about", "projects", "contact"]
}

# Generate patches
patches = generate_from_template("portfolio", variables)

# patches is now a list of JSON Patch operations ready to apply
```

## Available Templates

### Portfolio Template

**Purpose**: Personal portfolio website with customizable sections

**Required Variables**:
- `name` (str): Person's name
- `tagline` (str): Professional tagline/role

**Optional Variables**:
- `palette` (str): Color scheme
  - Options: `professional`, `personal`, `quirky`, `fun`, `energetic`, `dark`, `minimal`
  - Default: `professional`
  
- `fonts` (str): Font combination
  - Options: `modern`, `elegant`, `tech`, `playful`, `classic`, `serif`
  - Default: `modern`
  
- `spacing` (str): Spacing scale
  - Options: `compact`, `normal`, `spacious`
  - Default: `normal`
  
- `heroLayout` (str): Hero section layout
  - Options: `centered`, `split`, `minimal`
  - Default: `split`
  
- `image` (str): URL to profile/hero image
  - Default: Placeholder image
  
- `about` (str): About me text
  - Default: Placeholder text
  
- `sections` (list[str]): Which sections to include
  - Options: `about`, `projects`, `education`, `experience`, `skills`, `gallery`, `blog`, `contact`
  - Default: `["about", "projects", "contact"]`
  
- `projects` (list[dict]): Project data
  - Each project: `{title, description, image}`
  
- `education` (list[dict]): Education data
  - Each entry: `{degree, school, year, description}`
  
- `experience` (list[dict]): Work experience data
  - Each entry: `{title, company, period, description}`
  
- `skills` (list[str]): List of skills
  
- `socialLinks` (dict): Social media links
  - Keys: `github`, `linkedin`, `twitter`, `email`, `dribbble`, `scholar`, etc.

**Example Variables**:

```json
{
  "name": "Kesava Prasad",
  "tagline": "Student at TUM | Photography & Coding Enthusiast",
  "palette": "professional",
  "fonts": "modern",
  "heroLayout": "split",
  "sections": ["about", "skills", "projects", "contact"],
  "skills": ["Photography", "Coding", "Chess", "Hackathons"],
  "socialLinks": {
    "github": "https://github.com/kesava89",
    "email": "mailto:kesava@example.com"
  }
}
```

## Color Palettes

### Professional (Default)
- Clean, corporate look
- Blue accents on white background
- Ideal for: Business, consulting, corporate portfolios

### Personal
- Warm, approachable feel
- Purple and pink tones
- Ideal for: Creative professionals, personal brands

### Quirky
- Fun, unique vibe
- Bright red, teal, and yellow
- Ideal for: Designers, artists, creative agencies

### Fun
- Energetic and vibrant
- Orange and red tones
- Ideal for: Youth brands, entertainment, startups

### Energetic
- Bold and exciting
- Pink, orange, and yellow gradients
- Ideal for: Fitness, events, dynamic brands

### Dark
- Modern, sleek appearance
- Dark background with blue accents
- Ideal for: Tech, gaming, modern portfolios

### Minimal
- Ultra-clean, black and white
- Minimalist aesthetic
- Ideal for: Architecture, photography, luxury brands

## Font Combinations

### Modern (Default)
- **Heading & Body**: Inter
- Clean, versatile, professional

### Elegant
- **Heading**: Playfair Display
- **Body**: Source Sans Pro
- Sophisticated, classic

### Tech
- **Heading & Body**: Space Grotesk
- Modern, geometric, tech-forward

### Playful
- **Heading**: Fredoka
- **Body**: Nunito
- Friendly, approachable, fun

### Classic
- **Heading**: Montserrat
- **Body**: Lato
- Timeless, professional

### Serif
- **Heading & Body**: Merriweather
- Traditional, scholarly

## Extending the System

### Creating a New Template

1. **Create template file** (e.g., `templates/landing_page.py`):

```python
from typing import Dict, List, Any
from .base import TemplateBase

class LandingPageTemplate(TemplateBase):
    """Landing page template with hero, features, and CTA."""
    
    def __init__(self, variables: Dict[str, Any]):
        super().__init__(variables)
        self.title = variables.get("title", "Welcome")
        self.subtitle = variables.get("subtitle", "")
        # ... more variables
    
    def generate_patches(self) -> List[Dict[str, Any]]:
        patches = []
        patches.append(self.create_global_styles_patch())
        patches.append(self._create_hero())
        # ... more sections
        return patches
    
    def _create_hero(self) -> Dict[str, Any]:
        hero = self.create_box(
            id="hero",
            style={"height": "100vh", "display": "flex"},
            children=[
                self.create_gradient_text(
                    id="hero-title",
                    content=self.title
                )
            ]
        )
        return {"op": "add", "path": "/tree/slots/default/-", "value": hero}
```

2. **Register in `templates/__init__.py`**:

```python
from .landing_page import LandingPageTemplate

TEMPLATES = {
    "portfolio": PortfolioTemplate,
    "landing_page": LandingPageTemplate,  # Add here
}
```

3. **Create example variables** in `templates/examples/`

### Adding Color Palettes

Edit `templates/variables.py`:

```python
COLOR_PALETTES = {
    # ... existing palettes
    "cyberpunk": {
        "primary": "#ff00ff",
        "secondary": "#00ffff",
        "accent": "#ffff00",
        "background": "#0a0014",
        "text": "#ffffff",
        "textLight": "#b0b0ff",
        "cardBg": "#1a0028",
        "border": "#ff00ff"
    }
}
```

### Adding Font Combinations

Edit `templates/variables.py`:

```python
FONT_COMBOS = {
    # ... existing combos
    "handwritten": {
        "heading": "Caveat",
        "body": "Open Sans",
        "googleFontsImport": "@import url('...');",
        "headingWeight": "700",
        "bodyWeight": "400"
    }
}
```

## Integration with Compiler

The template system generates JSON Patch operations that are **identical in format** to what the LLM compiler generates. This means:

1. Templates provide **instant starter sites**
2. Users can then use **voice commands** to modify the generated site
3. All modifications use the **same JSON Patch format**
4. **Seamless transition** from template to custom edits

### Workflow

```
1. User selects template + variables
   ↓
2. Template generator creates JSON Patches
   ↓
3. Patches applied to create initial project
   ↓
4. User modifies with voice: "Add a testimonials section"
   ↓
5. LLM generates more patches
   ↓
6. Combined template + custom edits = final site
```

## Examples in Action

### Example 1: Professional Portfolio

```bash
python template_generator.py portfolio \
  --input templates/examples/portfolio_kesava.json \
  --output outputs/kesava_site.json
```

Generates: Full-height hero with split layout, about section, skills grid, projects showcase, contact form

### Example 2: Minimal Academic

```bash
python template_generator.py portfolio \
  --input templates/examples/portfolio_academic.json \
  --output outputs/academic_site.json
```

Generates: Minimal hero, experience timeline, education list, blog section

### Example 3: Quirky Designer

```bash
python template_generator.py portfolio \
  --input templates/examples/portfolio_quirky.json \
  --output outputs/designer_site.json
```

Generates: Centered hero with playful fonts, colorful project cards, fun aesthetics

## Best Practices

1. **Start with a template** for quick initial structure
2. **Customize variables** to match brand/personality
3. **Use voice commands** for fine-tuning and additions
4. **Maintain semantic IDs** when extending templates
5. **Test with different palettes** to find the right feel
6. **Combine sections** strategically based on content needs

## Troubleshooting

**Template not found**: Run `python template_generator.py --list` to see available templates

**Invalid variables**: Run `python template_generator.py --info <template>` to see required/optional variables

**JSON parse error**: Validate your variables file with a JSON linter

**Missing sections**: Check the `sections` array in your variables

## Future Templates (Planned)

- Landing Page (marketing site with hero, features, pricing, CTA)
- Blog (article listing, post pages, categories)
- E-commerce (product grid, cart, checkout)
- Documentation (sidebar nav, search, code examples)
- Agency (services, team, case studies)
- Restaurant (menu, reservations, gallery)

## Contributing

To contribute a new template:

1. Create template class inheriting from `TemplateBase`
2. Implement `generate_patches()` method
3. Register in `TEMPLATES` registry
4. Add example variables in `templates/examples/`
5. Document in this README
