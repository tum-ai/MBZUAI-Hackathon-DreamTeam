# Dynamic Navbar Padding & Clean API Update

## Overview

This update adds two major improvements:
1. **Dynamic navbar padding** - Automatically calculates and applies padding based on actual navbar height
2. **Clean API endpoint** - Programmatic cleaning via REST API

## 1. Dynamic Navbar Padding

### Problem
Previously, the navbar padding was hardcoded to 80px, which caused issues when:
- Navbar content wrapped to multiple lines (stacked vertically)
- Navbar height varied based on content or screen size
- Users needed different navbar heights for different designs

### Solution
The App.vue component now dynamically calculates the navbar height using Vue's Composition API and applies it as padding to the content area.

### Implementation

**Location:** `src/project_generator.py` - `_generate_app_vue()` method

**Generated Code (in App.vue):**
```vue
<template>
  <div data-component-id="navbar" ...>
    <!-- Navbar content -->
  </div>
  <div :style="contentStyle">
    <router-view/>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const navbarHeight = ref(0)
const contentStyle = ref({})

const updateNavbarHeight = () => {
  const navbar = document.querySelector('[data-component-id="navbar"]')
  if (navbar) {
    navbarHeight.value = navbar.offsetHeight
    contentStyle.value = { paddingTop: `${navbarHeight.value}px` }
  }
}

onMounted(() => {
  updateNavbarHeight()
  // Update on window resize in case navbar height changes
  window.addEventListener('resize', updateNavbarHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateNavbarHeight)
})
</script>
```

### How It Works

1. **Reactive References:**
   - `navbarHeight` - Stores the navbar's offsetHeight
   - `contentStyle` - Reactive style object applied to content wrapper

2. **updateNavbarHeight() Function:**
   - Queries the DOM for navbar element using `data-component-id="navbar"`
   - Reads `offsetHeight` (actual rendered height including padding/borders)
   - Updates `contentStyle` with dynamic `paddingTop`

3. **Lifecycle Hooks:**
   - `onMounted` - Calculates height once component is rendered
   - `window.resize` listener - Recalculates on window resize
   - `onUnmounted` - Cleans up event listener

### Benefits

✅ **Automatic adaptation** - Works with any navbar height  
✅ **Responsive** - Updates on window resize  
✅ **No hardcoded values** - Pure dynamic calculation  
✅ **Performance** - Only recalculates on mount and resize  

### When Script is Added

The script section is only added when:
```python
navbar_enabled = shared_components.get('navbar', {}).get('enabled', False)
if navbar_enabled:
    # Add script section
```

If no navbar is present (`enabled: false`), the static `<div>` wrapper is used without the script.

## 2. Clean API Endpoint

### Endpoint Details

**URL:** `POST /clean`  
**Query Parameter:** `mode` (optional, default: "all")

### Modes

| Mode | Description | Removes |
|------|-------------|---------|
| `all` | Clean everything | Generated files + cache |
| `files-only` | Clean generated files only | src/, public/, node_modules/, dist/, package files |
| `cache-only` | Clean cache only | .generation_cache.json |
| `inputs` | Clean orphaned inputs | AST files not in project.json |

### Usage Examples

**cURL:**
```bash
# Clean everything
curl -X POST "http://localhost:8000/clean?mode=all"

# Clean cache only
curl -X POST "http://localhost:8000/clean?mode=cache-only"

# Clean orphaned input files
curl -X POST "http://localhost:8000/clean?mode=inputs"
```

**Python API Client:**
```python
from test_api_client import VueBitsAPIClient

client = VueBitsAPIClient()

# Clean cache only
result = client.clean(mode="cache-only")
print(f"Removed {result['count']} items")

# Clean all
result = client.clean(mode="all")
for item in result['removed_items']:
    print(f"  - {item}")
```

### Response Format

```json
{
  "status": "success",
  "mode": "cache-only",
  "removed_items": [
    "cache: .generation_cache.json"
  ],
  "count": 1
}
```

### Implementation

**Location:** `src/server.py` - `/clean` endpoint

