# Docker Architecture Diagram

## Complete System Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│                           DOCKER HOST SYSTEM                                │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                      CONTAINER 1: compiler-api                       │ │
│  │                                                                      │ │
│  │  ┌────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Python FastAPI Server (Port 8000)                             │ │ │
│  │  │  - run_server.py                                               │ │ │
│  │  │  - Handles REST API requests                                   │ │ │
│  │  │  - Template generation logic                                   │ │ │
│  │  └────────────────────────────────────────────────────────────────┘ │ │
│  │                              │                                       │ │
│  │                              │ writes to                             │ │
│  │                              ↓                                       │ │
│  │  ┌────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Volume Mounts                                                 │ │ │
│  │  │  /tmp/selection/  → Docker Volume: template-variations       │ │ │
│  │  │  /tmp/active/     → Docker Volume: active-project            │ │ │
│  │  └────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              ║                                             │
│                              ║ Shared Volumes                              │
│                              ║ (Docker manages persistence)                │
│                              ║                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                  CONTAINER 2: compiler-variations                    │ │
│  │                                                                      │ │
│  │  ┌────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Volume Mounts (Read-Only Access)                             │ │ │
│  │  │  /tmp/selection/  → Docker Volume: template-variations       │ │ │
│  │  │  /tmp/active/     → Docker Volume: active-project            │ │ │
│  │  └────────────────────────────────────────────────────────────────┘ │ │
│  │                              │                                       │ │
│  │                              │ reads from                             │ │
│  │                              ↓                                       │ │
│  │  ┌────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Vite Dev Servers (run_variations.sh)                         │ │ │
│  │  │                                                                │ │ │
│  │  │  Port 5173: /tmp/selection/0 (Professional)                  │ │ │
│  │  │  Port 5174: /tmp/selection/1 (Dark)                          │ │ │
│  │  │  Port 5175: /tmp/selection/2 (Minimal)                       │ │ │
│  │  │  Port 5176: /tmp/selection/3 (Energetic)                     │ │ │
│  │  │  Port 5177: /tmp/active      (Selected/Editable)             │ │ │
│  │  └────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              │                                             │
│                              │ exposes to                                  │
│                              ↓                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                        HOST PORT MAPPING                             │ │
│  │                                                                      │ │
│  │  localhost:8000  → Container 1 Port 8000  (API Server)              │ │
│  │  localhost:5173  → Container 2 Port 5173  (Variation 0)             │ │
│  │  localhost:5174  → Container 2 Port 5174  (Variation 1)             │ │
│  │  localhost:5175  → Container 2 Port 5175  (Variation 2)             │ │
│  │  localhost:5176  → Container 2 Port 5176  (Variation 3)             │ │
│  │  localhost:5177  → Container 2 Port 5177  (Active Project)          │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Template Generation Flow

```
User/Client
    │
    │ HTTP POST /generate-template-variations
    ↓
compiler-api:8000
    │
    │ Generates 4 variations
    ↓
Writes to Docker Volumes:
    - /tmp/selection/0/  (Professional + Modern)
    - /tmp/selection/1/  (Dark + Tech)
    - /tmp/selection/2/  (Minimal + Elegant)
    - /tmp/selection/3/  (Energetic + Playful)
    │
    │ Volumes persist
    ↓
compiler-variations reads from volumes
    │
    │ Starts 4 dev servers
    ↓
Available at:
    - http://localhost:5173
    - http://localhost:5174
    - http://localhost:5175
    - http://localhost:5176
```

### 2. Template Selection Flow

```
User/Client
    │
    │ HTTP POST /select-template-variation {"variation_index": 1}
    ↓
compiler-api:8000
    │
    │ Copies /tmp/selection/1/ to /tmp/active/
    ↓
Writes to Docker Volume:
    - /tmp/active/  (Copy of selected variation)
    │
    │ Volume persists
    ↓
compiler-variations reads from volume
    │
    │ Starts/updates dev server
    ↓
Available at:
    - http://localhost:5177 (Active/Editable)
```

## Volume Details

### template-variations Volume

```
template-variations (Docker Volume)
    └── /tmp/selection/
        ├── 0/                    # Variation 0: Professional + Modern
        │   ├── package.json
        │   ├── vite.config.js
        │   ├── index.html
        │   ├── project.json
        │   └── src/
        │       ├── App.vue
        │       ├── main.js
        │       ├── router/
        │       └── views/
        │           ├── Home.vue
        │           ├── Features.vue
        │           ├── Specs.vue
        │           └── Gallery.vue
        │
        ├── 1/                    # Variation 1: Dark + Tech
        │   └── (same structure)
        │
        ├── 2/                    # Variation 2: Minimal + Elegant
        │   └── (same structure)
        │
        └── 3/                    # Variation 3: Energetic + Playful
            └── (same structure)
```

### active-project Volume

```
active-project (Docker Volume)
    └── /tmp/active/
        ├── package.json
        ├── vite.config.js
        ├── index.html
        ├── project.json
        └── src/
            ├── App.vue
            ├── main.js
            ├── router/
            └── views/
                ├── Home.vue
                ├── Features.vue
                ├── Specs.vue
                └── Gallery.vue
```

## Container Details

### compiler-api Container

