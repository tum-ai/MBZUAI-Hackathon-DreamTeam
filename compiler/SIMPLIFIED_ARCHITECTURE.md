# Simplified Template Selection Architecture

**Date**: November 9, 2025  
**Status**: ✅ IMPLEMENTED & WORKING

## Problem
Previous architecture was overly complex:
- Selected template copied from `/tmp/selection/{id}` → `/tmp/active`
- Required npm install on every selection
- Needed restart mechanisms (active_server_controller.sh, trigger_restart.sh)
- Race conditions between multiple scripts managing same directory
- ETXTBSY errors when esbuild binary locked
- Permission issues on restart scripts

## Solution: Direct Editing
Simplified to a stateless, direct-edit model:

### Architecture Changes

1. **No Copying**
   - Templates stay in `/tmp/selection/0`, `/tmp/selection/1`, etc.
   - Each runs on its own port (5173-5176)
   - Vite servers run continuously with hot-reload

2. **Track Selection State**
   - Compiler API tracks `SELECTED_VARIATION_INDEX` (0-3 or None)
   - GET `/selected-variation` returns current selection
   - POST `/select-template-variation` just sets the index

3. **Direct Patch Application**
   - GET/PATCH `/ast/{page_name}` reads/writes to selected variation path
   - Vite hot-reload picks up changes automatically
   - No restart needed!

### Code Changes

#### `compiler/server/src/server.py`
```python
# Track which variation is selected (0-3, or None)
SELECTED_VARIATION_INDEX = None

@app.post("/select-template-variation")
async def select_template_variation(request: TemplateSelectionRequest):
    global SELECTED_VARIATION_INDEX
    SELECTED_VARIATION_INDEX = request.variation_index
    # No copying, no restart - just track the selection!
    return {"port": 5173 + request.variation_index}

@app.get("/ast/{page_name}")
async def get_page_ast(page_name: str):
    if SELECTED_VARIATION_INDEX is not None:
        # Read from /tmp/selection/{index}/src/ast/
        selected_ast_dir = TEMPLATE_SELECTION_DIR / str(SELECTED_VARIATION_INDEX)
        ast_file_path = selected_ast_dir / "src" / "ast" / f"{page_name_lower}.json"
```

#### `llm/editor/editor.py`
```python
def load_current_ast() -> dict:
    # Query compiler for selected variation
    response = client.get(f"{COMPILER_URL}/selected-variation")
    if response.json()["status"] == "selected":
        # Fetch AST from compiler (reads from selected variation)
        ast = client.get(f"{COMPILER_URL}/ast/home").json()
```

#### `compiler/docker-compose.yml`
```yaml
compiler-variations:
  ports:
    - "5173:5173"  # Only 4 ports, no port 5177
    - "5174:5174"
    - "5175:5175"
    - "5176:5176"
  volumes:
    - template-variations:/tmp/selection  # No active-project volume
  command: /app/compiler/server/run_variations.sh  # Simple!
```

### Removed Files/Complexity
- ❌ `/tmp/active` directory (no longer needed)
- ❌ `active_server_controller.sh` (no restart needed)
- ❌ `trigger_restart.sh` (no restart needed)
- ❌ Port 5177 (no 5th server)
- ❌ `.restart-signal` marker files
- ❌ npm install on template selection
- ❌ File copying logic
- ❌ Race condition between controllers

### Benefits

1. **Simplicity**
   - One script manages variations (`run_variations.sh`)
   - No complex lifecycle management
   - No signal files or IPC

2. **Performance**
   - No npm install on selection (instant!)
   - No file copying
   - Vite hot-reload is near-instant

3. **Reliability**
   - No race conditions
   - No ETXTBSY errors
   - No permission issues
   - Fewer moving parts = fewer bugs

4. **Developer Experience**
   - Easy to understand
   - Easy to debug
   - Each variation independent

### How It Works

1. **Template Generation**
   ```
   User requests template generation
   ↓
   Compiler generates 4 variations
   ↓
   Saved to /tmp/selection/0-3
   ↓
   Docker starts Vite for each (ports 5173-5176)
   ```

2. **Template Selection**
   ```
   User selects variation 2
   ↓
   Frontend POSTs to /select-template-variation
   ↓
   Compiler sets SELECTED_VARIATION_INDEX = 2
   ↓
   (No copying, no restart!)
   ```

3. **Editing Selected Template**
   ```
   User makes edit request
   ↓
   LLM Editor generates component
   ↓
   Editor PATCHes /ast/home
   ↓
   Compiler writes to /tmp/selection/2/src/ast/home.json
   ↓
   Compiler regenerates to /tmp/selection/2/
   ↓
   Vite hot-reload picks up changes
   ↓
   Browser refreshes automatically (port 5175)
   ```

### Testing Verification

```bash
# Start services
cd compiler && sudo docker compose up -d

# Verify all variations running
sudo docker compose logs compiler-variations

# Expected: All 4 Vite servers ready
# ✓ Port 5173: Professional
# ✓ Port 5174: Dark
# ✓ Port 5175: Minimal
# ✓ Port 5176: Energetic
```

### API Endpoints

- `GET /selected-variation` - Get current selection info
- `POST /select-template-variation` - Set selection (no side effects!)
- `GET /ast/{page}` - Reads from selected variation if set
- `PATCH /ast/{page}` - Writes to selected variation if set

### Frontend Integration

Frontend already correct:
```jsx
const options = [
  { id: 'A', port: 5173, label: 'Professional' },
  { id: 'B', port: 5174, label: 'Dark' },
  { id: 'C', port: 5175, label: 'Minimal' },
  { id: 'D', port: 5176, label: 'Energetic' }
]
```

After selection, iframe stays on same port (e.g., 5175), edits apply there directly!

## Result

✅ **Clean architecture**: Stateless, predictable, simple  
✅ **Fast**: No restarts, no copying, just hot-reload  
✅ **Reliable**: No race conditions, no permission issues  
✅ **Ready for demo**: All 4 variations running smoothly