```python
@app.post("/clean", summary="Clean generated files and/or cache")
async def clean_files(mode: str = "all"):
    """Clean generated files, cache, and/or orphaned inputs."""
    import shutil
    removed_items = []
    
    if mode in ["all", "files-only"]:
        # Remove generated files
        items_to_remove = [
            config.OUTPUT_DIR / 'src',
            config.OUTPUT_DIR / 'public',
            config.OUTPUT_DIR / 'node_modules',
            config.OUTPUT_DIR / 'dist',
            config.OUTPUT_DIR / 'package.json',
            config.OUTPUT_DIR / 'vite.config.js',
            config.OUTPUT_DIR / 'index.html',
        ]
        for item in items_to_remove:
            if item.exists():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                removed_items.append(f"{'directory' if item.is_dir() else 'file'}: {item.name}")
    
    if mode in ["all", "cache-only"]:
        # Remove cache file
        if config.GENERATION_CACHE_FILE.exists():
            config.GENERATION_CACHE_FILE.unlink()
            removed_items.append(f"cache: {config.GENERATION_CACHE_FILE.name}")
    
    if mode == "inputs":
        # Remove orphaned input files (AST files not in project.json)
        valid_ast_files = set(...)
        orphaned_files = [f for f in json_files if f.name.lower() not in valid_ast_files]
        for orphaned_file in orphaned_files:
            orphaned_file.unlink()
            removed_items.append(f"orphaned input: {orphaned_file.name}")
    
    return {"status": "success", "mode": mode, "removed_items": removed_items, "count": len(removed_items)}
```

### Updated test_api_client.py

Added `clean()` method to VueBitsAPIClient:

```python
def clean(self, mode: str = "all") -> Dict:
    """Clean generated files, cache, and/or orphaned inputs."""
    response = requests.post(
        f"{self.base_url}/clean",
        params={"mode": mode}
    )
    response.raise_for_status()
    return response.json()
```

Added menu option 4 for clean operations with sub-menu for different modes.

## Testing

### Test Dynamic Padding

1. Start the dev server:
   ```bash
   cd compiler/output/my-new-site
   npm run dev
   ```

2. Open browser to `http://localhost:5173`

3. Open browser DevTools and check the computed padding-top value:
   ```javascript
   // In console
   document.querySelector('[data-component-id="navbar"]').offsetHeight
   // Should match the padding-top of the content wrapper
   ```

4. Resize the browser window - padding should update dynamically

### Test Clean API

1. Start the server:
   ```bash
   cd compiler/server
   python run_server.py
   ```

2. Test with cURL:
   ```bash
   # Test cache-only mode
   curl -X POST "http://localhost:8000/clean?mode=cache-only" | python -m json.tool
   
   # Should return:
   # {
   #   "status": "success",
   #   "mode": "cache-only",
   #   "removed_items": ["cache: .generation_cache.json"],
   #   "count": 1
   # }
   ```

3. Test with API client:
   ```bash
   cd compiler/server
   python test_api_client.py
   # Choose option 4 (Clean)
   # Choose sub-option 2 (cache-only)
   ```

## Version History

- **V23** - Added dynamic navbar padding and clean API endpoint
- **V22** - Added shared components architecture
- **V21** - Added Vue Bits components and animations
- **V20** - Initial component system

## Files Modified

1. **`src/project_generator.py`**
   - Modified `_generate_app_vue()` to add dynamic padding script
   - Added conditional script generation based on navbar_enabled flag

2. **`src/server.py`**
   - Added `/clean` POST endpoint with mode parameter
   - Supports 4 cleaning modes: all, files-only, cache-only, inputs

3. **`test_api_client.py`**
   - Added `clean()` method to VueBitsAPIClient class
   - Added menu option 4 with clean sub-menu
   - Updated menu prompts from "1-4" to "1-5"

## Future Enhancements

Potential improvements:
- **Footer padding** - Similar dynamic padding for footer if enabled
- **Custom selectors** - Allow custom data attributes for navbar selection
- **Transition animations** - Smooth transition when navbar height changes
- **SSR support** - Handle server-side rendering scenarios
- **Clean scheduling** - Automatic cleanup of old cache files
- **Clean webhook** - Notify external systems after cleanup
