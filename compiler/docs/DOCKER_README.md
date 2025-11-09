# Docker Setup for Compiler Service

This directory contains Docker configurations to run the template compiler system with two services:
1. **API Server** - Generates template variations via REST API
2. **Variations Viewer** - Hosts 5 dev servers for previewing and editing templates

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Host                            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  compiler-api (Port 8000)                          │ │
│  │  - FastAPI server                                  │ │
│  │  - Generates 4 template variations                 │ │
│  │  - Writes to /tmp/selection/{0,1,2,3}             │ │
│  │  - Writes active project to /tmp/active            │ │
│  └────────────────────────────────────────────────────┘ │
│                         ↓                                │
│              (shared volumes)                            │
│        /tmp/selection  &  /tmp/active                    │
│                         ↓                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  compiler-variations (Ports 5173-5177)             │ │
│  │  - Runs 5 Vite dev servers                         │ │
│  │  - Reads from shared volumes                       │ │
│  │  - Port 5173-5176: Preview variations             │ │
│  │  - Port 5177: Active/editable project             │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Files

- **Dockerfile** - Main API server image
- **Dockerfile.variations** - Variations viewer image  
- **docker-compose.yml** - Orchestrates both services with shared volumes

## Quick Start

### Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)

### Build and Run

From the **repository root** directory:

```bash
cd /path/to/MBZUAI-Hackathon-DreamTeam

# Build and start both services
docker-compose -f compiler/docker-compose.yml up --build
```

This will:
1. Build both images
2. Start the API server on port 8000
3. Wait for template variations to be generated
4. Start 5 dev servers when variations are ready

### Generate Templates

In another terminal:

```bash
# Generate 4 template variations
curl -X POST http://localhost:8000/generate-template-variations \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "product",
    "variables": {
      "productName": "iPhone 16 Pro",
      "tagline": "Titanium. So Pro.",
      "heroImage": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=1920",
      "features": [
        {"title": "A18 Pro Chip", "description": "Blazing fast"},
        {"title": "Pro Camera", "description": "48MP"}
      ],
      "specs": [
        {"label": "Display", "value": "6.3\" Super Retina XDR"},
        {"label": "Chip", "value": "A18 Pro"}
      ],
      "galleryImages": [
        "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800"
      ]
    }
  }'
```

### View Variations

Once generated, the variations viewer will automatically start dev servers:

- **Variation 0 (Professional):** http://localhost:5173
- **Variation 1 (Dark):** http://localhost:5174
- **Variation 2 (Minimal):** http://localhost:5175
- **Variation 3 (Energetic):** http://localhost:5176

### Select and Edit

Select a variation to copy to the active project:

```bash
# Select variation 1 (Dark theme)
curl -X POST http://localhost:8000/select-template-variation \
  -H "Content-Type: application/json" \
  -d '{"variation_index": 1}'
```

The selected variation will be available for editing at:
- **Active Project:** http://localhost:5177 ⭐

## Manual Control

### Start Services Separately

```bash
# API server only
docker-compose -f compiler/docker-compose.yml up compiler-api

# Variations viewer only (requires API server running)
docker-compose -f compiler/docker-compose.yml up compiler-variations
```

### Execute Commands in Running Containers

```bash
# Run variations script manually
docker exec -it compiler-api /app/compiler/server/run_variations.sh

# Check API server logs
docker logs -f compiler-api

# Check variations logs
docker logs -f compiler-variations
```

### Stop Services

```bash
# Stop all services
docker-compose -f compiler/docker-compose.yml down

# Stop and remove volumes
docker-compose -f compiler/docker-compose.yml down -v
```

## Development Mode

For development with hot reload, mount local directories:

```yaml
# In docker-compose.yml (already configured)
volumes:
  - ./server:/app/compiler/server
  - ./manifests:/app/compiler/manifests
  - ./server/templates:/app/compiler/server/templates
```

