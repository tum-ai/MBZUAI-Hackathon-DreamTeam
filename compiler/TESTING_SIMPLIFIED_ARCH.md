# Testing the Simplified Architecture

This document provides steps to test the new simplified template selection flow.

## Prerequisites

All services running:
- ✅ Compiler API (port 8000)
- ✅ Compiler Variations (ports 5173-5176)
- ✅ LLM Server (port 8000)
- ✅ Webapp (port 5178)

## Test Flow

### 1. Generate Template Variations

```bash
# Generate 4 portfolio variations
curl -X POST http://localhost:8000/generate-template-variations \
  -H "Content-Type: application/json" \
  -d '{
    "template_type": "portfolio",
    "variables": {
      "name": "Test Developer",
      "role": "Full Stack Engineer"
    }
  }'
```

**Expected**: 4 variations created in `/tmp/selection/0-3`

Verify variations are accessible:
```bash
curl http://localhost:5173  # Professional
curl http://localhost:5174  # Dark
curl http://localhost:5175  # Minimal
curl http://localhost:5176  # Energetic
```

### 2. Select a Variation

```bash
# Select variation 2 (Minimal)
curl -X POST http://localhost:8000/select-template-variation \
  -H "Content-Type: application/json" \
  -d '{"variation_index": 2}'
```

**Expected Response**:
```json
{
  "status": "success",
  "selected_variation": 2,
  "palette": "minimal",
  "port": 5175,
  "message": "Variation 2 (minimal) selected. Edits will apply directly to port 5175."
}
```

Verify selection:
```bash
curl http://localhost:8000/selected-variation
```

**Expected**:
```json
{
  "status": "selected",
  "selected_variation": 2,
  "port": 5175,
  "palette": "minimal"
}
```

### 3. Test AST Reading

```bash
# Get current AST (should read from selected variation)
curl http://localhost:8000/ast/home | jq '.tree.id'
```

**Expected**: "root" (proves AST was read successfully)

### 4. Test AST Patching (Manual)

```bash
# Apply a simple patch to add a text component
curl -X PATCH http://localhost:8000/ast/home \
  -H "Content-Type: application/json" \
  -d '[
    {
      "op": "add",
      "path": "/tree/slots/default/-",
      "value": {
        "id": "test-text-1",
        "type": "Text",
        "props": {
          "content": "Architecture Simplified!",
          "as": "h2"
        },
        "slots": {}
      }
    }
  ]'
```

**Expected Behavior**:
1. Patch applied to `/tmp/selection/2/src/ast/home.json`
2. Compiler regenerates files in `/tmp/selection/2/`
3. Vite hot-reload picks up changes
4. Browser on `http://localhost:5175` shows new text

**Verify**:
```bash
# Check AST was updated
curl http://localhost:8000/ast/home | jq '.tree.slots.default | length'
# Should be incremented by 1
```

### 5. Test LLM Editor Integration

Start Python shell:
```python
import httpx

# Plan a UI change
response = httpx.post("http://localhost:8000/plan", json={
    "request": "Add a contact form with name and email fields"
})
print(response.json())
```

**Expected**:
1. Planner routes to Editor
2. Editor queries `/selected-variation` (gets variation 2)
3. Editor generates component
4. Editor PATCHes `/ast/home` with new component
5. Compiler writes to `/tmp/selection/2/`
6. Vite hot-reload updates `http://localhost:5175`

### 6. Test Multiple Selection Changes

```bash
# Select different variation
curl -X POST http://localhost:8000/select-template-variation \
  -H "Content-Type: application/json" \
  -d '{"variation_index": 0}'

# Verify selection changed
curl http://localhost:8000/selected-variation | jq '.selected_variation'
# Expected: 0

# Future edits now apply to variation 0 (port 5173)
```

## Success Criteria

- ✅ All 4 variations accessible on ports 5173-5176
- ✅ Selection changes instantly (no npm install delay)
- ✅ AST reads from correct variation
- ✅ Patches apply to correct variation
- ✅ Vite hot-reload picks up changes automatically
- ✅ No restart errors in Docker logs
- ✅ No ETXTBSY or permission errors
- ✅ Editor can query and patch selected variation

## Debugging

Check Docker logs:
```bash
# Variations
sudo docker compose logs -f compiler-variations

# API
sudo docker compose logs -f compiler-api
```

Check if Vite servers are running:
```bash
sudo docker exec -it compiler-variations ps aux | grep vite
# Should show 4 Vite processes
```

Check variation files:
```bash
sudo docker exec -it compiler-variations ls -la /tmp/selection/
# Should show directories 0, 1, 2, 3

sudo docker exec -it compiler-variations ls -la /tmp/selection/2/src/ast/
# Should show home.json
```

## Performance Comparison

**Old Architecture** (with /tmp/active):
- Template selection: ~10-15 seconds (copy + npm install)
- Risk of race conditions, ETXTBSY errors
- Complex restart logic

**New Architecture** (direct editing):
- Template selection: ~50ms (just set a variable!)
- No race conditions possible
- Simple, predictable behavior

## Next Steps

After verifying this works:
1. Test frontend template selection UI
2. Test voice commands → LLM → Editor → Compiler flow
3. Run end-to-end demo (Sprint 5)
