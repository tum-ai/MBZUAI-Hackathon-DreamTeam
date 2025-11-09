# Template Generation API

This document describes the new API endpoint for generating multiple website variations from templates.

## Overview

The `/generate-template-variations` endpoint generates **4 variations** of a selected template, each with a different color palette and font combination. The variations are saved to `/tmp/selection/0`, `/tmp/selection/1`, `/tmp/selection/2`, and `/tmp/selection/3` for the container to watch and display.

## Endpoint

**POST** `/generate-template-variations`

### Request Body

```json
{
  "template_type": "blog",
  "variables": {
    "blogName": "Tech Insights",
    "tagline": "Exploring Technology",
    "posts": [
      {
        "title": "Post Title",
        "date": "Nov 9, 2025",
        "excerpt": "Post excerpt...",
        "image": "https://..."
      }
    ],
    "about": "Blog description..."
  }
}
```

### Template Types

| Template | Pages | Use Case |
|----------|-------|----------|
| `portfolio` | Home, About, Projects, Contact | Personal portfolios |
| `product` | Home, Features, Specs, Gallery | Product showcases |
| `gallery` | Home, Gallery, About | Photography/art |
| `ecommerce` | Home, Products, About, Contact | Online stores |
| `blog` | Home, Blog, About, Contact | Blogs/articles |

### Response

```json
{
  "status": "success",
  "template_type": "blog",
  "selection_dir": "/tmp/selection",
  "variations": [
    {
      "index": 0,
      "palette": "professional",
      "font": "modern",
      "path": "/tmp/selection/0",
      "pages": ["home.json", "blog.json", "about.json", "contact.json"],
      "project_file": "/tmp/selection/0/project.json"
    },
    {
      "index": 1,
      "palette": "dark",
      "font": "tech",
      "path": "/tmp/selection/1",
      "pages": ["home.json", "blog.json", "about.json", "contact.json"],
      "project_file": "/tmp/selection/1/project.json"
    },
    {
      "index": 2,
      "palette": "minimal",
      "font": "elegant",
      "path": "/tmp/selection/2",
      "pages": ["home.json", "blog.json", "about.json", "contact.json"],
      "project_file": "/tmp/selection/2/project.json"
    },
    {
      "index": 3,
      "palette": "energetic",
      "font": "playful",
      "path": "/tmp/selection/3",
      "pages": ["home.json", "blog.json", "about.json", "contact.json"],
      "project_file": "/tmp/selection/3/project.json"
    }
  ],
  "message": "Generated 4 variations of blog template"
}
```

## Palette Variations

The 4 variations use these palettes:

1. **Professional** - Modern font, business colors (blue, gray)
2. **Dark** - Tech font, dark background with neon accents
3. **Minimal** - Elegant font, clean black & white
4. **Energetic** - Playful font, vibrant colors

## Output Structure

Each variation is saved in `/tmp/selection/{index}/` as a **complete, ready-to-run Vue.js project**:

```
/tmp/selection/
├── 0/                          # Variation 0 (professional) - READY TO RUN!
│   ├── package.json            # Vue project dependencies
│   ├── index.html              # Entry point
│   ├── vite.config.js          # Vite configuration
│   ├── project.json            # Internal project config
│   ├── src/                    # Vue source files
│   │   ├── App.vue             # Root component
│   │   ├── main.js             # Vue entry
│   │   ├── router/
│   │   │   └── index.js        # Vue Router config
│   │   └── views/              # Generated page components
│   │       ├── Home.vue
│   │       ├── Blog.vue
│   │       ├── About.vue
│   │       └── Contact.vue
│   ├── public/                 # Public assets
│   ├── inputs/                 # Page AST files (internal)
│   │   ├── home.json
│   │   ├── blog.json
│   │   ├── about.json
│   │   └── contact.json
│   ├── static/                 # Static templates (internal)
│   └── manifests/              # Component manifests (internal)
├── 1/                          # Variation 1 (dark) - READY TO RUN!
│   └── (same structure as variation 0)
├── 2/                          # Variation 2 (minimal) - READY TO RUN!
│   └── (same structure as variation 0)
└── 3/                          # Variation 3 (energetic) - READY TO RUN!
    └── (same structure as variation 0)
```

**Each variation can be run immediately:**
```bash
cd /tmp/selection/0
npm install
npm run dev
# Opens on http://localhost:5173
```

## Template Variables

### Blog Template

```json
{
  "blogName": "string",
  "tagline": "string",
  "authorName": "string (optional)",
  "about": "string",
  "posts": [
    {
      "title": "string",
      "date": "string",
      "excerpt": "string",
      "image": "url"
    }
  ]
}
```

