# Docker Setup Summary

## What Was Created

Created a complete Docker setup for the compiler service with two containerized services that share volumes for template generation and preview.

### Files Created

1. **`Dockerfile`** - Main API server image
   - Based on `node:20-slim` with Python 3
   - Installs Python dependencies from `requirements.txt`
   - Copies compiler code to `/app/compiler/`
   - Exposes port 8000 for API
   - Exposes ports 5173-5177 for dev servers
   - Includes startup script that launches API server

2. **`Dockerfile.variations`** - Variations viewer image
   - Lightweight Node-based image
   - Only includes scripts needed to run variations
   - Shares volumes with API server
   - Runs the `run_variations.sh` script

3. **`docker-compose.yml`** - Service orchestration
   - Defines two services: `compiler-api` and `compiler-variations`
   - Creates shared volumes: `template-variations` and `active-project`
   - Maps volumes to `/tmp/selection` and `/tmp/active`
   - Configures health checks
   - Sets up networking between services
   - Handles service dependencies

4. **`DOCKER_README.md`** - Complete documentation
   - Architecture diagrams
   - Quick start guide
   - API endpoint documentation
   - Troubleshooting guide
   - Production deployment notes

5. **`docker-start.sh`** - Convenience wrapper script
   - Commands: up, down, restart, logs, clean, test, select, status
   - Makes Docker operations easier
   - Includes test template generation

6. **`.dockerignore`** (in repo root) - Build optimization
   - Excludes unnecessary files from Docker context
   - Reduces image size
   - Speeds up builds

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Docker Host                                         │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  compiler-api (Container 1)                  │  │
│  │  Port 8000: FastAPI REST API                 │  │
│  │  - Generates 4 template variations           │  │
│  │  - Writes to volumes                         │  │
│  └──────────────────────────────────────────────┘  │
│              ↓                                       │
│    Shared Volumes (Docker Volumes)                  │
│    /tmp/selection (4 variations)                    │
│    /tmp/active (selected variation)                 │
│              ↓                                       │
│  ┌──────────────────────────────────────────────┐  │
│  │  compiler-variations (Container 2)           │  │
│  │  Ports 5173-5177: Vite Dev Servers          │  │
│  │  - Reads from volumes                        │  │
│  │  - Serves 5 live preview websites            │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## How It Works

### 1. Build Context
- Build context is the **repository root** (not `compiler/` dir)
- This allows access to `requirements.txt` in repo root
- `docker-compose.yml` has `context: ..` configured

### 2. Service Startup Flow
1. `compiler-api` starts first
2. Health check waits for API to be ready (checks `/project` endpoint)
3. `compiler-variations` starts after API is healthy
4. Variations service waits for `/tmp/selection/0` to exist
5. Once variations are generated, dev servers start on ports 5173-5177

### 3. Volume Sharing
- **template-variations** volume → `/tmp/selection/`
  - Written by API server (4 variations)
  - Read by variations viewer
  
- **active-project** volume → `/tmp/active/`
  - Written by API server (selected variation)
  - Read by variations viewer for port 5177

### 4. Development Mode
- Code is mounted as volumes for hot reload
- Python server auto-reloads on file changes (uvicorn `--reload`)
- Vue dev servers have HMR enabled

## Usage

### Basic Commands

```bash
# From repo root
cd /path/to/MBZUAI-Hackathon-DreamTeam

# Start everything
./compiler/docker-start.sh up

# Or directly with docker-compose
docker-compose -f compiler/docker-compose.yml up --build
```

### Quick Start Workflow

```bash
# 1. Start services
./compiler/docker-start.sh up

# 2. In another terminal, generate templates
./compiler/docker-start.sh test

# 3. View variations
# Open browser to:
#   http://localhost:5173 (Professional)
#   http://localhost:5174 (Dark)
#   http://localhost:5175 (Minimal)
#   http://localhost:5176 (Energetic)

# 4. Select a variation for editing
./compiler/docker-start.sh select 1

# 5. Edit the active project
# Open browser to: http://localhost:5177
```

### Management Commands

```bash
# View logs
./compiler/docker-start.sh logs

# View specific service logs
./compiler/docker-start.sh logs compiler-api

# Check status
./compiler/docker-start.sh status

# Stop services
./compiler/docker-start.sh down

# Clean everything (containers, volumes, images)
./compiler/docker-start.sh clean

# Restart
./compiler/docker-start.sh restart
```

## Port Mapping

| Host Port | Container Port | Service | Purpose |
|-----------|----------------|---------|---------|
| 8000 | 8000 | API | REST API for template generation |
| 5173 | 5173 | Variations | Variation 0 (Professional palette) |
| 5174 | 5174 | Variations | Variation 1 (Dark palette) |
| 5175 | 5175 | Variations | Variation 2 (Minimal palette) |
| 5176 | 5176 | Variations | Variation 3 (Energetic palette) |
| 5177 | 5177 | Variations | Active project (editable) |

## API Endpoints

Once running, access at `http://localhost:8000`:

- `GET /project` - Get current project info
- `POST /generate-template-variations` - Generate 4 template variations
- `POST /select-template-variation` - Select a variation as active
- `GET /active-project` - Get active project status

## Key Features

1. **Isolated Services** - API and viewer run in separate containers
2. **Shared Volumes** - Data persists between container restarts
3. **Health Checks** - Ensures services start in correct order
4. **Hot Reload** - Changes to code reflect immediately (dev mode)
5. **Port Exposure** - All 6 services accessible from host
6. **Easy Management** - Simple commands via `docker-start.sh`

## Production Notes

For production deployment:

1. Remove development volume mounts (code shouldn't be mounted)
2. Set `NODE_ENV=production`
3. Use environment variables for secrets
4. Add reverse proxy (nginx) for SSL
5. Configure resource limits in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

## Troubleshooting

### Variations not starting
- Ensure templates were generated via API first
- Check: `docker exec compiler-api ls -la /tmp/selection/`

### Port conflicts
- Change port mapping in `docker-compose.yml`
- Example: `"8001:8000"` to use host port 8001

### Build failures
- Ensure building from repo root
- Clean build: `./compiler/docker-start.sh clean && ./compiler/docker-start.sh up`

### View container logs
```bash
docker logs -f compiler-api
docker logs -f compiler-variations
```

## Benefits

✅ **Reproducible** - Same environment everywhere  
✅ **Isolated** - No conflicts with host system  
✅ **Portable** - Works on any system with Docker  
✅ **Scalable** - Easy to add more services  
✅ **Maintainable** - Clear separation of concerns  
✅ **Developer-Friendly** - Hot reload, easy debugging  

## Next Steps

1. Test the setup:
   ```bash
   ./compiler/docker-start.sh up
   ./compiler/docker-start.sh test
   ```

2. Access the services:
   - API: http://localhost:8000
   - Variations: http://localhost:5173-5177

3. Integrate with your workflow:
   - Use the API to generate templates
   - Preview variations in browser
   - Select and edit active project

4. Deploy to production:
   - Push images to Docker registry
   - Deploy with docker-compose or Kubernetes
   - Configure environment variables
   - Set up reverse proxy with SSL

## Files Location

All Docker-related files are in `/compiler/`:
```
compiler/
├── Dockerfile                  # API server image
├── Dockerfile.variations       # Variations viewer image
├── docker-compose.yml          # Service orchestration
├── docker-start.sh             # Convenience wrapper
└── DOCKER_README.md           # Complete documentation
```

Plus `.dockerignore` in repo root for build optimization.