Changes to Python files will trigger auto-reload (uvicorn's `--reload` flag).

## Volumes

Two shared volumes enable communication between services:

1. **template-variations** - Maps to `/tmp/selection`
   - Contains 4 preview variations (0, 1, 2, 3)
   - Written by API server, read by variations viewer

2. **active-project** - Maps to `/tmp/active`
   - Contains the selected variation for editing
   - Written by API server, read by variations viewer

## Ports

| Port | Service | Purpose |
|------|---------|---------|
| 8000 | API Server | REST API for template generation |
| 5173 | Variation 0 | Professional palette preview |
| 5174 | Variation 1 | Dark palette preview |
| 5175 | Variation 2 | Minimal palette preview |
| 5176 | Variation 3 | Energetic palette preview |
| 5177 | Active Project | Selected variation for editing |

## Environment Variables

### API Server (compiler-api)

- `HOST=0.0.0.0` - Listen on all interfaces
- `PORT=8000` - API server port
- `PYTHONUNBUFFERED=1` - Immediate log output

### Variations Viewer (compiler-variations)

- `NODE_ENV=development` - Enable dev features

## Health Checks

Both services have health checks:

- **API Server:** Checks `/project` endpoint every 10s
- **Variations Viewer:** Checks if dev servers are responsive every 30s

## Troubleshooting

### Variations not starting

The variations service waits for `/tmp/selection/0` to exist. Make sure you've generated templates via the API first.

```bash
# Check if variations were generated
docker exec compiler-api ls -la /tmp/selection/
```

### Port conflicts

If ports are already in use:

```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Map different host port
```

### View logs

```bash
# All services
docker-compose -f compiler/docker-compose.yml logs -f

# Specific service
docker logs -f compiler-api
docker logs -f compiler-variations

# Inside container logs
docker exec compiler-variations tail -f /tmp/variation-*.log
```

### Clean rebuild

```bash
# Remove containers and volumes
docker-compose -f compiler/docker-compose.yml down -v

# Rebuild from scratch
docker-compose -f compiler/docker-compose.yml build --no-cache

# Start fresh
docker-compose -f compiler/docker-compose.yml up
```

## Production Deployment

For production:

1. Remove volume mounts for code (use image versions)
2. Set `NODE_ENV=production`
3. Use proper secrets management for API keys
4. Add reverse proxy (nginx) for SSL/HTTPS
5. Configure resource limits:

```yaml
services:
  compiler-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Build Context Note

**Important:** The Docker build context must be the **repository root**, not the `compiler/` directory. This is because the Dockerfiles need access to `requirements.txt` in the root directory.

```bash
# ✅ Correct - from repo root
cd /path/to/MBZUAI-Hackathon-DreamTeam
docker-compose -f compiler/docker-compose.yml up

# ❌ Wrong - from compiler directory
cd /path/to/MBZUAI-Hackathon-DreamTeam/compiler
docker-compose up  # Will fail - can't find requirements.txt
```

The `docker-compose.yml` already has `context: ..` configured to build from the parent directory.

## API Endpoints

When services are running:

- `GET http://localhost:8000/project` - Get project info
- `POST http://localhost:8000/generate-template-variations` - Generate 4 variations
- `POST http://localhost:8000/select-template-variation` - Select a variation
- `GET http://localhost:8000/active-project` - Get active project status

See `docs/CONTAINER_INTEGRATION.md` for full API documentation.

## Summary

```bash
# One-command startup (from repo root)
docker-compose -f compiler/docker-compose.yml up --build

# Generate templates
curl -X POST http://localhost:8000/generate-template-variations -H 'Content-Type: application/json' -d '{...}'

# View variations
open http://localhost:5173  # Professional
open http://localhost:5174  # Dark
open http://localhost:5175  # Minimal
open http://localhost:5176  # Energetic

# Select and edit
curl -X POST http://localhost:8000/select-template-variation -d '{"variation_index": 1}'
open http://localhost:5177  # Active/editable ⭐
```
