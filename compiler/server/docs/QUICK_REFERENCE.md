# Quick Reference Guide

## Starting the Server

```bash
cd compiler/server
python run_server.py
```

Server runs on: `http://localhost:8000`

---

## Programmatic Website Creation

### Option 1: API Client (Recommended)

```bash
cd compiler/server
python test_api_client.py
```

Choose option 1 to create a complete sample website.

### Option 2: Direct Generator

```bash
cd compiler/server
python -c "from src.project_generator import ProjectGenerator; ProjectGenerator().generate_project()"
```

---

## Key Commands

### Clean generated files
```bash
# Clean generated files only (keeps cache)
python clean.py

# Or use the shell script
./clean.sh
```

### Clean everything
```bash
# Clean generated files + cache (start fresh)
python clean.py --all

# Or use the shell script
./clean.sh --all
```

### Clean orphaned input files
```bash
# Remove AST files not in project.json (like old landing.json)
python clean.py --inputs

# Or use the shell script
./clean.sh --inputs
```

### Check what will be regenerated
```bash
python -c "
from src.project_generator import ProjectGenerator
pg = ProjectGenerator()
project_changed, pages_list_changed, changed_pages, all_pages = pg._detect_changes()
print(f'Project changed: {project_changed}')
print(f'Pages list changed: {pages_list_changed}')
print(f'Changed pages: {changed_pages}')
"
```

### Force full rebuild
```bash
python clean.py --cache-only  # Clear cache
python -c "from src.project_generator import ProjectGenerator; ProjectGenerator().generate_project()"
```

---

## API Endpoints

### GET /project
Returns the current project configuration.

```bash
curl http://localhost:8000/project
```

### PATCH /project
Apply JSON patches to project.json

```bash
curl -X PATCH http://localhost:8000/project \
  -H "Content-Type: application/json" \
  -d '[{"op": "replace", "path": "/projectName", "value": "new-name"}]'
```

### GET /ast/{page_name}
Returns the AST for a specific page.

```bash
curl http://localhost:8000/ast/home
```

### PATCH /ast/{page_name}
Apply JSON patches to a page AST.

```bash
curl -X PATCH http://localhost:8000/ast/home \
  -H "Content-Type: application/json" \
  -d '[{"op": "add", "path": "/tree/slots/default/-", "value": {...}}]'
```

### POST /clean
Clean generated files, cache, and/or orphaned inputs.

**Query Parameter:** `mode` (optional, default: "all")

**Modes:**
- `all` - Clean generated files + cache
- `files-only` - Clean generated files only (keep cache)
- `cache-only` - Clean cache only (keep generated files)
- `inputs` - Clean orphaned input AST files

```bash
# Clean everything
curl -X POST "http://localhost:8000/clean?mode=all"

# Clean cache only (force rebuild)
curl -X POST "http://localhost:8000/clean?mode=cache-only"

# Clean orphaned input files
curl -X POST "http://localhost:8000/clean?mode=inputs"
```

**Response:**
```json
{
  "status": "success",
  "mode": "cache-only",
  "removed_items": ["cache: .generation_cache.json"],
  "count": 1
}
```

**Note**: All PATCH endpoints automatically trigger project generation!

---

## Configuration

### Enable Shared Navbar

Edit `project.json`:
```json
{
  "sharedComponents": {
    "navbar": {
      "enabled": true,
      "ast": { /* navbar component AST */ }
    }
  }
}
```

### Add a New Page

Via API:
```python
client.patch_project_config([
    {"op": "add", "path": "/pages/-", "value": {
        "name": "Blog",
        "path": "/blog",
        "astFile": "blog.json"
    }}
])
```

Or edit `project.json` manually and add to pages array.

---

## Performance Tips

### Speed up development
- Use incremental generation (automatic with cache)
- Only modify one page at a time
- Don't change `project.json` unless necessary (cascades to all pages)

### When to clear cache
- After pulling from git
- After major refactoring
- If generation seems stuck on old version

### When cache is invalidated automatically
- When `project.json` changes (excluding pages array)
- When any page AST file changes
- Never for static files (vite.config.js, etc.)

---

## Debugging