### Product Template

```json
{
  "productName": "string",
  "tagline": "string",
  "heroImage": "url",
  "features": [
    {
      "title": "string",
      "description": "string"
    }
  ],
  "specs": [
    {
      "label": "string",
      "value": "string"
    }
  ],
  "galleryImages": ["url", "url", ...]
}
```

### Gallery Template

```json
{
  "name": "string",
  "tagline": "string",
  "heroImage": "url",
  "galleryImages": ["url", "url", ...],
  "about": "string"
}
```

### E-commerce Template

```json
{
  "storeName": "string",
  "tagline": "string",
  "heroImage": "url",
  "products": [
    {
      "name": "string",
      "price": "string",
      "image": "url"
    }
  ],
  "about": "string"
}
```

### Portfolio Template

```json
{
  "name": "string",
  "title": "string",
  "bio": "string",
  "profileImage": "url",
  "skills": ["skill1", "skill2", ...],
  "projects": [
    {
      "title": "string",
      "description": "string",
      "image": "url",
      "link": "url (optional)"
    }
  ],
  "contact": {
    "email": "string",
    "github": "string (optional)",
    "linkedin": "string (optional)"
  }
}
```

## Usage Example

### Python

```python
import requests

response = requests.post("http://127.0.0.1:8000/generate-template-variations", json={
    "template_type": "blog",
    "variables": {
        "blogName": "My Tech Blog",
        "tagline": "Exploring AI and Web Development",
        "posts": [
            {
                "title": "Getting Started with AI",
                "date": "Nov 9, 2025",
                "excerpt": "An introduction to AI concepts...",
                "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800"
            }
        ],
        "about": "A blog about technology and innovation."
    }
})

result = response.json()
print(f"Generated {len(result['variations'])} variations")
for var in result['variations']:
    print(f"  [{var['index']}] {var['palette']} at {var['path']}")
```

### cURL

```bash
curl -X POST http://127.0.0.1:8000/generate-template-variations \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "product",
    "variables": {
      "productName": "Amazing Product",
      "tagline": "The best product ever",
      "heroImage": "https://...",
      "features": [
        {"title": "Feature 1", "description": "Description..."}
      ],
      "specs": [
        {"label": "Size", "value": "Large"}
      ],
      "galleryImages": ["https://..."]
    }
  }'
```

### JavaScript/TypeScript

```typescript
const response = await fetch("http://127.0.0.1:8000/generate-template-variations", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    template_type: "gallery",
    variables: {
      name: "Jane Doe",
      tagline: "Photographer",
      heroImage: "https://...",
      galleryImages: ["https://...", "https://..."],
      about: "Fine art photographer..."
    }
  })
});

const result = await response.json();
console.log(`Generated ${result.variations.length} variations`);
```

## Testing

Run the test script to verify the API:

```bash
cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server
python test_template_api.py
```

This will:
1. Check if the server is running
2. Generate 4 variations for each template type
3. Verify the output files are created
4. Display a summary of results

## Integration with Container

The container should:

1. Watch `/tmp/selection/0`, `/tmp/selection/1`, `/tmp/selection/2`, `/tmp/selection/3`
2. When files change in any variation directory:
   - Read `project.json` for configuration
   - Read page ASTs from `inputs/*.json`
   - Serve the generated output from `output/site/`
3. Display all 4 variations side-by-side for the user to choose

## Workflow

```
User: "Create a blog about technology"
    ↓
LLM: Extract intent + variables
    ↓
POST /generate-template-variations
{
  template_type: "blog",
  variables: {...}
}
    ↓
Server generates 4 variations:
  - Professional (modern, business colors)
  - Dark (tech, dark theme)
  - Minimal (elegant, clean)
  - Energetic (playful, vibrant)
    ↓
Container watches /tmp/selection/
    ↓
User sees 4 previews, selects one
    ↓
Selected variation becomes active project
```

## Error Handling

### Invalid Template Type

```json
{
  "detail": "Invalid template type. Available: portfolio, product, gallery, ecommerce, blog"
}
```

### Missing Variables

The template system will use defaults for missing variables, but key fields should be provided for best results.

### Generation Error

```json
{
  "detail": "Error generating template variations: <error message>"
}
```

## Notes

- The `/tmp/selection` directory is hardcoded as specified
- Each generation **overwrites** previous variations in `/tmp/selection/0-3`
- The container should be prepared to handle file changes
- All 4 variations are generated synchronously (may take a few seconds)
- Generated files include complete Vue projects ready to serve
