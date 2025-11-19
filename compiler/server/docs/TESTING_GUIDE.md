# Testing Guide - Two Methods

## The Problem

The `run_patches_from_file.py` script expects a **JSON Patch array** (RFC 6902 format), but `test-enhanced.json` contains a **complete AST object**.

## Solution 1: Use JSON Patches (Server Method)

### Step 1: Start the server
```powershell
cd compiler\server
python run_server.py
```

### Step 2: Run with the patches file
```powershell
# Use the patches version (not the AST version)
python run_patches_from_file.py tests\test-enhanced-patches.json Home
```

**What's the difference?**
- ❌ `test-enhanced.json` - Complete AST: `{ "state": {...}, "tree": {...} }`
- ✅ `test-enhanced-patches.json` - JSON Patch array: `[{ "op": "add", "path": "...", "value": ... }]`

## Solution 2: Use Direct AST Testing (No Server)

This is simpler for testing - no server needed!

### Run the test directly
```powershell
cd compiler\server
python test_ast_directly.py tests\test-enhanced.json Home
```

This script:
1. ✅ Takes a complete AST file (like `test-enhanced.json`)
2. ✅ Creates the project config automatically
3. ✅ Generates the output directly
4. ✅ No server needed

## Solution 3: Use the Existing AST Files

If you just want to test the existing pages:

```powershell
cd compiler\server
python -m src.project_generator
```

This will use the existing `inputs/home.json` and `inputs/contact.json` files.

## Understanding the File Formats

### Format 1: Complete AST File
**File**: `inputs/home.json`, `tests/test-enhanced.json`

```json
{
  "state": {
    "myVar": { "type": "string", "defaultValue": "hello" }
  },
  "tree": {
    "id": "root",
    "type": "Box",
    "props": {},
    "slots": { "default": [] }
  }
}
```

**Used by**:
- ✅ `test_ast_directly.py`
- ✅ `project_generator.py` (reads from `inputs/` folder)
- ❌ `run_patches_from_file.py`

### Format 2: JSON Patch Array
**File**: `tests/test-enhanced-patches.json`

```json
[
  {
    "op": "add",
    "path": "/state/myVar",
    "value": { "type": "string", "defaultValue": "hello" }
  },
  {
    "op": "add",
    "path": "/tree/slots/default/-",
    "value": { "id": "my-component", "type": "Box", ... }
  }
]
```

**Used by**:
- ✅ `run_patches_from_file.py` (requires server running)
- ✅ Server endpoints: `PATCH /project`, `PATCH /ast/{page}`
- ❌ `project_generator.py`

## Quick Commands

### Test the enhanced components (fastest):
```powershell
cd compiler\server
python test_ast_directly.py tests\test-enhanced.json Home
```

### Test with patches (requires server):
```powershell
# Terminal 1 - Start server
cd compiler\server
python run_server.py

# Terminal 2 - Run patches
cd compiler\server
python run_patches_from_file.py tests\test-enhanced-patches.json Home
```

### Test existing pages:
```powershell
cd compiler\server
python -m src.project_generator
```

## View the Results

After generation:
```powershell
cd compiler\output\my-new-site
npm install
npm run dev
```

Then open browser to: http://localhost:5173

## Troubleshooting

### "Module not found" error
```powershell
# Make sure you're in the server directory
cd compiler\server
```

### "Server not responding"
```powershell
# Check if server is running
# Should see: "Server running at http://localhost:8000"
```

### "AST file not found"
```powershell
# Use relative path from server directory
python test_ast_directly.py tests\test-enhanced.json Home

# Or use absolute path
python test_ast_directly.py C:\path\to\test-enhanced.json Home
```

### Generated output has errors
1. Check the console output for Python errors
2. Check the manifest files are loaded correctly
3. Verify the AST structure is valid JSON
4. Look for missing component manifests

## Files Created

- ✅ `test_ast_directly.py` - New helper script (no server needed)
- ✅ `tests/test-enhanced-patches.json` - Patches version of test file
- ✅ `tests/test-enhanced.json` - Complete AST (already existed in inputs/)

## Recommendation

For quick testing, use **Solution 2** (`test_ast_directly.py`):
- No server setup
- Works with complete AST files
- Faster iteration
- Easier debugging

Use `run_patches_from_file.py` when:
- Testing the full LLM workflow
- Testing the server's patch endpoints
- Simulating real LLM output
