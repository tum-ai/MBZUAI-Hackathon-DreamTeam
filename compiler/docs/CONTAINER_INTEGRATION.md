# Container Integration Guide

This guide explains how to integrate the template system with a container that hosts 5 ports: 4 for previewing template variations and 1 for editing the selected template.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Container                            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Port 5173: Variation 0 (Professional + Modern)  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Port 5174: Variation 1 (Dark + Tech)            │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Port 5175: Variation 2 (Minimal + Elegant)      │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Port 5176: Variation 3 (Energetic + Playful)    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Port 5177: ⭐ ACTIVE (Selected for Editing) ⭐   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## File Structure

```
/tmp/
├── selection/          # Preview variations (read-only)
│   ├── 0/             # Professional + Modern
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   ├── index.html
│   │   ├── project.json
│   │   └── src/
│   │       ├── App.vue
│   │       ├── main.js
│   │       ├── router/
│   │       └── views/
│   ├── 1/             # Dark + Tech
│   ├── 2/             # Minimal + Elegant
│   └── 3/             # Energetic + Playful
│
└── active/            # Selected variation (editable)
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── project.json
    └── src/
        ├── App.vue
        ├── main.js
        ├── router/
        └── views/
```

## Workflow

### 1. Generate Template Variations

**API Endpoint:** `POST /generate-template-variations`

Generates 4 variations of a template with different palette and font combinations.

```bash
curl -X POST http://localhost:8000/generate-template-variations \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "product",
    "variables": {
      "productName": "iPhone 16 Pro",
      "tagline": "Titanium. So Pro.",
      "heroImage": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=1920",
      "features": [
        {"title": "A18 Pro Chip", "description": "Blazing fast performance"},
        {"title": "Pro Camera", "description": "48MP with 10x zoom"}
      ]
    }
  }'
```

**Response:**
```json
{
  "message": "Generated 4 template variations",
  "variations": [
    {"index": 0, "palette": "professional", "font": "modern", "path": "/tmp/selection/0"},
    {"index": 1, "palette": "dark", "font": "tech", "path": "/tmp/selection/1"},
    {"index": 2, "palette": "minimal", "font": "elegant", "path": "/tmp/selection/2"},
    {"index": 3, "palette": "energetic", "font": "playful", "path": "/tmp/selection/3"}
  ],
  "selection_dir": "/tmp/selection",
  "active_project_dir": "/tmp/active",
  "preview_ports": {
    "variation_0": 5173,
    "variation_1": 5174,
    "variation_2": 5175,
    "variation_3": 5176,
    "active": 5177
  }
}
```

### 2. Select a Variation

**API Endpoint:** `POST /select-template-variation`

Copies a variation to `/tmp/active` for editing.

```bash
curl -X POST http://localhost:8000/select-template-variation \
  -H "Content-Type: application/json" \
  -d '{"variation_index": 1}'
```

**Response:**
```json
{
  "message": "Template variation selected and copied to active project",
  "selected_variation": 1,
  "palette": "dark",
  "font": "tech",
  "active_project_path": "/tmp/active",
  "project_name": "New GenAI Project",
  "pages": ["Home", "Features", "Specs", "Gallery"],
  "preview_ports": {
    "variation_0": 5173,
    "variation_1": 5174,
    "variation_2": 5175,
    "variation_3": 5176,
    "active": 5177
  }
}
```

### 3. Check Active Project Status

**API Endpoint:** `GET /active-project`

Returns information about the current active project.

```bash
curl http://localhost:8000/active-project
```

**Response (when active):**
```json
{
  "status": "active",
  "active_project_path": "/tmp/active",
  "project_name": "New GenAI Project",
  "pages": ["Home", "Features", "Specs", "Gallery"],
  "container_port": 5177,
  "message": "Active project ready"
}
```

**Response (when none):**
```json
{
  "status": "none",
  "message": "No active project. Use POST /select-template-variation to select one."
}
```