### Check if cache exists
```bash
ls -lah .generation_cache.json
cat .generation_cache.json | jq '.'
```

### Verify file hashes
```bash
python -c "
import hashlib
file = 'inputs/home-page.json'
with open(file, 'rb') as f:
    print(f'{file}: {hashlib.sha256(f.read()).hexdigest()}')
"
```

### See generated files
```bash
ls -R ../output/my-new-site/src/
```

### Check App.vue for shared navbar
```bash
head -n 20 ../output/my-new-site/src/App.vue
```

---

## Common Workflows

### Create a new multi-page website

1. Start server: `python run_server.py`
2. Run client: `python test_api_client.py`
3. Choose option 1
4. Check output: `ls ../output/my-new-site/`
5. Start dev server: `cd ../output/my-new-site && npm run dev`

### Update one page content

1. Edit `inputs/your-page.json`
2. Run generator (or use API)
3. Only that page regenerates (~0.5s)

### Add a global navbar

1. Edit `project.json`, set `sharedComponents.navbar.enabled: true`
2. Add navbar AST to `sharedComponents.navbar.ast`
3. Run generator
4. All pages regenerate, navbar in App.vue

### Remove shared navbar

1. Edit `project.json`, set `sharedComponents.navbar.enabled: false`
2. Run generator
3. All pages regenerate, navbar removed from App.vue

---

## File Locations

```
compiler/server/
├── .generation_cache.json        # Hash cache (gitignored)
├── project.json                   # Project config + shared components
├── run_server.py                  # FastAPI server entry point
├── test_api_client.py            # API client demo
├── config.py                      # Server configuration
├── inputs/
│   ├── home-page.json            # Page ASTs
│   ├── about-page.json
│   └── ...
├── src/
│   ├── server.py                 # FastAPI routes
│   ├── project_generator.py      # Main generator (with incremental logic)
│   └── vue_generator.py          # Vue code generator
└── ../output/my-new-site/
    ├── src/
    │   ├── App.vue               # Root (contains shared navbar)
    │   ├── views/
    │   │   ├── Home.vue
    │   │   └── ...
    │   └── router/
    │       └── index.js
    └── package.json
```

---

## Dependencies

Install all required packages:
```bash
pip install uvicorn fastapi jsonpatch requests
```

Or use requirements.txt (if exists):
```bash
pip install -r requirements.txt
```

---

## Environment Variables

None required. All configuration is in `config.py`:

- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 8000)
- `OUTPUT_DIR`: Output directory (default: ../output/my-new-site)
- `AST_INPUT_DIR`: Input AST directory (default: inputs/)

---

## Troubleshooting Quick Fixes

### "ModuleNotFoundError: No module named 'uvicorn'"
```bash
pip install uvicorn fastapi
```

### Stale files (old routes, duplicate pages, etc.)
```bash
# Clean everything and start fresh
python clean.py --all

# Then regenerate
python -c "from src.project_generator import ProjectGenerator; ProjectGenerator().generate_project()"
```

### Orphaned input files (landing.json, etc.)
```bash
# Shows orphaned files and prompts to delete
python clean.py --inputs
```

### "No changes detected" but I changed a file
```bash
# Verify change was saved
cat inputs/home-page.json | grep "_test"

# Force rebuild by clearing cache
python clean.py --cache-only
python -c "from src.project_generator import ProjectGenerator; ProjectGenerator().generate_project()"
```

### Shared navbar not appearing
```bash
# Check config
cat project.json | jq '.sharedComponents.navbar.enabled'

# Should print: true

# Check if AST exists
cat project.json | jq '.sharedComponents.navbar.ast' | head -n 5

# Should show component definition

# If still not working, clean and rebuild
python clean.py --all
python -c "from src.project_generator import ProjectGenerator; ProjectGenerator().generate_project()"
```

### Server won't start
```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Or use different port
# Edit config.py: PORT = 8001
```

---

## Next Steps

1. Read IMPLEMENTATION_SUMMARY.md for detailed architecture
2. Try test_api_client.py to see programmatic creation
3. Experiment with shared components in project.json
4. Monitor .generation_cache.json to understand change detection

Happy building! 🚀