**Base Image:** `node:20-slim` + Python 3  
**Working Directory:** `/app/compiler/`  
**Entry Point:** `/app/start.sh` → `python3 run_server.py`  
**Exposed Ports:** 8000, 5173-5177 (for potential manual runs)  
**Health Check:** `curl -f http://localhost:8000/project`

**Environment:**
- `PYTHONUNBUFFERED=1`
- `HOST=0.0.0.0`
- `PORT=8000`

**Volume Mounts:**
```yaml
/tmp/selection → template-variations (read-write)
/tmp/active    → active-project (read-write)
./server       → /app/compiler/server (dev mode)
./manifests    → /app/compiler/manifests (dev mode)
./templates    → /app/compiler/server/templates (dev mode)
```

### compiler-variations Container

**Base Image:** `node:20-slim`  
**Working Directory:** `/app/compiler/`  
**Entry Point:** Custom bash command → `run_variations.sh`  
**Exposed Ports:** 5173, 5174, 5175, 5176, 5177  
**Health Check:** `curl -f http://localhost:5173 || curl -f http://localhost:5174`

**Environment:**
- `NODE_ENV=development`

**Volume Mounts:**
```yaml
/tmp/selection → template-variations (read-only)
/tmp/active    → active-project (read-only)
```

**Startup Logic:**
```bash
1. Wait for /tmp/selection/0 to exist
2. For each variation 0-3:
   - cd /tmp/selection/$i
   - npm install
   - npm run dev -- --port 517$((3+i)) &
3. If /tmp/active exists:
   - cd /tmp/active
   - npm install
   - npm run dev -- --port 5177 &
4. Keep running
```

## Network Communication

```
┌─────────────────────────────────────────────────┐
│  compiler-network (Docker Bridge Network)       │
│                                                 │
│  ┌──────────────────┐      ┌─────────────────┐ │
│  │  compiler-api    │      │  compiler-      │ │
│  │  (API Server)    │      │  variations     │ │
│  │                  │      │  (Dev Servers)  │ │
│  │  Internal: API   │      │  Internal: N/A  │ │
│  │  External: 8000  │      │  External:      │ │
│  │                  │      │    5173-5177    │ │
│  └──────────────────┘      └─────────────────┘ │
│           │                        │            │
│           └────────────────────────┘            │
│              Shared Volumes                     │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Service Dependencies

```
docker-compose up
    │
    ├─→ Build compiler-api image
    │       │
    │       └─→ Start compiler-api container
    │               │
    │               └─→ Health check (wait for /project to respond)
    │                       │
    │                       └─→ HEALTHY
    │
    └─→ Build compiler-variations image
            │
            └─→ Wait for compiler-api to be HEALTHY
                    │
                    └─→ Start compiler-variations container
                            │
                            └─→ Wait for /tmp/selection/0
                                    │
                                    └─→ Start dev servers
```

## File System View

### Inside compiler-api Container

```
/app/
└── compiler/
    ├── manifests/
    │   ├── Text.manifest.json
    │   ├── Button.manifest.json
    │   └── ...
    ├── server/
    │   ├── run_server.py
    │   ├── config.py
    │   ├── src/
    │   │   ├── server.py
    │   │   ├── vue_generator.py
    │   │   └── project_generator.py
    │   └── templates/
    │       ├── product_showcase.py
    │       ├── portfolio.py
    │       └── ...
    └── ...

/tmp/
├── selection/    (Docker volume)
│   ├── 0/
│   ├── 1/
│   ├── 2/
│   └── 3/
└── active/       (Docker volume)
```

### Inside compiler-variations Container

```
/app/
└── compiler/
    └── server/
        ├── run_variations.sh
        └── stop_variations.sh

/tmp/
├── selection/    (Docker volume - same as api)
│   ├── 0/
│   ├── 1/
│   ├── 2/
│   └── 3/
└── active/       (Docker volume - same as api)
```

## Lifecycle

### Startup Sequence

1. `docker-compose up`
2. Build images (if not cached)
3. Create volumes if they don't exist
4. Start `compiler-api` container
5. API server starts on port 8000
6. Health check begins (every 10s)
7. Once healthy, start `compiler-variations` container
8. Variations container waits for `/tmp/selection/0`
9. User generates templates via API
10. Templates written to `/tmp/selection/`
11. Variations container detects files and starts dev servers
12. All 4 variations available on ports 5173-5176
13. User selects a variation
14. Selected variation copied to `/tmp/active/`
15. Active project available on port 5177

### Shutdown Sequence

1. `docker-compose down`
2. Send SIGTERM to containers
3. Containers gracefully stop
4. Volumes persist (unless `-v` flag used)
5. Network removed
6. Containers removed

### Data Persistence

- **Volumes persist** after `docker-compose down`
- **Use `down -v`** to remove volumes
- **Restart keeps data** - Templates remain available
- **Upgrade safe** - New containers use existing volumes

## Summary

This Docker setup provides:

✅ **Isolation** - Services run in separate containers  
✅ **Persistence** - Docker volumes survive restarts  
✅ **Scalability** - Easy to add more services  
✅ **Portability** - Works anywhere Docker runs  
✅ **Development** - Hot reload with volume mounts  
✅ **Production** - Remove dev mounts for deployment  