## Container Implementation

### Starting Dev Servers

The container should start 5 Vite dev servers:

```bash
# Variation 0 (Preview)
cd /tmp/selection/0 && npm install && npm run dev -- --port 5173 --host &

# Variation 1 (Preview)
cd /tmp/selection/1 && npm install && npm run dev -- --port 5174 --host &

# Variation 2 (Preview)
cd /tmp/selection/2 && npm install && npm run dev -- --port 5175 --host &

# Variation 3 (Preview)
cd /tmp/selection/3 && npm install && npm run dev -- --port 5176 --host &

# Active Project (Editable)
if [ -d "/tmp/active" ]; then
  cd /tmp/active && npm install && npm run dev -- --port 5177 --host &
fi
```

Or use the helper script:

```bash
cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server
./run_variations.sh
```

### File Watching Strategy

The container should implement different watching strategies for preview vs. active:

#### Preview Variations (5173-5176)
- **Location:** `/tmp/selection/{0,1,2,3}`
- **Strategy:** Read-only, no hot reload needed
- **Purpose:** Show different styling options
- **Rebuild:** Only when new variations are generated via API

#### Active Project (5177)
- **Location:** `/tmp/active`
- **Strategy:** Full hot reload with file watching
- **Purpose:** Allow user to edit and see changes in real-time
- **Rebuild:** On every file change in `/tmp/active/src/`

### User Interaction Flow

1. **User requests template:** LLM calls `POST /generate-template-variations`
2. **Container displays 4 previews:** Shows ports 5173-5176 side-by-side
3. **User selects a variation:** UI calls `POST /select-template-variation`
4. **Container switches to active:** Shows port 5177 for editing
5. **User edits template:** Changes to `/tmp/active/src/` trigger hot reload
6. **User can switch back:** To preview other variations and select different one

## Template Types

Available templates with multi-page support:

### 1. Product Showcase
- **Template Type:** `product`
- **Pages:** Home, Features, Specs, Gallery
- **Best For:** Products, apps, hardware
- **Variables:**
  - `productName`: Product name
  - `tagline`: Hero tagline
  - `heroImage`: Hero background image URL
  - `features`: Array of {title, description}
  - `specs`: Array of {label, value}
  - `galleryImages`: Array of image URLs

### 2. Portfolio
- **Template Type:** `portfolio`
- **Pages:** Home, Projects, About, Contact
- **Best For:** Personal websites, showcases
- **Variables:**
  - `name`: Your name
  - `title`: Professional title
  - `bio`: Short bio
  - `projects`: Array of {name, description, image, link}
  - `skills`: Array of skill names
  - `social`: Object with {github, linkedin, twitter, email}

### 3. Gallery
- **Template Type:** `gallery`
- **Pages:** Home, Gallery, About
- **Best For:** Photography, art portfolios
- **Variables:**
  - `title`: Gallery title
  - `subtitle`: Gallery subtitle
  - `heroImage`: Hero background
  - `images`: Array of {url, title, description}
  - `about`: About text

### 4. E-commerce
- **Template Type:** `ecommerce`
- **Pages:** Home, Products, About, Contact
- **Best For:** Online stores, shops
- **Variables:**
  - `storeName`: Store name
  - `tagline`: Store tagline
  - `products`: Array of {name, price, image, description}
  - `categories`: Array of category names

### 5. Blog
- **Template Type:** `blog`
- **Pages:** Home, Blog, About, Contact
- **Best For:** Blogs, news sites
- **Variables:**
  - `siteName`: Blog name
  - `tagline`: Blog tagline
  - `posts`: Array of {title, excerpt, author, date, image}
  - `categories`: Array of category names

## Palette & Font Combinations

### Variation 0: Professional + Modern
- **Colors:** Navy blues, slate grays
- **Fonts:** Inter, system-ui
- **Vibe:** Corporate, trustworthy

### Variation 1: Dark + Tech
- **Colors:** Deep blacks, cyan accents
- **Fonts:** JetBrains Mono, monospace
- **Vibe:** Technical, developer-focused

### Variation 2: Minimal + Elegant
- **Colors:** Soft whites, muted tones
- **Fonts:** Playfair Display, serif
- **Vibe:** Clean, sophisticated

### Variation 3: Energetic + Playful
- **Colors:** Vibrant oranges, purples
- **Fonts:** Poppins, rounded sans
- **Vibe:** Fun, youthful

## Testing

Run the complete workflow test:

```bash
cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server
python test_selection.py
```

This will:
1. Generate 4 variations
2. Select variation 1 as active
3. Verify file structure
4. Show port configuration

## Container Dockerfile Example

```dockerfile
FROM node:20-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose all 5 ports
EXPOSE 5173 5174 5175 5176 5177 8000

# Start script that runs API server and watches for variations
CMD ["./start_container.sh"]
```

## Container Start Script Example

```bash
#!/bin/bash
# start_container.sh

# Start API server in background
cd /app/compiler/server
python run_server.py &

# Wait for variations to be generated
echo "Waiting for template variations..."
while [ ! -d "/tmp/selection/0" ]; do
  sleep 1
done

# Start all dev servers
./run_variations.sh

# Keep container running
tail -f /tmp/variation-*.log /tmp/active.log
```

## API Integration Examples

### Python Example

```python
import requests

# Generate variations
response = requests.post(
    "http://localhost:8000/generate-template-variations",
    json={
        "template_type": "product",
        "variables": {"productName": "My Product"}
    }
)
variations = response.json()

# Select variation 2
response = requests.post(
    "http://localhost:8000/select-template-variation",
    json={"variation_index": 2}
)
active = response.json()

print(f"Active project on port {active['preview_ports']['active']}")
```

### JavaScript Example

```javascript
// Generate variations
const response = await fetch('http://localhost:8000/generate-template-variations', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    template_type: 'product',
    variables: {productName: 'My Product'}
  })
});
const variations = await response.json();

// Select variation
const selectResponse = await fetch('http://localhost:8000/select-template-variation', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({variation_index: 2})
});
const active = await selectResponse.json();

console.log(`Active: http://localhost:${active.preview_ports.active}`);
```

## Troubleshooting

### Ports Already in Use

```bash
# Find and kill processes on ports
lsof -ti:5173,5174,5175,5176,5177 | xargs kill -9

# Or use the stop script
./stop_variations.sh
```

### Variations Not Generating

Check that the API server is running:
```bash
curl http://localhost:8000/project
```

### Active Project Not Starting

Verify the active directory exists:
```bash
ls -la /tmp/active/
```

If not, select a variation first:
```bash
curl -X POST http://localhost:8000/select-template-variation \
  -H "Content-Type: application/json" \
  -d '{"variation_index": 0}'
```

## Best Practices

1. **Generate once, preview all:** Generate all 4 variations upfront, don't regenerate unless needed
2. **Selection is cheap:** Copying a variation to `/tmp/active` is fast, users can switch freely
3. **Watch only active:** Only enable hot reload for `/tmp/active`, not preview variations
4. **Clean on exit:** Use `./stop_variations.sh` to properly clean up processes and logs
5. **Port consistency:** Always use the same port mapping (5173-5177) for predictable URLs

## Summary

- **5 Ports Total:** 4 previews + 1 active
- **Preview Ports (5173-5176):** Show different palette/font combos, read-only
- **Active Port (5177):** Selected variation for editing with hot reload
- **Selection Flow:** Generate → Preview 4 variations → Select one → Edit in active
- **File Locations:** `/tmp/selection/{0,1,2,3}` for previews, `/tmp/active` for editing
- **API Endpoints:** 
  - `POST /generate-template-variations` - Create 4 variations
  - `POST /select-template-variation` - Copy to active
  - `GET /active-project` - Check active status
